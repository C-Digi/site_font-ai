import os
import torch
import numpy as np
from PIL import Image
from transformers import AutoProcessor, AutoModel
from qwen_vl_utils import process_vision_info
from typing import List, Dict, Union, Optional

class Qwen3VLEmbedder:
    def __init__(self, model_name: str = "Qwen/Qwen3-VL-Embedding-8B", device_map: str = "auto", torch_dtype: torch.dtype = torch.float16):
        print(f"Loading model {model_name}...")
        self.processor = AutoProcessor.from_pretrained(model_name, trust_remote_code=True)
        # We use AutoModel for embedding models; if it's a specific class like Qwen2_5_VLEmbedding, 
        # transformers should pick it up via trust_remote_code or standard mapping.
        self.model = AutoModel.from_pretrained(
            model_name,
            trust_remote_code=True,
            torch_dtype=torch_dtype,
            device_map=device_map
        ).eval()
        self.device = self.model.device
        print(f"Model loaded on {self.device}")

    def embed_items(self, items: List[Dict[str, str]], normalize: bool = True) -> np.ndarray:
        """
        Embeds a list of items.
        Each item can be:
        - {"text": "..."}
        - {"image": "path/to/image"}
        - {"text": "...", "image": "path/to/image"}
        """
        embeddings = []
        
        for item in items:
            messages = []
            content = []
            
            if "image" in item:
                # Support local paths
                image_path = item["image"]
                if not image_path.startswith("file://") and not image_path.startswith("http"):
                    image_path = f"file://{os.path.abspath(image_path)}"
                content.append({"type": "image", "image": image_path})
            
            if "text" in item:
                content.append({"type": "text", "text": item["text"]})
            
            messages.append({"role": "user", "content": content})
            
            # Preprocess
            text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            image_inputs, video_inputs = process_vision_info(messages)
            
            inputs = self.processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt"
            )
            inputs = inputs.to(self.device)

            with torch.no_grad():
                # For embedding models, the forward pass usually returns the pooled output 
                # or we take the last hidden state of the [CLS]/EOS token.
                # Qwen3-VL-Embedding is expected to return the embedding in the model output.
                outputs = self.model(**inputs)
                
                # If it's a standard transformer, we might need to extract the correct token.
                # But for a dedicated embedding model, it likely has a 'pooler_output' or similar.
                if hasattr(outputs, "pooler_output") and outputs.pooler_output is not None:
                    emb = outputs.pooler_output
                elif hasattr(outputs, "last_hidden_state"):
                    # Fallback to mean pooling or last token if not explicitly an embedding model
                    # (Though the user specified an embedding model)
                    emb = outputs.last_hidden_state[:, -1, :] 
                else:
                    # Some models return the embedding directly as the first element
                    emb = outputs[0]
                    if len(emb.shape) == 3: # (batch, seq, dim)
                        emb = emb[:, -1, :]
                
                emb = emb.cpu().float().numpy()
                
                if normalize:
                    norm = np.linalg.norm(emb, axis=1, keepdims=True)
                    emb = emb / norm
                
                embeddings.append(emb)

        return np.vstack(embeddings)

def smoke_test():
    """
    Runs a minimal smoke test for the embedder.
    """
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="Qwen/Qwen3-VL-Embedding-8B")
    parser.add_argument("--image", help="Path to a local PNG for testing")
    args = parser.parse_args()

    # Create dummy image if none provided
    test_image_path = args.image
    if not test_image_path:
        test_image_path = "smoke_test_glyph.png"
        img = Image.new('RGB', (224, 224), color = (255, 255, 255))
        img.save(test_image_path)
        print(f"Created dummy image: {test_image_path}")

    try:
        embedder = Qwen3VLEmbedder(model_name=args.model)
        
        items = [
            {"text": "heavy display font"},
            {"text": "heavy display font"}, # Cosine(text, text) should be ~1.0
            {"image": test_image_path},
            {"text": "heavy display font", "image": test_image_path}
        ]
        
        print(f"Embedding {len(items)} items...")
        embs = embedder.embed_items(items)
        
        print(f"Embedding dimension: {embs.shape[1]}")
        
        def cosine_sim(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

        print(f"cosine(text, text): {cosine_sim(embs[0], embs[1]):.4f}")
        print(f"cosine(text, image): {cosine_sim(embs[0], embs[2]):.4f}")
        print(f"cosine(mixed, mixed): {cosine_sim(embs[3], embs[3]):.4f}")

    finally:
        # Cleanup dummy image
        if not args.image and os.path.exists("smoke_test_glyph.png"):
            os.remove("smoke_test_glyph.png")

if __name__ == "__main__":
    smoke_test()

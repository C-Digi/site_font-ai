import os
import json
import base64
import requests
from pathlib import Path
from dotenv import load_dotenv

def load_env():
    root = Path(__file__).resolve().parents[3]
    load_dotenv(root / ".env", override=False)
    load_dotenv(root / ".env.local", override=False)

def image_to_base64(image_path: Path) -> str:
    if not image_path.exists():
        return ""
    return base64.b64encode(image_path.read_bytes()).decode("utf-8")

def check_multimodal(model_id: str):
    load_env()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("OPENROUTER_API_KEY not found")
        return

    image_path = Path("research/ab-eval/out/specimens_v3/Actor_bottom.png")
    if not image_path.exists():
        print(f"Image not found: {image_path}")
        return

    b64_image = image_to_base64(image_path)
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model_id,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What is in this image? Describe it briefly."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{b64_image}"
                        }
                    }
                ]
            }
        ]
    }
    
    print(f"Checking multimodal capability for {model_id}...")
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            print(f"SUCCESS: Response from {model_id}:")
            print(content)
            return True
        else:
            print(f"FAILED: Status code {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    import sys
    model = sys.argv[1] if len(sys.argv) > 1 else "openrouter/pony-alpha"
    check_multimodal(model)

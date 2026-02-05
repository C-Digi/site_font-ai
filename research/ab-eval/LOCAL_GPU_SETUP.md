# Local GPU Setup for Qwen3-VL Embedding

This document describes how to set up a local workstation for generating Qwen3-VL embeddings.

## Hardware Specification
- **GPUs**: 2× NVIDIA GeForce RTX 3090 (24GB VRAM each)
- **Interconnect**: NVLink Bridge (Optional but recommended for Tensor Parallelism)

## Environment Setup

### Operating System
- **Recommended**: Ubuntu 22.04 LTS or WSL2 (Windows Subsystem for Linux).
- **Windows Native**: Not recommended due to complexities with `flash-attn` and certain CUDA kernels.

### Prerequisites
- **CUDA Toolkit**: 12.1 or 12.4
- **Python**: 3.10+
- **NVIDIA Drivers**: 535+

### Installation Steps

1. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/WSL2
   ```

2. **Install PyTorch**:
   ```bash
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r research/ab-eval/py/requirements.txt
   ```

4. **Flash Attention (Required for VL Performance)**:
   ```bash
   pip install flash-attn --no-build-isolation
   ```

## Model Configuration

### Precision (dtype)
- **Recommended**: `float16` for RTX 3090.
- While 3090 supports `bfloat16`, `float16` is often better optimized for inference on Ampere consumer cards unless the model was specifically trained to require BF16 for stability.

### Multi-GPU Usage
The provided `embed_qwen3_vl.py` uses `device_map="auto"` via the `accelerate` library. 
- If the model (approx 16GB in FP16) fits on a single GPU, it will likely stay there.
- If you want to force sharding across 2 GPUs to save VRAM for larger context/images, `device_map="balanced"` or `"auto"` will handle it automatically.
- **vLLM Note**: If using the vLLM backend (experimental), use `--tensor-parallel-size 2` to utilize both GPUs via NVLink.

## Usage & Validation

### Smoke Test
Run the following command to verify the installation and model loading:
```bash
python research/ab-eval/py/embed_qwen3_vl.py --model Qwen/Qwen3-VL-Embedding-8B
```

### Expected Output
- Embedding dimension: 4096
- `cosine(text, text)`: ~1.0000
- `cosine(text, image)`: (variable, usually 0.2 - 0.5 depending on alignment)
- `cosine(mixed, mixed)`: 1.0000

## Troubleshooting

- **Out of Memory (OOM)**:
  - Reduce `max_pixels` in the processor configuration if images are too large.
  - Ensure no other processes are using VRAM (`nvidia-smi`).
- **Flash Attention Errors**:
  - Ensure `ninja` is installed (`pip install ninja`) for faster compilation.
  - Check that your CUDA version matches the one PyTorch was built with.
- **vLLM Mismatch**:
  - As noted in `DECISIONS.md`, vLLM may produce slightly different embeddings due to preprocessing differences. Use the `transformers` backend for the most "correct" embeddings matching the official implementation.

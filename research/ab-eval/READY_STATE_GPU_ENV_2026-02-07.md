# A/B Eval Environment Readiness Report (GPU + Env)

Date (UTC): 2026-02-07
Scope: Environment readiness only for VL/text embedding runs used by `research/ab-eval/py/*.py`.

## Root Cause(s)

- Root cause 1: The default Python interpreters on PATH were using CPU-only PyTorch (`torch 2.10.0+cpu`), so CUDA was unavailable despite healthy NVIDIA driver/GPU visibility.
- Root cause 2: Runtime dependency alignment for VL execution was not isolated to a CUDA-enabled interpreter intended for eval runs.
- Root cause 3 (minor): Text embedding script had soft-fail behavior when `OPENROUTER_API_KEY` was missing (printed and returned), which can hide CI/operator failures.

## Exact Commands Run

1) Driver/GPU and interpreter discovery
- `powershell -NoProfile -Command "Write-Host '=== nvidia-smi ==='; nvidia-smi; Write-Host '=== where python ==='; where.exe python; Write-Host '=== py launcher envs ==='; py -0p"`

2) Torch diagnostics on default Python
- `python -c "import torch,sys; print('PYTHON_EXE',sys.executable); print('PYTHON_VER',sys.version.replace('\\n',' ')); print('TORCH_VERSION',torch.__version__); print('TORCH_CUDA_BUILD',torch.version.cuda); print('TORCH_CUDA_AVAILABLE',torch.cuda.is_available()); print('TORCH_CUDA_DEVICE_COUNT',torch.cuda.device_count()); print('TORCH_CUDA_DEVICE_0',torch.cuda.get_device_name(0) if torch.cuda.is_available() and torch.cuda.device_count()>0 else 'N/A')"`
- `python -m pip show torch torchvision transformers qwen-vl-utils accelerate sentencepiece`

3) Python 3.12 checks (pre-fix)
- `py -3.12 -c "import sys,importlib.util; print('PYTHON_EXE',sys.executable); print('PYTHON_VER',sys.version.replace('\\n',' ')); print('TORCH_PRESENT', bool(importlib.util.find_spec('torch')) )"`
- `py -3.12 -c "import sys,torch; print('PYTHON_EXE',sys.executable); print('PYTHON_VER',sys.version.replace('\\n',' ')); print('TORCH_VERSION',torch.__version__); print('TORCH_CUDA_BUILD',torch.version.cuda); print('TORCH_CUDA_AVAILABLE',torch.cuda.is_available()); print('TORCH_CUDA_DEVICE_COUNT',torch.cuda.device_count()); print('TORCH_CUDA_DEVICE_0',torch.cuda.get_device_name(0) if torch.cuda.is_available() and torch.cuda.device_count()>0 else 'N/A')"`

4) Minimal safe local fix (isolated CUDA-ready eval venv)
- `powershell -NoProfile -Command "py -3.12 -m venv .venv-ab-eval; .\\.venv-ab-eval\\Scripts\\python -m pip install --upgrade pip; .\\.venv-ab-eval\\Scripts\\python -m pip install --index-url https://download.pytorch.org/whl/cu124 torch torchvision; .\\.venv-ab-eval\\Scripts\\python -m pip install -r research/ab-eval/py/requirements-vl.txt; .\\.venv-ab-eval\\Scripts\\python -m pip install -r research/ab-eval/py/requirements-text.txt"`

5) Torch diagnostics on the actual eval interpreter
- `.\\.venv-ab-eval\\Scripts\\python -c "import sys,torch; print('PYTHON_EXE',sys.executable); print('PYTHON_VER',sys.version.replace('\\n',' ')); print('TORCH_VERSION',torch.__version__); print('TORCH_CUDA_BUILD',torch.version.cuda); print('TORCH_CUDA_AVAILABLE',torch.cuda.is_available()); print('TORCH_CUDA_DEVICE_COUNT',torch.cuda.device_count()); print('TORCH_CUDA_DEVICE_0',torch.cuda.get_device_name(0) if torch.cuda.is_available() and torch.cuda.device_count()>0 else 'N/A')"`

6) Transformers/qwen-vl-utils compatibility sanity
- `.\\.venv-ab-eval\\Scripts\\python -c "import transformers,qwen_vl_utils,accelerate,sentencepiece; print('TRANSFORMERS_VERSION',transformers.__version__); print('QWEN_VL_UTILS_VERSION',getattr(qwen_vl_utils,'__version__','unknown')); print('ACCELERATE_VERSION',accelerate.__version__); print('SENTENCEPIECE_VERSION',getattr(sentencepiece,'__version__','unknown'))"`
- `.\\.venv-ab-eval\\Scripts\\python -c "import sys; sys.path.insert(0, 'research/ab-eval/py'); import embed_qwen3_vl; print('EMBED_QWEN3_VL_IMPORT_OK'); from transformers import AutoConfig; cfg = AutoConfig.from_pretrained('Qwen/Qwen3-VL-Embedding-8B', trust_remote_code=True); print('HF_MODEL_CONFIG_OK', cfg.__class__.__name__)"`

7) Env var presence check (without printing values)
- `powershell -NoProfile -Command "$vars = 'OPENROUTER_API_KEY','VL_EMBEDDING_ENDPOINT','VL_EMBEDDING_API_KEY','HUGGINGFACE_HUB_TOKEN','HF_TOKEN','HF_HOME'; foreach ($v in $vars) { if ([string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable($v,'Process'))) { Write-Output \"$v PROCESS=MISSING\" } else { Write-Output \"$v PROCESS=PRESENT\" } }; if (Test-Path '.env.local') { Write-Output '.env.local FILE=PRESENT'; $envText = Get-Content '.env.local' -Raw; foreach ($v in $vars) { if ($envText -match \"(?m)^$v=.+$\") { Write-Output \"$v DOTENV=PRESENT\" } else { Write-Output \"$v DOTENV=MISSING\" } } } else { Write-Output '.env.local FILE=MISSING'; foreach ($v in $vars) { Write-Output \"$v DOTENV=MISSING\" } }"`

## Evidence Snapshot

- `nvidia-smi`: driver visible, GPUs visible (2x RTX 3090 Ti), CUDA runtime reported by driver as 13.1.
- Default python (`Python314` / `Python312`) had CPU-only torch (`+cpu`), `torch.cuda.is_available() == False`.
- Eval venv python (`.venv-ab-eval`) now has CUDA torch (`2.6.0+cu124`), `torch.cuda.is_available() == True`, device_count = 2.
- Qwen VL stack import sanity passed (`transformers`, `qwen-vl-utils`, `accelerate`, `sentencepiece`) and model config load passed.

## Required Env Var Checklist (PRESENT/MISSING only)

- OPENROUTER_API_KEY: PRESENT in `.env.local`; MISSING in current process env (acceptable because script loads `.env.local`).
- VL_EMBEDDING_ENDPOINT: MISSING (not required by the local Python VL eval scripts in `research/ab-eval/py`, used by app/server TS path).
- VL_EMBEDDING_API_KEY: MISSING (same note as above).
- HUGGINGFACE_HUB_TOKEN: MISSING.
- HF_TOKEN: MISSING.
- HF_HOME: MISSING.

Interpretation for this scope:
- Text eval path requires `OPENROUTER_API_KEY` -> PRESENT via `.env.local`.
- Local VL eval path does not require `VL_EMBEDDING_ENDPOINT`/`VL_EMBEDDING_API_KEY`.
- `HF_TOKEN`/`HUGGINGFACE_HUB_TOKEN` are optional unless the model/access policy requires auth or rate limits force authenticated pulls.

## Minimal Code Changes Applied

- `research/ab-eval/py/embed_openrouter_text.py`
  - Added `import sys`.
  - Changed missing-key behavior from soft return to explicit non-zero exit (`sys.exit(2)`) with clearer error text.

## Exact Files Changed

- `research/ab-eval/py/embed_openrouter_text.py`
- `research/ab-eval/READY_STATE_GPU_ENV_2026-02-07.md`

## Final Readiness Verdict

READY

Conditions for READY in this report:
- CUDA-enabled PyTorch is now available in the intended eval interpreter (`.venv-ab-eval\Scripts\python`).
- NVIDIA driver/GPU visibility is confirmed.
- Required env var for text path (`OPENROUTER_API_KEY`) is present in `.env.local`.
- VL dependency/import sanity checks passed for the local Python embedding path.

## Operator-Only Actions Still Required

- Use the eval interpreter explicitly for all A/B eval Python runs:
  - `.\.venv-ab-eval\Scripts\python research/ab-eval/py/run_all.py --dataset complex --variant all`
- If Hugging Face auth/rate-limit errors occur during model pull, set either `HF_TOKEN` or `HUGGINGFACE_HUB_TOKEN` in the session (or `.env.local`) and reopen terminal/session before rerun.

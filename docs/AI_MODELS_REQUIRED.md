# AI Models Required for Cerebrum

This document details the AI models that are necessary for the full functionality of the Cerebrum AI-driven art platform.

## Overview

Cerebrum uses AI models primarily for perception and style analysis, not for generating final artwork. The models serve to analyze canvas state, detect anatomical structure, and suggest artistic styles. The actual drawing is performed by the Motor System using deliberate, traceable strokes.

## Required Models (Already Integrated)

### 1. MediaPipe Models

**Purpose**: Pose, face, and hand landmark detection for anatomical analysis

**Components Used**:
- **Pose Landmarker**: 33-point body pose detection
- **Face Landmarker**: 468 facial landmark detection  
- **Hand Landmarker**: 21 landmarks per hand with handedness classification

**Installation**:
```bash
pip install mediapipe>=0.10.0
```

**Models Downloaded Automatically**:
- `pose_landmarker_lite.task` - Lightweight pose detection model
- `pose_landmarker_full.task` - Full pose detection model
- `pose_landmarker_heavy.task` - Heavy pose detection model (most accurate)
- `face_landmarker.task` - Face landmark detection model
- `hand_landmarker.task` - Hand landmark detection model

**Location**: These models are downloaded automatically by MediaPipe on first use and cached in:
- Linux: `~/.mediapipe/`
- Windows: `%USERPROFILE%\.mediapipe\`
- macOS: `~/.mediapipe/`

**Model Sizes**:
- Pose Landmarker Lite: ~5 MB
- Pose Landmarker Full: ~12 MB  
- Pose Landmarker Heavy: ~26 MB
- Face Landmarker: ~2.9 MB
- Hand Landmarker: ~8.6 MB

**Total Storage**: ~55 MB for all MediaPipe models

**Use Cases**:
- Analyzing reference images for pose structure
- Detecting anatomical errors in canvas drawings
- Identifying proportions and symmetry issues
- Guiding corrective drawing actions

**Note**: MediaPipe models use TensorFlow Lite for efficient inference on CPU or GPU.

## Optional Models (For Enhanced Functionality)

### 2. Style Transfer / Image Generation Models

**Purpose**: Generate stylized references for artistic inspiration (Imagination System)

**Recommended Options**:

#### Option A: Stable Diffusion XL (SDXL)
- **Model**: stabilityai/stable-diffusion-xl-base-1.0
- **Size**: ~7 GB
- **Use Case**: Generating stylized reference images
- **Installation**: 
  ```bash
  pip install diffusers transformers accelerate
  ```
- **Usage**: Image-to-image generation for style suggestions
- **Note**: Requires GPU with 8+ GB VRAM for optimal performance

#### Option B: ControlNet
- **Model**: lllyasviel/control_v11p_sd15_*
- **Size**: ~1.5 GB per model
- **Use Case**: Structure-preserving style transfer
- **Installation**:
  ```bash
  pip install diffusers transformers
  ```
- **Variants**: 
  - `control_v11p_sd15_canny` - Edge-based control
  - `control_v11p_sd15_openpose` - Pose-based control
  - `control_v11p_sd15_lineart` - Line art control

#### Option C: Lightweight Alternatives
- **Model**: runwayml/stable-diffusion-v1-5
- **Size**: ~4 GB
- **Use Case**: Faster style suggestions on consumer hardware
- **Memory**: Works on GPUs with 4+ GB VRAM

**Important Notes**:
- These models are **optional** for the Imagination System
- The system currently uses placeholder implementations that can work without these models
- Actual image generation requires explicit model download and configuration
- Generated images are used **only as reference/inspiration**, not as final output
- All drawing is performed by the Motor System with deliberate strokes

### 3. Segmentation Models (Optional Enhancement)

**Purpose**: Region-specific style application and masking

**Recommended**:
- **Model**: facebook/maskformer-swin-base-ade
- **Size**: ~220 MB
- **Use Case**: Automatic region detection for selective styling
- **Installation**:
  ```bash
  pip install transformers torch
  ```

**Alternative**:
- **Model**: nvidia/segformer-b0-finetuned-ade-512-512
- **Size**: ~14 MB
- **Use Case**: Lightweight segmentation for region masking

## Model Configuration

### Setting Up Optional Models

To enable full Imagination System functionality with image generation:

1. **Create a model configuration file** (`config/models.yaml`):
```yaml
imagination:
  enable_generation: true
  model_type: "sdxl"  # or "sd15", "controlnet"
  model_path: "stabilityai/stable-diffusion-xl-base-1.0"
  device: "cuda"  # or "cpu", "mps"
  cache_dir: "~/.cache/cerebrum/models"
```

2. **Download models manually** (optional):
```python
from diffusers import StableDiffusionXLPipeline
import torch

# Download and cache
pipe = StableDiffusionXLPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16,
    use_safetensors=True,
    cache_dir="~/.cache/cerebrum/models"
)
```

3. **Update Imagination Module** to use downloaded models:
```python
from imagination import ImaginationModule

# With default (no generation)
imagination = ImaginationModule()

# With model-based generation (if models downloaded)
imagination = ImaginationModule(enable_generation=True)
```

## Storage Requirements Summary

### Minimum (Core Functionality)
- **MediaPipe Models**: ~55 MB
- **Python Dependencies**: ~500 MB
- **Total**: ~555 MB

### Recommended (With Style Generation)
- **MediaPipe Models**: ~55 MB
- **Stable Diffusion XL**: ~7 GB
- **Python Dependencies**: ~2 GB
- **Total**: ~9 GB

### Full Setup (All Optional Models)
- **MediaPipe Models**: ~55 MB
- **SDXL**: ~7 GB
- **ControlNet Models**: ~4.5 GB (3 variants)
- **Segmentation Models**: ~220 MB
- **Python Dependencies**: ~2.5 GB
- **Total**: ~14.3 GB

## Hardware Recommendations

### Minimum Requirements (Core Features Only)
- **CPU**: Any modern CPU (2+ cores)
- **RAM**: 4 GB
- **Storage**: 1 GB free
- **GPU**: Not required (MediaPipe works on CPU)

### Recommended (With Style Generation)
- **CPU**: 4+ cores
- **RAM**: 16 GB
- **Storage**: 10 GB free
- **GPU**: NVIDIA GPU with 8+ GB VRAM
- **CUDA**: Version 11.8 or later

### Optimal (Full Features)
- **CPU**: 8+ cores
- **RAM**: 32 GB
- **Storage**: 20 GB free on SSD
- **GPU**: NVIDIA RTX 3080 or better (12+ GB VRAM)
- **CUDA**: Version 11.8 or later

## Performance Notes

### MediaPipe Performance
- **CPU Mode**: 
  - Pose detection: ~50-100ms per frame
  - Face detection: ~30-50ms per frame
  - Hand detection: ~40-60ms per frame
  
- **GPU Mode** (with TensorFlow GPU):
  - Pose detection: ~10-20ms per frame
  - Face detection: ~5-10ms per frame
  - Hand detection: ~5-15ms per frame

### Style Generation Performance
- **SDXL on RTX 3080**:
  - 512x512: ~2-3 seconds
  - 1024x1024: ~5-8 seconds
  
- **SDXL on RTX 4090**:
  - 512x512: ~1-2 seconds
  - 1024x1024: ~3-4 seconds
  
- **SD 1.5 on RTX 3060**:
  - 512x512: ~3-4 seconds
  - 768x768: ~6-8 seconds

- **CPU Only** (not recommended):
  - 512x512: ~2-5 minutes
  - 1024x1024: ~8-15 minutes

## Cloud/API Alternatives

If local model execution is not feasible, consider these alternatives:

### 1. Replicate API
- Models: SDXL, ControlNet, others
- Pricing: Pay per generation (~$0.003-0.01 per image)
- Setup: API key only, no local storage needed

### 2. Stability AI API
- Models: SDXL, Stable Diffusion 3
- Pricing: Credit-based (~$0.002-0.008 per image)
- Setup: API key only

### 3. HuggingFace Inference API
- Models: Various Stable Diffusion models
- Pricing: Free tier available, pay for more
- Setup: API token

**Note**: Using cloud APIs eliminates local storage and compute requirements but introduces latency and ongoing costs.

## Installation Scripts

### Quick Setup (Core Only)
```bash
# Install core dependencies (includes MediaPipe)
pip install -r requirements.txt

# MediaPipe models download automatically on first use
python -c "from vision import VisionModule; v = VisionModule(); v.close()"
```

### Full Setup (With Style Generation)
```bash
# Install all dependencies
pip install -r requirements.txt
pip install diffusers transformers accelerate torch torchvision

# Download SDXL
python scripts/download_models.py --model sdxl

# Or download all models
python scripts/download_models.py --all
```

### Verify Installation
```bash
# Check installed models
python scripts/check_models.py

# Test model inference
python scripts/test_models.py
```

## Updating Models

MediaPipe models are updated automatically by the library. To force update:

```bash
# Clear MediaPipe cache
rm -rf ~/.mediapipe/

# Models will re-download on next use
python -c "from vision import VisionModule; v = VisionModule(); v.close()"
```

For Stable Diffusion models:
```bash
# Clear HuggingFace cache
rm -rf ~/.cache/huggingface/

# Re-download
python scripts/download_models.py --model sdxl --force
```

## Troubleshooting

### MediaPipe Issues
- **Error**: "Failed to download model"
  - Solution: Check internet connection, clear cache and retry
  
- **Error**: "No module named 'mediapipe'"
  - Solution: `pip install --upgrade mediapipe`

### Style Generation Issues  
- **Error**: "CUDA out of memory"
  - Solution: Reduce image size, enable CPU offload, or use SD 1.5
  
- **Error**: "Model not found"
  - Solution: Check model name, clear cache, re-download

## License Considerations

- **MediaPipe**: Apache 2.0 License (free for commercial use)
- **Stable Diffusion XL**: CreativeML Open RAIL++-M License (free with restrictions)
- **ControlNet**: Apache 2.0 License (free for commercial use)

Always review model licenses before commercial deployment.

## Summary

**Core Cerebrum functionality requires only:**
- MediaPipe models (~55 MB, auto-downloaded)
- Standard Python libraries

**Style generation is optional and requires:**
- Stable Diffusion models (~4-7 GB)
- GPU with 4-8+ GB VRAM (or CPU with patience)

**The platform is designed to work without generative AI models**, using them only as optional inspiration sources while maintaining full control over the drawing process through the Motor System.

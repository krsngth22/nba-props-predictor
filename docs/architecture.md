# System Architecture

## Overview

Origami CV is a hybrid local/cloud system. Heavy ML inference runs locally to avoid cloud compute costs, while a lightweight Claude wrapper runs persistently on AWS EC2.

---

## Request Flow

```
User uploads image (browser)
         ↓
React frontend (Vercel CDN)
         ↓  POST /analyze (multipart/form-data)
Local FastAPI server (WSL via ngrok tunnel)
         ↓  YOLOv8 inference (CPU, ~100ms)
Detected symbols:
[{"cls": "arrow", "confidence": 0.98, "bbox": [...]},
 {"cls": "fold-line", "confidence": 0.71, "bbox": [...]}]
         ↓  POST /instructions (JSON)
FastAPI Claude wrapper (AWS EC2 t3.micro)
         ↓  Anthropic Claude Sonnet API (~2.5s)
Structured JSON fold instructions:
{"steps": [{"step_number": 1, "instruction": "...", "fold_type": "valley-fold"}]}
         ↓
React frontend renders:
  - Step panel with plain-English instructions
  - Three.js 3D paper mesh with GSAP fold animations
```

---

## Component Breakdown

### Frontend (Vercel)

| File | Purpose |
|---|---|
| App.js | Main state management, upload handler |
| api.js | Axios HTTP client, calls local backend via ngrok |
| ImageUpload.jsx | Drag-and-drop file upload with preview |
| PaperScene.jsx | Three.js canvas, OrbitControls, GSAP fold animations |
| StepPanel.jsx | Step navigation, instruction display, progress dots |

**Key libraries:**
- React 19 + Tailwind CSS (UI)
- @react-three/fiber + @react-three/drei (Three.js in React)
- GSAP (smooth fold animations)
- Axios (HTTP requests)

---

### Local Backend (FastAPI + ngrok)

Runs on developer's machine (WSL). Handles the heavy CV inference.

**Responsibilities:**
- Accept image uploads from the React frontend
- Run YOLOv8 inference (CPU, ~100ms per image)
- Forward detected symbols to EC2 for Claude processing
- Return combined response to frontend

**Model specs:**
- Architecture: YOLOv8n (nano)
- Weights: 6.3MB (best.pt)
- Input: 640×640px
- Classes: arrow, fold-line
- Inference time: 85-215ms on CPU

---

### Cloud Backend (AWS EC2 t3.micro)

Always-on Claude wrapper. Tiny Docker image (56MB).

**Responsibilities:**
- Accept detection JSON from local backend
- Format detections as natural language for Claude
- Call Anthropic Claude Sonnet API
- Parse and return structured JSON instructions

**Why separate from local backend?**
The EC2 container has no PyTorch or OpenCV — it's pure Python + FastAPI + anthropic SDK. This keeps the Docker image at 56MB instead of 3GB+, fitting comfortably on a t3.micro's 8GB disk.

---

### ML Pipeline

**Data collection:**
- 30 origami diagram images from origami instruction websites
- Mix of step-by-step diagrams and crease patterns

**Labeling (Roboflow):**
- 691 total bounding box annotations
- 2 classes: arrow (297), fold-line (394)
- Train/val/test split: 80/10/10

**Augmentation (Roboflow):**
- Horizontal + vertical flip
- Rotation: ±15°
- Brightness: ±25%
- Blur: up to 1px
- 3x multiplier → 78 training images

**Training:**
- Model: YOLOv8n (pretrained on COCO)
- Epochs: 50
- Image size: 640×640
- Batch size: 8
- Hardware: CPU (Intel i5-1340P)
- Training time: ~16 minutes

**Results:**

| Class | mAP50 | Precision | Recall |
|---|---|---|---|
| arrow | 0.891 | 0.681 | 0.889 |
| fold-line | 0.248 | 0.799 | 0.185 |
| overall | 0.569 | 0.740 | 0.537 |

**Note on fold-line performance:**
Fold-line detection is deliberately de-emphasized. Straight lines are better detected by OpenCV's HoughLinesP (rule-based, no training needed). YOLO's strength is in complex visual patterns — arrows with varying orientations and styles.

---

## Claude Prompt Design

Detections are converted to natural language before sending to Claude:

```
1. arrow (confidence: 0.98) at left-top of image, size: 36x165px
2. arrow (confidence: 0.90) at center-middle of image, size: 102x21px
3. fold-line (confidence: 0.71) at right-top of image, size: 48x312px
```

Claude returns structured JSON:
```json
{
  "steps": [
    {
      "step_number": 1,
      "instruction": "Fold the left edge up to meet the right edge",
      "fold_type": "valley-fold",
      "explanation": "The large vertical arrow on the left indicates...",
      "position": "left side of paper, running top to bottom"
    }
  ],
  "difficulty": "beginner",
  "estimated_steps": 8,
  "notes": "Focus on the high-confidence arrows first..."
}
```

---

## Latency Breakdown

| Step | Time |
|---|---|
| Image upload | ~50ms |
| YOLOv8 inference | 85–215ms |
| EC2 network round trip | ~50ms |
| Claude API call | 2,000–3,000ms |
| Frontend rendering | ~instant |
| **Total** | **~2.5–3.5s** |

---

## Cost Analysis

| Component | Cost |
|---|---|
| AWS EC2 t3.micro | Free tier (750 hrs/month) |
| Vercel hobby plan | Free |
| ngrok free tier | Free |
| Anthropic Claude API | ~$0.003 per analysis |
| Roboflow free tier | Free (up to 1000 images) |
| **Total fixed cost** | **$0/month** |
| **Per-use cost** | **~$0.003** |

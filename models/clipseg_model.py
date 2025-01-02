import torch
from transformers import CLIPSegProcessor, CLIPSegForImageSegmentation
from PIL import Image
import os

MODEL_DIR = "models"
OUTPUT_DIR = "app/static/uploads/segmented"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_clipseg_model():
    processor = CLIPSegProcessor.from_pretrained("CIDAS/clipseg-rd64-refined")
    model = CLIPSegForImageSegmentation.from_pretrained("CIDAS/clipseg-rd64-refined")
    return {"processor": processor, "model": model}

def segment_image(model, image_path, prompt):
    processor = model["processor"]
    model_instance = model["model"]

    image = Image.open(image_path).convert("RGB")
    inputs = processor(text=prompt, images=image, return_tensors="pt")
    outputs = model_instance(**inputs)

    preds = torch.sigmoid(outputs.logits).squeeze().detach().cpu().numpy()
    mask = Image.fromarray((preds * 255).astype("uint8"))
    mask_path = os.path.join(OUTPUT_DIR, f"segmented_{os.path.basename(image_path)}")
    mask.save(mask_path)

    return mask_path

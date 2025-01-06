"""
This module provides functions to load the CLIPSeg model and perform image segmentation.
"""

import torch
from transformers import CLIPSegProcessor, CLIPSegForImageSegmentation
from PIL import Image
import os
import numpy as np
import cv2

MODEL_DIR = "models"
OUTPUT_DIR = "../static/segmented"
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


def segment_image_new(model,image_path, prompt):
    # Load and preprocess the image
    processor = model["processor"]
    model = model["model"]

    image = Image.open(image_path).convert("RGB")
    inputs = processor(text=prompt, images=image, return_tensors="pt")

    # Get segmentation logits
    with torch.no_grad():
        outputs = model(**inputs)

    segmentation_logits = outputs.logits
    segmentation_mask = (
        torch.sigmoid(segmentation_logits).cpu().numpy()[0, :, :]
    )  # Extract 2D mask

    # Apply a threshold to create a binary mask
    threshold = 0.5
    binary_mask = (segmentation_mask > threshold).astype(np.uint8)

    # Highlight the segmented area
    mask_image = Image.fromarray((binary_mask * 255).astype(np.uint8)).resize(
        image.size
    )
    mask = np.array(mask_image)
    image_array = np.array(image)
    
    highlighted_image = apply_violet_blue_mask(image_array, mask)
    segmented_image = Image.fromarray(highlighted_image)
    
    mask_path = os.path.join(OUTPUT_DIR, f"segmented_{os.path.basename(image_path)}")
    segmented_image.save(mask_path)

    return mask_path

def apply_violet_blue_mask(image_array, mask):

    final_image = image_array.copy()

    # Blue-Violet color for highlighting
    blue_violet = np.array([226, 43, 138], dtype=np.uint8)

    # Apply alpha blending to the segmented area
    alpha = 0.5
    for c in range(3):  # Loop over each color channel (R, G, B)
        final_image[:, :, c] = np.where(
            mask > 0,  # Where the mask is greater than 0 (segmented region)
            (1 - alpha) * image_array[:, :, c] + alpha * blue_violet[c],  # Blend with blue-violet
            image_array[:, :, c]  # Else, keep original color
        )
    return final_image


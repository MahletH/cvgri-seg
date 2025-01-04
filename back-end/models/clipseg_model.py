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
    # highlighted_image[mask == 0] = [0, 0, 0]  # Black out unsegmented areas

    
    mask_path = os.path.join(OUTPUT_DIR, f"segmented_{os.path.basename(image_path)}")
    segmented_image.save(mask_path)

    return mask_path

def apply_violet_blue_mask(image_array, circle_mask):
    circle_mask = cv2.resize(circle_mask, (image_array.shape[1], image_array.shape[0]))
    
    if len(circle_mask.shape) == 3:
        circle_mask = cv2.cvtColor(circle_mask, cv2.COLOR_BGR2GRAY)

    # Convert the mask to binary (0 and 255 values)
    circle_mask = (circle_mask > 0).astype(np.uint8) * 255

    blue_violet = np.array([226, 43, 138], dtype=np.uint8)

    final_image = image_array.copy()

    alpha = 0.5
    for c in range(3):
        final_image[:, :, c] = np.where(
            circle_mask > 0,
            (1 - alpha) * image_array[:, :, c] + alpha * blue_violet[c],
            image_array[:, :, c]
        ).astype(np.uint8)

    return final_image


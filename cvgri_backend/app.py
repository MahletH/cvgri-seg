from flask import Flask, request, jsonify
import os
from PIL import Image
import torch
from transformers import CLIPSegProcessor, CLIPSegForImageSegmentation
import numpy as np

app = Flask(__name__)

# Set up directories for saving files
UPLOAD_FOLDER = 'uploads'
SEGMENTED_FOLDER = 'segmented'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SEGMENTED_FOLDER'] = SEGMENTED_FOLDER

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SEGMENTED_FOLDER, exist_ok=True)

# Load the CLIPSeg model and processor
processor = CLIPSegProcessor.from_pretrained("CIDAS/clipseg-rd64-refined")
model = CLIPSegForImageSegmentation.from_pretrained("CIDAS/clipseg-rd64-refined")

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Segmentation function using CLIPSeg model
def segment_image(image_path, prompt):
    # Load the image
    image = Image.open(image_path).convert("RGB")
    
    # Preprocess the image and prompt using CLIPSegProcessor
    inputs = processor(text=prompt, images=image, return_tensors="pt", padding=True)

    # Run the image and prompt through the CLIPSeg model
    with torch.no_grad():
        outputs = model(**inputs)
    
    # The outputs contain the segmentation logits, directly access them
    segmentation_logits = outputs.logits
    
    # Apply sigmoid activation to the logits to obtain probabilities
    segmentation_mask = torch.sigmoid(segmentation_logits).cpu().numpy()[0]
    
    # Convert the segmentation mask to an image
    mask_image = Image.fromarray((segmentation_mask * 255).astype(np.uint8))
    
    # Save the segmented image
    segmented_image_path = os.path.join(app.config['SEGMENTED_FOLDER'], 'segmented_output.png')
    mask_image.save(segmented_image_path)
    
    return segmented_image_path

@app.route('/api/segment', methods=['POST'])
def segment():
    # Get the image and prompt from the request
    image_file = request.files['image']
    prompt = request.form['prompt']
    
    # Check if the file is allowed
    if image_file and allowed_file(image_file.filename):
        # Save the image to the uploads folder
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_file.filename)
        image_file.save(image_path)
        
        # Call the segmentation function using CLIPSeg
        segmented_image_path = segment_image(image_path, prompt)
        
        # Return the path to the segmented image
        return jsonify({"message": "Segmentation complete", "segmented_image_path": segmented_image_path}), 200
    else:
        return jsonify({"error": "Invalid file format"}), 400

if __name__ == '__main__':
    app.run(debug=True)

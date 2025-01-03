from flask import Flask, render_template, request, jsonify
import os
import sys
from werkzeug.utils import secure_filename
from PIL import Image

# Ensure the correct path for the models package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.clipseg_model import load_clipseg_model, segment_image as clipseg_segment
from models.langsam_model import LangSAM

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('app', 'static', 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
app.config['OUTPUT_DIR'] = os.path.join('app', 'static', 'uploads', 'lang_segmented')

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_DIR'], exist_ok=True)

# Load models
models = {
    "clipseg": load_clipseg_model(),
    "lang_sam": LangSAM()
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/segment', methods=['POST'])
def segment():
    if 'image' not in request.files or 'prompt' not in request.form or 'model_type' not in request.form:
        return jsonify({'error': 'Image, prompt, and model_type are required'}), 400

    file = request.files['image']
    prompt = request.form['prompt']
    model_type = request.form['model_type']

    if model_type not in models:
        return jsonify({'error': f"Unsupported model type '{model_type}'"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            if model_type == 'clipseg':
                output_path = clipseg_segment(models['clipseg'], filepath, prompt)
            elif model_type == 'lang_sam':
                # Initialize LangSAM model
                lang_sam_model = LangSAM()
                print(f"LangSAM model initialized with SAM type: {lang_sam_model.sam_type}")

                # Load image and call langsam_predict
                image_pil = Image.open(filepath).convert("RGB")     # Convert filepath to PIL Image
                print(f"Loaded image from: {filepath}")
                masks, boxes, phrases, logits = lang_sam_model.langsam_predict(image_pil, prompt)
                # Ensure masks are of shape (batch_size, H, W)
                if len(masks.shape) == 3:  # Add batch dimension if missing
                    masks = masks.unsqueeze(0)
                elif len(masks.shape) == 4 and masks.shape[1] == 1:  # Remove channel dimension if unnecessary
                    masks = masks.squeeze(1)
                    
                print(f"LangSAM model prediction completed with {len(boxes)} boxes")

                # Process and save the output
                mask_path = os.path.join(app.config['OUTPUT_DIR'], f"segmented_{os.path.basename(filepath)}")
                output_path = LangSAM.save_segmented_image(image_pil, masks, boxes, mask_path)

            segmented_image_url = os.path.relpath(output_path, start=os.path.join('app', 'static'))
            print(f"Segmented image saved at: {segmented_image_url}")
            return jsonify({'segmented_image': segmented_image_url}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    app.run(debug=True)

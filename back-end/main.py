from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os, sys
from werkzeug.utils import secure_filename
from cloudary_service import upload_image  # Import the Cloudinary service

# Ensure the correct path for the models package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.clipseg_model import load_clipseg_model, segment_image_new as clipseg_segment
from models.langsam_model import LangSAM, langsam_output_path

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load models
models = {
    "clipseg": load_clipseg_model(),
    "langsam": LangSAM(),
}

# Utility function to check allowed file types
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# API Route
@app.route("/api/segment", methods=["POST"])
def segment_image():
    try:
        # Validate file
        if "image" not in request.files or not allowed_file(request.files["image"].filename):
            return jsonify({"error": "Invalid or missing image file"}), 400

        file = request.files["image"]
        prompt = request.form.get("prompt", "").strip()
        model = request.form.get("model")
        print(f"Model: {model}")

        # Validate model selection
        if not model:
            return jsonify({"error": "Model selection is required"}), 400
        if model not in models:
            return jsonify({"error": f"Unsupported model type '{model}'"}), 400

        # Save the uploaded file
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)

            try:
                # Segment image based on the selected model
                if model == "clipseg":
                    segmented_image_path = clipseg_segment(models["clipseg"], file_path, prompt)
                elif model == "langsam":
                    segmented_image_path = langsam_output_path(models["langsam"], file_path, prompt)

                # Upload to Cloudinary
                segmented_image_url = upload_image(segmented_image_path)
                # Remove the locally saved segmented image to clean up
                if os.path.exists(segmented_image_path):
                    os.remove(segmented_image_path)

                return jsonify({"segmented_image": segmented_image_url}), 200

            except Exception as e:
                return jsonify({"error": str(e)}), 500
        return jsonify({"error": "Invalid file type"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Main Route
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)

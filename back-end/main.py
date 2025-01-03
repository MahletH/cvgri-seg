"""
This module provides a Flask web application for image segmentation using the CLIPSeg model.
"""

from flask import Flask, render_template, request, jsonify
import os
import sys
from werkzeug.utils import secure_filename
from flask_cors import CORS
from cloudary_service import upload_image

# Ensure the correct path for the models package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.clipseg_model import load_clipseg_model, segment_image

app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = os.path.join("static", "uploads")
CORS(app)
app.config["UPLOAD_FOLDER"] = os.path.join("static", "uploads")
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg"}

# Ensure upload folder exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Load the CLIPSeg model
model = load_clipseg_model()


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/segment", methods=["POST"])
def segment():
    if "image" not in request.files or "prompt" not in request.form:
        return jsonify({"error": "Image and prompt are required"}), 400

    file = request.files["image"]
    prompt = request.form["prompt"]

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        file.save(filepath)

        try:
            segmented_image = segment_image(model, filepath, prompt)
            image_path = upload_image(segmented_image)
            return jsonify({"segmented_image": image_path}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Invalid file type"}), 400


if __name__ == "__main__":
    app.run(debug=True)

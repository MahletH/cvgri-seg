# Web App - Zero-Shot Image Segmentation


This is a simple Flask-based web app that performs zero-shot image segmentation. It accepts an image and a text prompt from the user, processes them using a pre-trained model, and returns the segmented image.

## Features

- Upload an image.
- Provide a text prompt for segmentation (e.g., "Segment the car").
- View the segmented result with the original image and the segmented masks.

## Technologies

- **Flask**: Web framework for Python.
- **Transformers**: Hugging Face Transformers library for pre-trained models.
- **Torch**: PyTorch for running the model.
- **Matplotlib**: For visualizing and saving the segmentation results.
- **React.js**: Frontend for handling user interactions.

## Installation

### 1. Clone the repository

```bash
git https://github.com/MahletH/cvgri-seg.git
cd cvgri_backend
```

### 2. Set up the backend (Flask)

#### Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

#### Install backend dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up the frontend (React)

#### Navigate to the `cvgri_web` folder

```bash
cd cvgri_web
```

#### Install frontend dependencies

```bash
npm install
```

### 4. Running the application

#### Start the Flask backend

```bash
python app.py
```

The backend will be running on `http://127.0.0.1:5000`.

#### Start the React frontend

```bash
npm start
```

The frontend will be running on `http://localhost:3000`.

## Usage

1. Open the app in your browser (`http://localhost:3000`).
2. Upload an image and enter a prompt (e.g., "Segment the car").
3. Click **Segment Image** to see the segmented result.

## Folder Structure

```
flask-image-segmentation/
|--- cvgri_backend/
|    |--- app.py
|    |--- requirements.txt
|    ├── segmented/          # Output images
│         └── segmented_output.png
|--- cvgri_web/             # React frontend
│   └── src/
│   └── public/
└── README.md
```

## Contributing

1. Fork this repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to your branch (`git push origin feature-branch`).
5. Create a pull request.
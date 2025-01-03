# Image Segmentation Chatbot

A chatbot web app capable of accepting both an image and a prompt (e.g., "Dog"). The chatbot displays the segmented image as output.

## Overview

This application allows users to interact with an AI-powered chatbot for image segmentation. Users can upload an image and provide a prompt to identify and segment specific objects or areas in the image.

## Technologies

- HTML
- CSS
- JavaScript
- Flask
- Transformers
- PyTorch

## File Structure
```bash
image-segmentation-app/
│
├── app/
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css         # Styling for the chatbot interface
│   │   ├── js/
│   │   │   └── script.js          # Optional frontend interactivity scripts
│   │   └── uploads/               # Storage for uploaded images
│   │       └── (uploaded images)
│   ├── templates/
│   │   └── index.html             # Frontend chatbot interface
│   └── main.py                    # Backend logic with Flask
│
├── models/
│   └── clipseg_model.py           # Image segmentation model using CLIPSeg
│
├── requirements.txt               # Python dependencies
└── README.md                      # Project documentation
```

## Installation

Follow these steps to set up the project:

### Clone the Repository
```bash
git clone -b image-segmentation-app https://github.com/MahletH/cvgri-seg.git
cd cvgri-seg
```

### Create a Virtual Environment

1. Install virtualenv (if not already installed):
```bash
pip install virtualenv
```

2. Create and activate the virtual environment:

- On macOS/Linux:
```bash
virtualenv -p python3.11 venv
source venv/bin/activate
```

- On Windows
```bash
virtualenv -p python3.11 venv
venv\Scripts\activate
```
**Note**: Python 3.11 is selected because PyTorch currently does not support Python 3.13 (latest version).

### Install Dependencies
```bash
pip install -r requirements.txt
```

## Running the Application
```bash
python ./app/main.py
```

The application will run on http://127.0.0.1:5000.

## Features

- Accepts both image and text prompts for segmentation.

- Utilizes the CLIPSeg model for advanced image segmentation.

- Simple and intuitive user interface.

## Future Enhancements

- Add support for multiple segmentation models.

- Enable real-time segmentation previews.

- Enhance chatbot interactivity and conversational abilities.
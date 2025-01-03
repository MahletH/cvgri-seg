"""
This module provides a service for uploading images to Cloudinary.
"""

import cloudinary
import cloudinary.uploader

# Configuration
cloudinary.config(
    cloud_name="dx8mx8biu",
    api_key="777964454663135",
    api_secret="Bt9zE82sOd5Uzwadws0oEIMdBH4",  # Click 'View API Keys' above to copy your API secret
    secure=True,
)


def upload_image(image_path):
    """
    Uploads an image to Cloudinary and returns the public URL.

    Args:
        image_path (str): The path to the image file to be uploaded.

    Returns:
        str: The public URL of the uploaded image.
    """
    result = cloudinary.uploader.upload(image_path)
    public_url = result["secure_url"]
    print(public_url)
    return public_url

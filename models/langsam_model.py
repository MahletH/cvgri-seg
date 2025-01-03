import os
import warnings
import numpy as np
import torch
from PIL import Image
from torchvision.utils import draw_bounding_boxes, draw_segmentation_masks
import cv2
import groundingdino.datasets.transforms as T
from groundingdino.models import build_model
from groundingdino.util import box_ops
from groundingdino.util.inference import predict
from groundingdino.util.slconfig import SLConfig
from groundingdino.util.utils import clean_state_dict
from huggingface_hub import hf_hub_download
from segment_anything import sam_model_registry, SamPredictor

# Constants
SAM_MODELS = {
    "vit_h": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth",
    "vit_l": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth",
    "vit_b": "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"
}
CACHE_PATH = os.environ.get("TORCH_HOME", os.path.expanduser("~/.cache/torch/hub/checkpoints"))
MIN_AREA = 100

# Utility Functions
def load_image(image_path: str):
    return Image.open(image_path).convert("RGB")

def draw_image(image, masks, boxes, labels, alpha=0.4):
    # Convert image to tensor
    # image_tensor = torch.from_numpy(np.asarray(image_pil)).permute(2, 0, 1)

    # # Draw masks
    # if masks.shape[0] > 0:  # Ensure there's at least one mask
    #     image_with_masks = draw_segmentation_masks(image_tensor, masks, alpha=0.4)
    image = torch.from_numpy(image).permute(2, 0, 1)
    if len(boxes) > 0:
        image = draw_bounding_boxes(image, boxes, colors=['red'] * len(boxes), labels=labels, width=2)
    if len(masks) > 0:
        image = draw_segmentation_masks(image, masks=masks, colors=['cyan'] * len(masks), alpha=alpha)
    return image.numpy().transpose(1, 2, 0)

def get_contours(mask):
    mask = mask.astype(np.uint8) * 255
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return [c for c in contours if cv2.contourArea(c) > MIN_AREA]

def contour_to_points(contour):
    return [point.tolist() for point in contour.reshape(-1, 2).astype(np.float32)]

def generate_labelme_json(binary_masks, labels, image_size, image_path=None):
    num_masks = binary_masks.shape[0]
    binary_masks = binary_masks.numpy()

    json_dict = {
        "version": "4.5.6",
        "imageHeight": image_size[0],
        "imageWidth": image_size[1],
        "imagePath": image_path,
        "flags": {},
        "shapes": []
    }

    for i in range(num_masks):
        mask = binary_masks[i]
        label = labels[i]
        for contour in get_contours(mask):
            json_dict["shapes"].append({
                "label": label,
                "line_color": None,
                "fill_color": None,
                "points": contour_to_points(contour),
                "shape_type": "polygon"
            })
    return json_dict

def transform_image(image) -> torch.Tensor:
    transform = T.Compose([
        T.RandomResize([800], max_size=1333),
        T.ToTensor(),
        T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    image_transformed, _ = transform(image, None)
    return image_transformed

# Model Loader
def load_model_hf(repo_id, filename, ckpt_config_filename, device='cpu'):
    args = SLConfig.fromfile(hf_hub_download(repo_id, ckpt_config_filename))
    model = build_model(args)
    model.load_state_dict(clean_state_dict(torch.load(hf_hub_download(repo_id, filename), map_location='cpu')['model']), strict=False)

    # model.load_state_dict(clean_state_dict(torch.load(hf_hub_download(repo_id, filename), map_location='cpu')['model']))
    model.eval().to(device)
    return model

# LangSAM Class
class LangSAM:
    def __init__(self, sam_type="vit_h", ckpt_path=None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.sam_type = sam_type
        self.build_groundingdino()
        self.build_sam(ckpt_path)

    def build_groundingdino(self):
        repo_id, filename, config = "ShilongLiu/GroundingDINO", "groundingdino_swinb_cogcoor.pth", "GroundingDINO_SwinB.cfg.py"
        self.groundingdino = load_model_hf(repo_id, filename, config, self.device)

    def build_sam(self, ckpt_path):
        checkpoint_url = SAM_MODELS.get(self.sam_type, SAM_MODELS["vit_h"])
        if ckpt_path is None:
            state_dict = torch.hub.load_state_dict_from_url(checkpoint_url)
            model = sam_model_registry[self.sam_type]()
            model.load_state_dict(state_dict, strict=True)
        else:
            model = sam_model_registry[self.sam_type](ckpt_path)
        model.to(self.device)
        self.sam = SamPredictor(model)

    def predict_dino(self, image_pil, text_prompt, box_threshold, text_threshold):
        image_trans = transform_image(image_pil)
        boxes, logits, phrases = predict(
            model=self.groundingdino, image=image_trans, caption=text_prompt,
            box_threshold=box_threshold, text_threshold=text_threshold, device=self.device
        )
        W, H = image_pil.size
        boxes = box_ops.box_cxcywh_to_xyxy(boxes) * torch.Tensor([W, H, W, H])
        return boxes, logits, phrases

    def predict_sam(self, image_pil, boxes):
        image_array = np.asarray(image_pil)
        self.sam.set_image(image_array)
        transformed_boxes = self.sam.transform.apply_boxes_torch(boxes, image_array.shape[:2])
        masks, _, _ = self.sam.predict_torch(
            point_coords=None, point_labels=None,
            boxes=transformed_boxes.to(self.device), multimask_output=False
        )
        return masks.cpu()

    def langsam_predict(self, image_pil, text_prompt, box_threshold=0.3, text_threshold=0.25):
        boxes, logits, phrases = self.predict_dino(image_pil, text_prompt, box_threshold, text_threshold)
        masks = self.predict_sam(image_pil, boxes) if len(boxes) > 0 else torch.tensor([])
        print(f"LangSAM model prediction completed with {len(boxes)} boxes")
        print("Mask shape:", masks.shape)

        return masks, boxes, phrases, logits
    
    def save_segmented_image(image_pil, masks, boxes, filepath):
        # Convert PIL Image to numpy array for drawing
        image_np = np.array(image_pil)
        
        # Draw masks and bounding boxes
        if masks.numel() > 0:  # Check if masks are not empty
            image_np = draw_image(image_np, masks, boxes, labels=["Segment"] * len(boxes))
        
        # Save the segmented image
        output_dir = os.path.join('app', 'static', 'uploads', 'lang_segmented')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, os.path.basename(filepath))
        Image.fromarray(image_np).save(output_path)
        
        return output_path


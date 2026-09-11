import io
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import cv2
import numpy as np
from vision.exif_parser import extract_exif_metadata

# Class mappings
CLASSES = ["Clean Road / Landscape", "Slope Fissure / Landslide Debris"]

# Setup Pretrained MobileNetV3 Small
def get_model(pretrained=True):
    # Weights parameter instead of pretrained=True for modern torchvision
    weights = models.MobileNet_V3_Small_Weights.DEFAULT if pretrained else None
    model = models.mobilenet_v3_small(weights=weights)
    
    # Modify the final layer for 2 classes
    in_features = model.classifier[3].in_features
    model.classifier[3] = nn.Linear(in_features, 2)
    model.eval()
    return model

# Global model instance
_model = get_model()

# Standard ImageNet transforms for MobileNet
_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def evaluate_opencv_fallback(image_bytes: bytes) -> float:
    """
    Pragmatic Fallback: Uses OpenCV (Canny) to compute edge density 
    and contour variance to detect surface ruptures/cracks.
    Returns a pseudo-confidence score for Hazard.
    """
    # Decode image bytes to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return 0.0
        
    # Resize for consistent metrics
    img = cv2.resize(img, (224, 224))
    
    # Apply Gaussian Blur to reduce noise
    blurred = cv2.GaussianBlur(img, (5, 5), 0)
    
    # Canny Edge Detection
    edges = cv2.Canny(blurred, 50, 150)
    
    # Edge density: ratio of edge pixels to total pixels
    edge_density = np.sum(edges > 0) / edges.size
    
    # Normal roads/landscapes have some edges, but severe cracking/debris 
    # creates highly concentrated random edge maps.
    # Typical edge density for a clean road might be < 0.05.
    # Cracks/debris might push it > 0.15.
    
    # Scale density to a pseudo-probability [0, 1]
    # Adjusted thresholds to be more sensitive to scattered debris/boulders
    # Lower baseline from 0.05 to 0.02 so fewer edges are needed to trigger a hazard
    min_threshold = 0.02
    max_threshold = 0.10
    
    # Scale density to a pseudo-probability [0, 1] with higher sensitivity
    pseudo_prob = min(max((edge_density - min_threshold) / (max_threshold - min_threshold), 0.0), 1.0)
    return pseudo_prob

def verify_field_photo(image_bytes: bytes) -> dict:
    """
    Classifies a crowdsourced field photo as genuine hazard vs noise.
    Returns validation dict including EXIF extraction.
    """
    result = {
        "is_valid": False,
        "confidence": 0.0,
        "class": "Unknown",
        "method": "MobileNetV3",
        "exif": extract_exif_metadata(image_bytes)
    }
    
    try:
        # 1. Run MobileNet Classification
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        input_tensor = _transform(img).unsqueeze(0)
        
        with torch.no_grad():
            output = _model(input_tensor)
            probabilities = torch.nn.functional.softmax(output[0], dim=0)
            
        hazard_prob = probabilities[1].item()
        clean_prob = probabilities[0].item()
        
        # If model is highly confident it's a clean road (e.g., > 0.8)
        if clean_prob > 0.8:
            result["class"] = CLASSES[0]
            result["confidence"] = clean_prob
            result["is_valid"] = False
            return result
            
        # If model is highly confident it's a hazard
        if hazard_prob > 0.7:
            result["class"] = CLASSES[1]
            result["confidence"] = hazard_prob
            result["is_valid"] = True
            return result
            
        # 2. Fallback to OpenCV if MobileNet confidence is low/ambiguous
        result["method"] = "OpenCV_Fallback"
        fallback_prob = evaluate_opencv_fallback(image_bytes)
        
        if fallback_prob > 0.5:
            result["class"] = CLASSES[1]
            result["confidence"] = fallback_prob
            result["is_valid"] = True
        else:
            result["class"] = CLASSES[0]
            result["confidence"] = 1.0 - fallback_prob
            result["is_valid"] = False
            
    except Exception as e:
        print(f"Error processing image: {e}")
        
    return result

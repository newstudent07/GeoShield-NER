import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from vision.classifier import verify_field_photo

SAMPLE_DIR = "data/sample_photos"

def main():
    if not os.path.exists(SAMPLE_DIR):
        print(f"Directory {SAMPLE_DIR} not found.")
        return
        
    images = [f for f in os.listdir(SAMPLE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not images:
        print("No sample images found.")
        return
        
    print(f"Found {len(images)} sample images. Running verification pipeline...\n")
    
    for img_name in images:
        img_path = os.path.join(SAMPLE_DIR, img_name)
        print(f"--- Processing {img_name} ---")
        
        with open(img_path, "rb") as f:
            image_bytes = f.read()
            
        result = verify_field_photo(image_bytes)
        
        # Display Result
        print(f"Valid Hazard : {result['is_valid']}")
        print(f"Class        : {result['class']}")
        print(f"Confidence   : {result['confidence']:.4f}")
        print(f"Method       : {result['method']}")
        print(f"GPS Status   : {result['exif']['gps_status']}")
        print("")

if __name__ == "__main__":
    main()

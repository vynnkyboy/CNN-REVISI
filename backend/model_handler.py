import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import numpy as np
import base64
from io import BytesIO
import cv2

class WasteClassifierMobileNet(nn.Module):
    def __init__(self, num_classes=2):
        super(WasteClassifierMobileNet, self).__init__()
        self.model = models.mobilenet_v2(weights=None)
        
        # Replace classifier
        in_features = self.model.classifier[1].in_features
        self.model.classifier = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(in_features, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, num_classes)
        )
    
    def forward(self, x):
        return self.model(x)

class WasteClassifierLight(nn.Module):
    def __init__(self, num_classes=2):
        super(WasteClassifierLight, self).__init__()
        self.model = models.mobilenet_v3_small(weights=None)
        
        in_features = self.model.classifier[3].in_features
        self.model.classifier = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(in_features, num_classes)
        )
    
    def forward(self, x):
        return self.model(x)

class WasteDetectorAPI:
    def __init__(self, model_path='models/best_waste_classifier_mobilenet.pth', model_type='mobilenetv2'):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Loading model on: {self.device}")
        
        self.model_type = model_type
        self.model = self.load_model(model_path, model_type)
        self.transform = self.get_transform()
        self.classes = ['Organik', 'Anorganik']
        print("Model loaded successfully!")
        
    def load_model(self, model_path, model_type):
        if model_type == 'mobilenetv2':
            model = WasteClassifierMobileNet(num_classes=2)
        else:
            model = WasteClassifierLight(num_classes=2)
        
        # Load model weights
        try:
            model.load_state_dict(torch.load(model_path, map_location=self.device, weights_only=True))
        except:
            # Try without weights_only for older PyTorch versions
            model.load_state_dict(torch.load(model_path, map_location=self.device))
        
        model = model.to(self.device)
        model.eval()
        return model
    
    def get_transform(self):
        return transforms.Compose([
            transforms.Resize((128, 128)),  # Match training size
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    
    def preprocess_image(self, image):
        """Preprocess PIL image for model input"""
        image = image.convert('RGB')
        image_tensor = self.transform(image).unsqueeze(0)
        return image_tensor.to(self.device)
    
    def predict_single(self, image):
        """Predict single image window"""
        image_tensor = self.preprocess_image(image)
        
        with torch.no_grad():
            output = self.model(image_tensor)
            probabilities = torch.nn.functional.softmax(output, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
        
        return self.classes[predicted.item()], confidence.item()
    
    def sliding_window_detection(self, image, window_size=128, step_size=64, confidence_threshold=0.6):
        """Detect waste using sliding window approach"""
        original_size = image.size
        image_np = np.array(image)
        height, width = image_np.shape[:2]
        
        detections = []
        
        # Resize if image is too large
        max_dim = 800
        scale = 1.0
        if max(width, height) > max_dim:
            scale = max_dim / max(width, height)
            new_size = (int(width * scale), int(height * scale))
            image = image.resize(new_size)
            image_np = np.array(image)
            height, width = image_np.shape[:2]
            window_size = int(window_size * scale)
            step_size = int(step_size * scale)
        
        # Sliding window
        for y in range(0, height - window_size + 1, step_size):
            for x in range(0, width - window_size + 1, step_size):
                window = image.crop((x, y, x + window_size, y + window_size))
                class_name, confidence = self.predict_single(window)
                
                if confidence > confidence_threshold:
                    # Scale coordinates back to original
                    orig_x = int(x / scale) if scale != 1.0 else x
                    orig_y = int(y / scale) if scale != 1.0 else y
                    orig_w = int(window_size / scale) if scale != 1.0 else window_size
                    orig_h = int(window_size / scale) if scale != 1.0 else window_size
                    
                    # FIXED: Use 'class_name' instead of 'class'
                    detections.append({
                        'bbox': [orig_x, orig_y, orig_x + orig_w, orig_y + orig_h],
                        'class_name': class_name,  # Changed from 'class' to 'class_name'
                        'confidence': float(confidence)
                    })
        
        # Apply Non-Maximum Suppression
        detections = self.non_max_suppression(detections, iou_threshold=0.3)
        
        return detections
    
    def non_max_suppression(self, detections, iou_threshold=0.3):
        """Remove overlapping bounding boxes"""
        if not detections:
            return detections
        
        # Sort by confidence descending
        detections = sorted(detections, key=lambda x: x['confidence'], reverse=True)
        
        keep = []
        while detections:
            best = detections.pop(0)
            keep.append(best)
            
            detections = [d for d in detections if self.calculate_iou(best['bbox'], d['bbox']) < iou_threshold]
        
        return keep
    
    def calculate_iou(self, box1, box2):
        """Calculate Intersection over Union"""
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        
        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0
    
    def detect_from_base64(self, image_base64):
        """Detect waste from base64 encoded image"""
        try:
            # Remove data URL prefix if present
            if ',' in image_base64:
                image_base64 = image_base64.split(',')[1]
            
            # Decode base64 to image
            image_bytes = base64.b64decode(image_base64)
            image = Image.open(BytesIO(image_bytes))
            
            return self.sliding_window_detection(image)
        
        except Exception as e:
            print(f"Error in detect_from_base64: {e}")
            raise
    
    def detect_from_file(self, file_bytes):
        """Detect waste from file bytes"""
        try:
            image = Image.open(BytesIO(file_bytes))
            return self.sliding_window_detection(image)
        
        except Exception as e:
            print(f"Error in detect_from_file: {e}")
            raise

# Singleton instance
_detector_instance = None

def get_detector():
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = WasteDetectorAPI()
    return _detector_instance
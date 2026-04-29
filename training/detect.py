import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
from pathlib import Path

class WasteDetector:
    def __init__(self, model_path='../models/best_waste_classifier.pth'):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self.load_model(model_path)
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        self.classes = ['Organik', 'Anorganik']
        
    def load_model(self, model_path):
        class WasteClassifier(nn.Module):
            def __init__(self, num_classes=2):
                super(WasteClassifier, self).__init__()
                import torchvision.models as models
                self.model = models.resnet50(weights=None)
                num_features = self.model.fc.in_features
                self.model.fc = nn.Sequential(
                    nn.Dropout(0.5),
                    nn.Linear(num_features, 512),
                    nn.ReLU(),
                    nn.Dropout(0.3),
                    nn.Linear(512, num_classes)
                )
            
            def forward(self, x):
                return self.model(x)
        
        model = WasteClassifier(num_classes=2).to(self.device)
        model.load_state_dict(torch.load(model_path, map_location=self.device))
        model.eval()
        return model
    
    def detect_waste(self, image_path, confidence_threshold=0.7):
        # Load and preprocess image
        image = Image.open(image_path).convert('RGB')
        original_size = image.size
        
        # For sliding window detection
        window_size = 224
        step_size = 112
        
        detections = []
        
        # Resize image if too large
        if original_size[0] > 800 or original_size[1] > 800:
            ratio = min(800/original_size[0], 800/original_size[1])
            new_size = (int(original_size[0]*ratio), int(original_size[1]*ratio))
            image = image.resize(new_size)
        
        image_np = np.array(image)
        height, width = image_np.shape[:2]
        
        # Sliding window
        for y in range(0, height - window_size + 1, step_size):
            for x in range(0, width - window_size + 1, step_size):
                window = image.crop((x, y, x + window_size, y + window_size))
                window_tensor = self.transform(window).unsqueeze(0).to(self.device)
                
                with torch.no_grad():
                    output = self.model(window_tensor)
                    probabilities = torch.nn.functional.softmax(output, dim=1)
                    confidence, predicted = torch.max(probabilities, 1)
                
                if confidence.item() > confidence_threshold:
                    detections.append({
                        'bbox': [x, y, x + window_size, y + window_size],
                        'class': self.classes[predicted.item()],
                        'confidence': confidence.item()
                    })
        
        # Non-maximum suppression
        detections = self.non_max_suppression(detections, iou_threshold=0.3)
        
        return detections, image
    
    def non_max_suppression(self, detections, iou_threshold=0.3):
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
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        
        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0
    
    def draw_detections(self, image, detections):
        draw = ImageDraw.Draw(image)
        colors = {'Organik': (34, 139, 34), 'Anorganik': (255, 140, 0)}  # Green for organic, Orange for inorganic
        
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        for detection in detections:
            bbox = detection['bbox']
            class_name = detection['class']
            confidence = detection['confidence']
            
            # Draw bounding box
            draw.rectangle(bbox, outline=colors[class_name], width=3)
            
            # Draw label background
            label = f"{class_name}: {confidence:.2f}"
            bbox_label = (bbox[0], bbox[1] - 25, bbox[2], bbox[1])
            draw.rectangle(bbox_label, fill=colors[class_name])
            
            # Draw label text
            draw.text((bbox[0] + 5, bbox[1] - 20), label, fill='white', font=font)
        
        return image

if __name__ == "__main__":
    detector = WasteDetector()
    
    # Test on sample image
    test_image = "../dataset/test/o/sample.jpg"  # Change to your test image path
    if Path(test_image).exists():
        detections, image = detector.detect_waste(test_image)
        print(f"Found {len(detections)} waste items:")
        for det in detections:
            print(f"  - {det['class']} (confidence: {det['confidence']:.2f})")
        
        result_image = detector.draw_detections(image, detections)
        result_image.save("detection_result.jpg")
        print("Detection result saved as detection_result.jpg")
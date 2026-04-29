import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms, models
import os
from PIL import Image
from tqdm import tqdm
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import multiprocessing
import time

# Set device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")
if device == 'cpu':
    print("⚠️  Using CPU - training will be slower. Consider using GPU if available.")

# Custom Dataset Class
class WasteDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.classes = ['o', 'r']
        self.class_to_idx = {'o': 0, 'r': 1}
        self.images = []
        self.labels = []
        
        for class_name in self.classes:
            class_dir = os.path.join(root_dir, class_name)
            if os.path.exists(class_dir):
                for img_name in os.listdir(class_dir):
                    if img_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                        self.images.append(os.path.join(class_dir, img_name))
                        self.labels.append(self.class_to_idx[class_name])
        
        print(f"Loaded {len(self.images)} images from {root_dir}")
    
    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        img_path = self.images[idx]
        image = Image.open(img_path).convert('RGB')
        label = self.labels[idx]
        
        if self.transform:
            image = self.transform(image)
        
        return image, label

# MobileNetV2 Model (FASTER!)
class WasteClassifierMobileNet(nn.Module):
    def __init__(self, num_classes=2):
        super(WasteClassifierMobileNet, self).__init__()
        # Load pretrained MobileNetV2
        self.model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V1)
        
        # Freeze early layers for faster training
        for param in self.model.parameters():
            param.requires_grad = False
        
        # Unfreeze last few layers only
        for param in self.model.features[-3:].parameters():
            param.requires_grad = True
        
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

# Lightweight Model (EVEN FASTER - for CPU training)
class WasteClassifierLight(nn.Module):
    def __init__(self, num_classes=2):
        super(WasteClassifierLight, self).__init__()
        self.model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.IMAGENET1K_V1)
        
        # Freeze most layers
        for param in self.model.parameters():
            param.requires_grad = False
        
        # Unfreeze last classifier
        in_features = self.model.classifier[3].in_features
        self.model.classifier = nn.Sequential(
            nn.Dropout(0.2),
            nn.Linear(in_features, num_classes)
        )
    
    def forward(self, x):
        return self.model(x)

def train_epoch(model, loader, criterion, optimizer):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    
    for data, target in tqdm(loader, desc="Training"):
        data, target = data.to(device), target.to(device)
        
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item()
        _, predicted = output.max(1)
        total += target.size(0)
        correct += predicted.eq(target).sum().item()
    
    return running_loss / len(loader), 100. * correct / total

def validate(model, loader, criterion):
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for data, target in tqdm(loader, desc="Validation"):
            data, target = data.to(device), target.to(device)
            output = model(data)
            loss = criterion(output, target)
            
            running_loss += loss.item()
            _, predicted = output.max(1)
            total += target.size(0)
            correct += predicted.eq(target).sum().item()
            
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(target.cpu().numpy())
    
    return running_loss / len(loader), 100. * correct / total, all_preds, all_labels

if __name__ == '__main__':
    multiprocessing.freeze_support()
    
    # Create models directory
    os.makedirs('../models', exist_ok=True)
    
    # Data transforms (smaller image size for faster training)
    train_transform = transforms.Compose([
        transforms.Resize((128, 128)),  # Smaller than 224x224 for speed
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    val_transform = transforms.Compose([
        transforms.Resize((128, 128)),  # Smaller for speed
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # Load datasets
    print("\n📂 Loading datasets...")
    train_dataset = WasteDataset('../dataset/train', transform=train_transform)
    val_dataset = WasteDataset('../dataset/valid', transform=val_transform)
    test_dataset = WasteDataset('../dataset/test', transform=val_transform)

    print(f"\n📊 Dataset statistics:")
    print(f"   Training: {len(train_dataset)} images")
    print(f"   Validation: {len(val_dataset)} images")
    print(f"   Test: {len(test_dataset)} images")

    if len(train_dataset) == 0:
        print("\n❌ ERROR: No training images found!")
        print("Please ensure dataset structure:")
        print("  dataset/train/o/ - organic waste")
        print("  dataset/train/r/ - inorganic waste")
        exit(1)

    # Data loaders with optimized settings
    batch_size = 32  # Larger batch size for MobileNet
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=0)

    # Choose model
    print("\n🤖 Initializing model...")
    
    # For faster training on CPU, use Light model
    if device == 'cpu':
        print("   Using MobileNetV3 Small (optimized for CPU)")
        model = WasteClassifierLight(num_classes=2).to(device)
    else:
        print("   Using MobileNetV2 (balanced speed/accuracy)")
        model = WasteClassifierMobileNet(num_classes=2).to(device)
    
    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"   Total parameters: {total_params:,}")
    print(f"   Trainable parameters: {trainable_params:,}")

    # Optimizer with higher learning rate
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)  # Higher LR for MobileNet
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=2, factor=0.5)

    # Training loop with early stopping
    num_epochs = 20  # Fewer epochs for MobileNet
    best_val_acc = 0
    train_losses = []
    val_losses = []
    train_accs = []
    val_accs = []
    patience = 5
    patience_counter = 0

    print("\n🚀 Starting training...")
    print("=" * 60)
    start_time = time.time()
    
    for epoch in range(num_epochs):
        epoch_start = time.time()
        
        print(f"\n📈 Epoch {epoch+1}/{num_epochs}")
        print("-" * 50)
        
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer)
        val_loss, val_acc, _, _ = validate(model, val_loader, criterion)
        
        epoch_time = time.time() - epoch_start
        
        train_losses.append(train_loss)
        val_losses.append(val_loss)
        train_accs.append(train_acc)
        val_accs.append(val_acc)
        
        print(f"   Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
        print(f"   Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.2f}%")
        print(f"   Time: {epoch_time:.1f}s")
        
        scheduler.step(val_loss)
        
        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), '../models/best_waste_classifier_mobilenet.pth')
            print(f"   ✓ Saved best model (acc: {val_acc:.2f}%)")
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"\n⏹️  Early stopping at epoch {epoch+1}")
                break
    
    total_time = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"✅ Training completed in {total_time/60:.1f} minutes!")
    print(f"   Best validation accuracy: {best_val_acc:.2f}%")

    # Plot training history
    plt.figure(figsize=(12, 4))
    plt.subplot(1, 2, 1)
    plt.plot(train_losses, label='Train Loss')
    plt.plot(val_losses, label='Val Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.title('Training and Validation Loss')
    plt.grid(True)

    plt.subplot(1, 2, 2)
    plt.plot(train_accs, label='Train Accuracy')
    plt.plot(val_accs, label='Val Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy (%)')
    plt.legend()
    plt.title('Training and Validation Accuracy')
    plt.grid(True)
    plt.savefig('../models/training_history_mobilenet.png')
    plt.show()

    # Test evaluation
    print("\n📊 Evaluating on test set...")
    model.load_state_dict(torch.load('../models/best_waste_classifier_mobilenet.pth'))
    test_loss, test_acc, test_preds, test_labels = validate(model, test_loader, criterion)
    print(f"   Test Accuracy: {test_acc:.2f}%")

    # Classification report
    print("\n📋 Classification Report:")
    print(classification_report(test_labels, test_preds, target_names=['Organik', 'Anorganik']))

    # Save as TorchScript
    model.eval()
    example_input = torch.randn(1, 3, 128, 128).to(device)
    traced_script_module = torch.jit.trace(model, example_input)
    traced_script_module.save("../models/waste_classifier_mobilenet.pt")
    print("\n✓ Model saved for deployment!")
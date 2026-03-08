import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
import time
import os

# 1. HARDWARE CHECK
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Training on device: {device}")

# 2. DATA AUGMENTATION & PREPROCESSING
# We resize to 224x224 because that is what EfficientNet-B0 expects.
data_transforms = {
    'train': transforms.Compose([
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    'val': transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
}

# 3. LOAD DATASET (Food-101)
train_dataset = datasets.Food101(root='./data', split='train', download=True, transform=data_transforms['train'])
val_dataset = datasets.Food101(root='./data', split='test', download=True, transform=data_transforms['val'])

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, num_workers=2)
val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False, num_workers=2)

# 4. LOAD PRE-TRAINED EFFICIENTNET-B0
# We use weights from ImageNet (General knowledge of shapes/colors)
model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)

# 5. MODIFY THE FINAL LAYER (The "Fine-Tuning" Step)
# EfficientNet-B0 ends with 1280 features. We map those to our 101 food classes.
num_ftrs = model.classifier[1].in_features
model.classifier[1] = nn.Linear(num_ftrs, 101)
model = model.to(device)

# 6. DEFINE LOSS & OPTIMIZER
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 7. TRAINING LOOP
def train_model(epochs=10):
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            
        print(f"Epoch {epoch+1}/{epochs} - Loss: {running_loss/len(train_loader):.4f}")

# Start the training
train_model(epochs=10)

# 8. SAVE THE MODEL FOR FLASK BACKEND
torch.save(model.state_dict(), 'food_model_efficientnet.pth')
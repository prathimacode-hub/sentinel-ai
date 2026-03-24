import os
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------
DATA_DIR = "../dataset/images"
MODEL_DIR = "../models/classifier"
BATCH_SIZE = 16
EPOCHS = 5
LR = 0.001

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

os.makedirs(MODEL_DIR, exist_ok=True)

CLASSES = [
    "normal",
    "phone_usage",
    "multiple_faces",
    "no_face",
    "looking_away",
    "book_usage",
    "impersonation",
    "obstruction",
    "audio_cheating",
    "tab_switch"
]


# -----------------------------
# DATA TRANSFORMS
# -----------------------------
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])


# -----------------------------
# LOAD DATASET
# -----------------------------
dataset = datasets.ImageFolder(DATA_DIR, transform=transform)
dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

print("📊 Dataset size:", len(dataset))


# -----------------------------
# MODEL (TRANSFER LEARNING)
# -----------------------------
model = models.resnet18(pretrained=True)

# Modify final layer
model.fc = nn.Linear(model.fc.in_features, len(CLASSES))

model = model.to(DEVICE)


# -----------------------------
# LOSS + OPTIMIZER
# -----------------------------
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LR)


# -----------------------------
# TRAINING LOOP
# -----------------------------
def train():
    model.train()

    for epoch in range(EPOCHS):
        running_loss = 0.0
        correct = 0

        for images, labels in dataloader:
            images = images.to(DEVICE)
            labels = labels.to(DEVICE)

            optimizer.zero_grad()

            outputs = model(images)
            loss = criterion(outputs, labels)

            loss.backward()
            optimizer.step()

            running_loss += loss.item()

            _, preds = torch.max(outputs, 1)
            correct += (preds == labels).sum().item()

        acc = correct / len(dataset)

        print(f"Epoch {epoch+1}/{EPOCHS} | Loss: {running_loss:.4f} | Accuracy: {acc:.4f}")


# -----------------------------
# SAVE MODEL
# -----------------------------
def save_model():
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(MODEL_DIR, f"model_{timestamp}.pth")

    torch.save(model.state_dict(), path)

    print("✅ Model saved at:", path)


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    train()
    save_model()

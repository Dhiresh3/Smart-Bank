"""
animal.py — 8-Layer CNN Animal Classifier (Built from Scratch)
================================================================
USAGE
-----
1.  Set DATA_DIR below to your dataset root (must contain train/ and test/ subfolders,
    each organised as one subfolder per class, e.g. train/cat/, train/dog/ …)
2.  Run: python animal.py --mode train
3.  Predict: python animal.py --mode predict --image path/to/photo.jpg

Architecture (8 learnable layers)
-----------------------------------
Conv1 → BN → ReLU → MaxPool
Conv2 → BN → ReLU → MaxPool
Conv3 → BN → ReLU
Conv4 → BN → ReLU → MaxPool
FC1   → BN → ReLU → Dropout
FC2   → BN → ReLU → Dropout
FC3   (output)
"""
import os
import sys
import argparse
import json
import time
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ─────────────────────────────────────────────
#  ⚙  CONFIGURATION  — edit these paths
# ─────────────────────────────────────────────
DATA_DIR   = r"C:\Users\dhire\Downloads\data-20260326T180557Z-3-001\data"
TRAIN_DIR  = os.path.join(DATA_DIR, "train")
TEST_DIR   = os.path.join(DATA_DIR, "test")

MODEL_PATH = os.path.join(os.path.dirname(__file__), "animal_cnn.pth")
META_PATH  = os.path.join(os.path.dirname(__file__), "animal_classes.json")

# Hyper-parameters
IMG_SIZE    = 128        # resize all images to 128×128
BATCH_SIZE  = 32
EPOCHS      = 30
LR          = 1e-3
WEIGHT_DECAY= 1e-4
NUM_WORKERS = 2         

# ─────────────────────────────────────────────
#  🧠  8-LAYER CNN MODEL
# ─────────────────────────────────────────────
class AnimalCNN(nn.Module):
    """
    8 trainable layers:
        4 convolutional layers  (feature extraction)
        3 fully-connected layers (classification)
    Total learnable weight tensors: 8 (Conv×4 + FC×3 + output FC = 8)
    """

    def __init__(self, num_classes: int):
        super().__init__()

        # ── Convolutional Block 1 (Layer 1) ──
        self.conv1 = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),   # Layer 1
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),                            # 128→64
        )

        # ── Convolutional Block 2 (Layer 2) ──
        self.conv2 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, padding=1),  # Layer 2
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),                            # 64→32
        )

        # ── Convolutional Block 3 (Layer 3) ──
        self.conv3 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=3, padding=1), # Layer 3
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
        )

        # ── Convolutional Block 4 (Layer 4) ──
        self.conv4 = nn.Sequential(
            nn.Conv2d(128, 256, kernel_size=3, padding=1),# Layer 4
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),                            # 32→16
        )

        self.global_avg_pool = nn.AdaptiveAvgPool2d((4, 4))  # fixed to 4×4

        # ── Fully-Connected Block ──
        self.fc1 = nn.Sequential(                          # Layer 5
            nn.Linear(256 * 4 * 4, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
        )
        self.fc2 = nn.Sequential(                          # Layer 6
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.4),
        )
        self.fc3 = nn.Linear(256, num_classes)             # Layer 7 (output)

        self._init_weights()

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, nonlinearity="relu")
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                nn.init.zeros_(m.bias)

    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x = self.conv4(x)
        x = self.global_avg_pool(x)
        x = x.view(x.size(0), -1)   # flatten
        x = self.fc1(x)
        x = self.fc2(x)
        x = self.fc3(x)
        return x


# ─────────────────────────────────────────────
#  📦  DATA LOADING
# ─────────────────────────────────────────────
def get_transforms():
    train_tf = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3),
        transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std =[0.229, 0.224, 0.225]),
    ])
    val_tf = transforms.Compose([
        transforms.Resize((IMG_SIZE, IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std =[0.229, 0.224, 0.225]),
    ])
    return train_tf, val_tf


def get_loaders():
    train_tf, val_tf = get_transforms()
    train_ds = datasets.ImageFolder(TRAIN_DIR, transform=train_tf)
    test_ds  = datasets.ImageFolder(TEST_DIR,  transform=val_tf)

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE,
                              shuffle=True, num_workers=NUM_WORKERS,
                              pin_memory=True)
    test_loader  = DataLoader(test_ds,  batch_size=BATCH_SIZE,
                              shuffle=False, num_workers=NUM_WORKERS,
                              pin_memory=True)
    return train_loader, test_loader, train_ds.classes


# ─────────────────────────────────────────────
#  🏋  TRAINING
# ─────────────────────────────────────────────
def train():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n🖥  Device: {device}")

    train_loader, test_loader, classes = get_loaders()
    num_classes = len(classes)
    print(f"🐾  Classes ({num_classes}): {classes}\n")

    # Save class names
    with open(META_PATH, "w") as f:
        json.dump(classes, f)

    model = AnimalCNN(num_classes).to(device)
    total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"📐  Trainable parameters: {total_params:,}\n")

    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    optimizer = optim.AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)

    history = {"train_loss": [], "train_acc": [], "test_loss": [], "test_acc": []}
    best_acc  = 0.0
    start_epoch = 1

    # ── Resume from checkpoint if available ──
    if os.path.exists(MODEL_PATH):
        print(f"🔄  Resuming from checkpoint: {MODEL_PATH}")
        checkpoint = torch.load(MODEL_PATH, map_location=device)
        model.load_state_dict(checkpoint["model_state_dict"])
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        best_acc    = checkpoint.get("best_acc", 0.0)
        start_epoch = checkpoint.get("epoch", 0) + 1
        # Fast-forward scheduler to correct state
        for _ in range(start_epoch - 1):
            scheduler.step()
        print(f"   ↳ Continuing from epoch {start_epoch} (best acc so far: {best_acc:.2f}%)\n")

    for epoch in range(start_epoch, EPOCHS + 1):
        # ── Train phase ──
        model.train()
        running_loss, correct, total = 0.0, 0, 0
        t0 = time.time()

        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            correct += predicted.eq(labels).sum().item()
            total   += labels.size(0)

        train_loss = running_loss / total
        train_acc  = 100.0 * correct / total

        # ── Eval phase ──
        model.eval()
        val_loss, val_correct, val_total = 0.0, 0, 0
        with torch.no_grad():
            for images, labels in test_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                val_loss    += loss.item() * images.size(0)
                _, predicted = outputs.max(1)
                val_correct += predicted.eq(labels).sum().item()
                val_total   += labels.size(0)

        test_loss = val_loss / val_total
        test_acc  = 100.0 * val_correct / val_total
        scheduler.step()

        history["train_loss"].append(train_loss)
        history["train_acc"].append(train_acc)
        history["test_loss"].append(test_loss)
        history["test_acc"].append(test_acc)

        elapsed = time.time() - t0
        print(f"Epoch [{epoch:02d}/{EPOCHS}] | "
              f"Train Loss: {train_loss:.4f} Acc: {train_acc:.2f}% | "
              f"Test Loss: {test_loss:.4f} Acc: {test_acc:.2f}% | "
              f"⏱ {elapsed:.1f}s")

        # Save best model
        if test_acc > best_acc:
            best_acc = test_acc
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "best_acc": best_acc,
                "classes": classes,
                "num_classes": num_classes,
            }, MODEL_PATH)
            print(f"   ✅ Best model saved (acc={best_acc:.2f}%)")

    print(f"\n🏆  Training complete. Best test accuracy: {best_acc:.2f}%")
    _plot_history(history)


def _plot_history(history):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    ax1.plot(history["train_loss"], label="Train Loss", color="#4C72B0")
    ax1.plot(history["test_loss"],  label="Test Loss",  color="#DD8452")
    ax1.set_title("Loss Curve"); ax1.set_xlabel("Epoch"); ax1.legend()

    ax2.plot(history["train_acc"], label="Train Acc", color="#4C72B0")
    ax2.plot(history["test_acc"],  label="Test Acc",  color="#DD8452")
    ax2.set_title("Accuracy Curve"); ax2.set_xlabel("Epoch"); ax2.legend()

    plt.tight_layout()
    plot_path = os.path.join(os.path.dirname(__file__), "training_curves.png")
    plt.savefig(plot_path, dpi=150)
    print(f"📊  Training curves saved → {plot_path}")
    plt.show()


# ─────────────────────────────────────────────
#  🔍  PREDICTION
# ─────────────────────────────────────────────

# Minimum confidence required to accept a prediction as a known animal.
# If top-1 confidence is BELOW this value the image is rejected as
# "not a known animal from the dataset".
CONFIDENCE_THRESHOLD = 60.0   # percent (0-100)

def predict(image_path: str):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if not os.path.exists(MODEL_PATH):
        sys.exit("❌  No trained model found. Run with --mode train first.")
    if not os.path.exists(META_PATH):
        sys.exit("❌  Class metadata not found. Re-train the model.")

    with open(META_PATH) as f:
        classes = json.load(f)

    checkpoint = torch.load(MODEL_PATH, map_location=device)
    model = AnimalCNN(len(classes)).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    _, val_tf = get_transforms()
    img = Image.open(image_path).convert("RGB")
    tensor = val_tf(img).unsqueeze(0).to(device)

    with torch.no_grad():
        logits = model(tensor)
        probs  = torch.softmax(logits, dim=1).squeeze().cpu().numpy()

    top5_idx   = np.argsort(probs)[::-1][:5]
    top5_names = [classes[i] for i in top5_idx]
    top5_probs = [probs[i]   for i in top5_idx]

    pred_class = top5_names[0]
    confidence = top5_probs[0] * 100

    # ── Out-of-distribution check ──────────────────────────────────────
    if confidence < CONFIDENCE_THRESHOLD:
        print("\n⚠️  UNKNOWN IMAGE")
        print("─" * 40)
        print(f"   The model could not confidently identify any known animal.")
        print(f"   Best guess: {pred_class} ({confidence:.1f}%) — below threshold ({CONFIDENCE_THRESHOLD:.0f}%)")
        print("   Please upload an image of one of these animals:")
        print("   " + ", ".join(classes))
        _show_unknown(img, classes, confidence)
        return None, confidence
    # ───────────────────────────────────────────────────────────────────

    print(f"\n🐾  Prediction: {pred_class.upper()}  ({confidence:.1f}% confidence)")
    print("─" * 40)
    for name, prob in zip(top5_names, top5_probs):
        bar = "█" * int(prob * 30)
        print(f"  {name:<20} {prob*100:5.1f}%  {bar}")

    _show_prediction(img, pred_class, confidence, top5_names, top5_probs)
    return pred_class, confidence


def _show_prediction(img, pred_class, confidence, top5_names, top5_probs):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    ax1.imshow(img)
    ax1.axis("off")
    color = "#2ecc71" if confidence > 70 else "#e67e22" if confidence > 40 else "#e74c3c"
    ax1.set_title(f"Prediction: {pred_class.upper()}\n{confidence:.1f}% confidence",
                  fontsize=13, fontweight="bold", color=color)

    colors = [color] + ["#95a5a6"] * 4
    bars = ax2.barh(top5_names[::-1], [p * 100 for p in top5_probs[::-1]],
                    color=colors[::-1])
    ax2.set_xlabel("Confidence (%)")
    ax2.set_title("Top-5 Predictions")
    ax2.set_xlim(0, 100)
    for bar, prob in zip(bars, top5_probs[::-1]):
        ax2.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                 f"{prob*100:.1f}%", va="center", fontsize=9)

    plt.tight_layout()
    plt.show()


def _show_unknown(img, classes, best_confidence):
    """Popup shown when an image does not match any known animal."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    ax1.imshow(img)
    ax1.axis("off")
    ax1.set_title(
        "⚠️  Unknown / Out-of-Dataset Image\n"
        f"Best confidence only {best_confidence:.1f}% — not reliable",
        fontsize=11, fontweight="bold", color="#e74c3c"
    )

    # Show the supported classes as a neat list
    ax2.axis("off")
    ax2.set_title("Supported Animal Classes", fontsize=13, fontweight="bold")
    text = "\n".join(f"  🐾  {c}" for c in sorted(classes))
    ax2.text(
        0.05, 0.95, text,
        va="top", ha="left", fontsize=10,
        transform=ax2.transAxes,
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#fdecea", edgecolor="#e74c3c")
    )

    fig.suptitle(
        "❌  We cannot detect objects or animals outside our dataset.",
        fontsize=11, color="#c0392b", y=1.02
    )
    plt.tight_layout()
    plt.show()


# ─────────────────────────────────────────────
#  🚀  ENTRY POINT
# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Animal CNN Classifier (from scratch)")
    parser.add_argument("--mode",  choices=["train", "predict"], required=True,
                        help="train: train the model | predict: classify an image")
    parser.add_argument("--image", type=str, default=None,
                        help="Path to image file (required for predict mode)")
    args = parser.parse_args()

    if args.mode == "train":
        if not os.path.isdir(TRAIN_DIR) or not os.path.isdir(TEST_DIR):
            sys.exit(
                f"❌  Dataset folders not found.\n"
                f"   Expected:\n"
                f"     TRAIN: {TRAIN_DIR}\n"
                f"     TEST : {TEST_DIR}\n"
                f"   Please update DATA_DIR at the top of animal.py"
            )
        train()

    elif args.mode == "predict":
        if not args.image:
            sys.exit("❌  Provide --image path/to/image.jpg for predict mode.")
        if not os.path.isfile(args.image):
            sys.exit(f"❌  Image not found: {args.image}")
        predict(args.image)


if __name__ == "__main__":
    main()

"""
SağlıkCebim - Data Augmentation Pipeline
Eğitim ve inference için görüntü dönüşümleri.
V2: Güçlendirilmiş augmentation — daha iyi genelleme için.
"""

from torchvision import transforms


def get_train_transforms(image_size=224, config=None):
    """Eğitim seti için augmentation pipeline."""
    cfg = config or {}
    aug = cfg.get("augmentation", {})
    norm = aug.get("normalize", {})
    mean = norm.get("mean", [0.485, 0.456, 0.406])
    std = norm.get("std", [0.229, 0.224, 0.225])

    strength = aug.get("strength", "normal")

    if strength == "strong":
        return transforms.Compose([
            transforms.Resize((image_size + 32, image_size + 32)),
            transforms.RandomCrop(image_size),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomAffine(
                degrees=15,
                translate=(0.1, 0.1),
                scale=(0.85, 1.15),
                shear=10,
            ),
            transforms.ColorJitter(
                brightness=0.2,
                contrast=0.2,
                saturation=0.1,
            ),
            transforms.RandomAutocontrast(p=0.3),
            transforms.RandomAdjustSharpness(sharpness_factor=2, p=0.3),
            transforms.GaussianBlur(kernel_size=3, sigma=(0.1, 1.0)),
            transforms.ToTensor(),
            transforms.RandomErasing(p=0.15, scale=(0.02, 0.1)),
            transforms.Normalize(mean=mean, std=std),
        ])
    else:
        return transforms.Compose([
            transforms.Resize((image_size, image_size)),
            transforms.RandomHorizontalFlip(p=aug.get("random_horizontal_flip", 0.5)),
            transforms.RandomRotation(degrees=aug.get("random_rotation", 15)),
            transforms.ColorJitter(
                brightness=aug.get("random_brightness", 0.1),
                contrast=aug.get("random_contrast", 0.1),
            ),
            transforms.ToTensor(),
            transforms.Normalize(mean=mean, std=std),
        ])


def get_val_transforms(image_size=224, config=None):
    """Validasyon/test seti için dönüşümler (augmentation yok)."""
    cfg = config or {}
    norm = cfg.get("augmentation", {}).get("normalize", {})
    mean = norm.get("mean", [0.485, 0.456, 0.406])
    std = norm.get("std", [0.229, 0.224, 0.225])

    return transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=mean, std=std),
    ])


def get_tta_transforms(image_size=224):
    """Test-Time Augmentation: birden fazla varyant üret, tahminleri ortala."""
    mean = [0.485, 0.456, 0.406]
    std = [0.229, 0.224, 0.225]

    base = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=mean, std=std),
    ])

    flipped = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.RandomHorizontalFlip(p=1.0),
        transforms.ToTensor(),
        transforms.Normalize(mean=mean, std=std),
    ])

    crop_center = transforms.Compose([
        transforms.Resize((image_size + 32, image_size + 32)),
        transforms.CenterCrop(image_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=mean, std=std),
    ])

    slight_rotate = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.RandomRotation(degrees=5),
        transforms.ToTensor(),
        transforms.Normalize(mean=mean, std=std),
    ])

    brighter = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ColorJitter(brightness=0.15, contrast=0.15),
        transforms.ToTensor(),
        transforms.Normalize(mean=mean, std=std),
    ])

    return [base, flipped, crop_center, slight_rotate, brighter]


def get_inference_transforms(image_size=224):
    """Tek görüntü inference için dönüşümler."""
    return transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ])

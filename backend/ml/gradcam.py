"""
SağlıkCebim - Grad-CAM Görselleştirme
Modelin görüntünün neresine baktığını gösteren ısı haritası oluşturur.
"""

import numpy as np
import torch
from PIL import Image


class GradCAM:
    """DenseNet-121 için Gradient-weighted Class Activation Mapping."""

    def __init__(self, model):
        self.model = model
        self.model.eval()
        self.gradients = None
        self.activations = None
        self._register_hooks()

    def _register_hooks(self):
        """Son konvolüsyon katmanına hook ekle."""
        # DenseNet-121: features.denseblock4 son konvolüsyon bloğu
        target_layer = self.model.features[-1]

        def forward_hook(module, input, output):
            self.activations = output.clone().detach()

        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0].clone().detach()

        target_layer.register_forward_hook(forward_hook)
        target_layer.register_full_backward_hook(backward_hook)

    def generate(self, input_tensor, class_idx):
        """
        Belirli bir sınıf için Grad-CAM haritası oluştur.

        Args:
            input_tensor: [1, 3, 224, 224] boyutunda tensor
            class_idx: Hedef sınıf indeksi (0-13)

        Returns:
            cam: [224, 224] numpy array (0-1 arası normalize)
        """
        self.model.zero_grad()
        input_tensor = input_tensor.clone().requires_grad_(True)
        output = self.model(input_tensor)

        target = output[0, class_idx]
        target.backward(retain_graph=True)

        # Global average pooling of gradients
        weights = self.gradients.mean(dim=[2, 3], keepdim=True)

        # Weighted combination of activation maps
        cam = (weights * self.activations).sum(dim=1, keepdim=True)
        cam = torch.relu(cam)
        cam = cam.squeeze().cpu().numpy()

        # Normalize 0-1
        if cam.max() > 0:
            cam = cam / cam.max()

        # Resize to input size
        cam_pil = Image.fromarray((cam * 255).astype(np.uint8))
        cam_pil = cam_pil.resize((224, 224), Image.BILINEAR)
        cam = np.array(cam_pil).astype(np.float32) / 255.0

        return cam


def create_heatmap_overlay(original_image, cam, alpha=0.4):
    """
    Orijinal görüntü üzerine Grad-CAM ısı haritası bindir.

    Args:
        original_image: PIL Image (orijinal boyut)
        cam: numpy array [H, W] (0-1)
        alpha: Overlay şeffaflığı

    Returns:
        PIL Image: Heatmap overlay edilmiş görüntü
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.cm as cm

    # CAM'i orijinal görüntü boyutuna resize et
    cam_resized = np.array(
        Image.fromarray((cam * 255).astype(np.uint8)).resize(
            original_image.size, Image.BILINEAR
        )
    ).astype(np.float32) / 255.0

    # Jet colormap uygula
    colormap = cm.jet(cam_resized)[:, :, :3]
    colormap = (colormap * 255).astype(np.uint8)
    heatmap = Image.fromarray(colormap)

    # Orijinal görüntüyü RGB'ye çevir
    if original_image.mode != "RGB":
        original_image = original_image.convert("RGB")

    # Overlay
    overlay = Image.blend(original_image, heatmap, alpha=alpha)
    return overlay

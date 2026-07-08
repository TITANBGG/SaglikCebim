"""
SağlıkCebim - Model Export
Eğitilmiş modeli ONNX formatına çevirme (hızlı inference için).

Kullanım:
    python export_model.py --model ../models/chestxray_best.pt
"""

import argparse
import logging

import torch
import torch.nn as nn
from torchvision import models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def export_to_onnx(checkpoint_path, output_path=None):
    """PyTorch modelini ONNX formatına çevir."""
    checkpoint = torch.load(checkpoint_path, map_location="cpu")
    config = checkpoint["config"]
    model_cfg = config["model"]

    model = models.densenet121(weights=None)
    in_features = model.classifier.in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=model_cfg["dropout"]),
        nn.Linear(in_features, model_cfg["num_classes"]),
    )
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    dummy_input = torch.randn(1, 3, 224, 224)

    if output_path is None:
        output_path = checkpoint_path.replace(".pt", ".onnx")

    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        opset_version=17,
        input_names=["image"],
        output_names=["predictions"],
        dynamic_axes={
            "image": {0: "batch_size"},
            "predictions": {0: "batch_size"},
        },
    )
    logger.info(f"ONNX model kaydedildi: {output_path}")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=True)
    parser.add_argument("--output", type=str, default=None)
    args = parser.parse_args()
    export_to_onnx(args.model, args.output)

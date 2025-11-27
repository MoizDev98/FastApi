# app/utils/modelo.py
from pathlib import Path
from typing import Tuple

from PIL import Image
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import torchvision.models as models


DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# El archivo .pth debe estar en esta misma carpeta
MODEL_PATH = Path(__file__).parent / "modelo_mejor.pth"

# Etiquetas de las 14 patologías (ajusta si tu modelo tiene otra cosa)
ETIQUETAS = {
    0: "Atelectasis",
    1: "Cardiomegaly",
    2: "Consolidation",
    3: "Edema",
    4: "Effusion",
    5: "Emphysema",
    6: "Fibrosis",
    7: "Hernia",
    8: "Infiltration",
    9: "Mass",
    10: "Nodule",
    11: "Pleural Thickening",
    12: "Pneumonia",
    13: "Pneumothorax",
}

transform = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ]
)

# Usaremos un único objeto global para el modelo
_model: torch.nn.Module | None = None


def cargar_modelo() -> torch.nn.Module:
    """
    Carga el modelo ResNet50 afinado con tus pesos .pth.
    La arquitectura aquí debe ser EXACTAMENTE la misma que usaste al entrenar.
    """
    global _model
    if _model is None:
        try:
            # 1. Crear el mismo modelo que en el entrenamiento
            model = models.resnet50(weights=None)  # o pretrained=False
            num_ftrs = model.fc.in_features
            model.fc = nn.Linear(num_ftrs, len(ETIQUETAS))

            # 2. Cargar el checkpoint
            checkpoint = torch.load(MODEL_PATH, map_location=DEVICE)

            # Si guardaste solo state_dict
            if isinstance(checkpoint, dict) and "model_state_dict" in checkpoint:
                state_dict = checkpoint["model_state_dict"]
            else:
                state_dict = checkpoint

            # 3. Cargar los pesos
            model.load_state_dict(state_dict)  # aquí ya no habrá "base." ni nada raro

            model.to(DEVICE)
            model.eval()

            _model = model
            print(f"✓ Modelo IA cargado desde {MODEL_PATH}")
        except Exception as e:
            print(f"✗ Error al cargar el modelo: {e}")
            raise
    return _model


def predecir_imagen(pil_image: Image.Image) -> Tuple[str, float]:
    """
    Recibe una imagen PIL RGB y devuelve (diagnóstico, probabilidad_top1)
    """
    model = cargar_modelo()

    img_tensor = transform(pil_image.convert("RGB"))
    img_tensor = img_tensor.unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        outputs = model(img_tensor)
        probs = torch.softmax(outputs, dim=1)
        conf, pred = torch.max(probs, 1)

    clase = pred.item()
    prob = conf.item()
    diagnostico = ETIQUETAS.get(clase, f"Clase {clase}")
    return diagnostico, prob


# Precarga opcional
try:
    cargar_modelo()
except Exception as e:
    print(f"Advertencia: no se pudo precargar el modelo IA: {e}")

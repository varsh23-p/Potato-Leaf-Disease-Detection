"""Core logic of the Potato Leaf Disease Detection system (version 2 - leaf check added, fixes D01)."""
import io
import numpy as np
from PIL import Image

ALLOWED_EXT = {"jpg", "jpeg", "png"}
MAX_BYTES = 5 * 1024 * 1024        # 5 MB
MIN_SIDE = 32                      # pixels
IMG_SIZE = (128, 128)              # same input size as the Lab 8 model
CONF_THRESHOLD = 0.60
MIN_LEAF_RATIO = 0.30             # share of plant-coloured pixels required
CLASS_NAMES = ["Potato___Early_blight", "Potato___Late_blight", "Potato___healthy"]
DISPLAY = {
    "Potato___Early_blight": "Early Blight",
    "Potato___Late_blight": "Late Blight",
    "Potato___healthy": "Healthy",
}
ADVICE = {
    "Early Blight": "Remove infected leaves and apply a recommended fungicide; avoid overhead watering.",
    "Late Blight": "Isolate or destroy infected plants immediately and apply a late-blight fungicide.",
    "Healthy": "No disease detected. Continue regular monitoring and good field hygiene.",
    "Uncertain": "Model confidence is low. Upload a clearer leaf photo or consult an agronomist.",
}


def validate_upload(filename, data):
    """FR2/FR4: return (ok, message) for an uploaded file."""
    if not filename:
        return False, "No file selected"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXT:
        return False, "Unsupported file type. Use JPG or PNG"
    if len(data) == 0:
        return False, "Empty file"
    if len(data) > MAX_BYTES:
        return False, "File too large (max 5 MB)"
    try:
        img = Image.open(io.BytesIO(data))
        img.verify()
        img = Image.open(io.BytesIO(data))
    except Exception:
        return False, "Corrupted or unreadable image"
    if img.width < MIN_SIDE or img.height < MIN_SIDE:
        return False, "Image too small (minimum 32x32 pixels)"
    return True, "OK"


def preprocess_image(data):
    """FR3: decode, convert to RGB, resize to 128x128 -> array (1,128,128,3)."""
    img = Image.open(io.BytesIO(data)).convert("RGB").resize(IMG_SIZE)
    return np.asarray(img, dtype=np.float32)[np.newaxis, ...]


def predict_disease(model, arr):
    """FR3/FR5: run model, apply confidence threshold, return result dict."""
    probs = np.asarray(model.predict(arr, verbose=0))[0]
    idx = int(np.argmax(probs))
    conf = float(probs[idx])
    if conf < CONF_THRESHOLD:
        return {"label": "Uncertain", "confidence": conf}
    return {"label": DISPLAY[CLASS_NAMES[idx]], "confidence": conf}


def is_leaf_image(arr, min_ratio=MIN_LEAF_RATIO):
    """FR4 (added to fix D01): True if enough pixels are plant-coloured (green/yellow/brown-green).
    A pixel counts as plant-coloured when green is the strongest channel and not very dark."""
    img = np.asarray(arr[0] if arr.ndim == 4 else arr, dtype=np.float32)
    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    plant = (g >= r * 0.9) & (g > b * 1.15) & (g > 50)
    return float(np.mean(plant)) >= min_ratio


def get_advice(label):
    """FR6: treatment advice text for a predicted label."""
    return ADVICE.get(label, "No advice available")


def analyze_image(model, filename, data):
    """Full pipeline used by the web layer: validate -> preprocess -> predict -> advice."""
    ok, msg = validate_upload(filename, data)
    if not ok:
        return {"ok": False, "error": msg}
    arr = preprocess_image(data)
    if not is_leaf_image(arr):
        return {"ok": False, "error": "Not a potato leaf image. Please upload a clear leaf photo"}
    res = predict_disease(model, arr)
    res.update({"ok": True, "advice": get_advice(res["label"])})
    return res

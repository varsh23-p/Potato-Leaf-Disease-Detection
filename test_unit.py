import numpy as np
from leaf_app.core import (validate_upload, preprocess_image, predict_disease, get_advice, is_leaf_image)
from leaf_app.history import PredictionHistory
from leaf_app.stub_model import StubLeafModel
from helpers import make_leaf, make_image


class FixedModel:
    def __init__(self, probs): self.p = probs
    def predict(self, x, verbose=0): return np.array([self.p], dtype=np.float32)


# ---- validate_upload() ----
def test_UT01_validate_accepts_valid_png(log):
    r = validate_upload("leaf.png", make_leaf("healthy"))
    log("UT01", "validate_upload", "Unit", "leaf.png, valid 200x200 PNG", "(True, 'OK')", r)
    assert r == (True, "OK")

def test_UT02_validate_rejects_txt(log):
    r = validate_upload("notes.txt", b"hello")
    log("UT02", "validate_upload", "Unit", "notes.txt", "(False, 'Unsupported file type. Use JPG or PNG')", r)
    assert r == (False, "Unsupported file type. Use JPG or PNG")

def test_UT03_validate_rejects_empty_file(log):
    r = validate_upload("leaf.png", b"")
    log("UT03", "validate_upload", "Unit", "leaf.png, 0 bytes", "(False, 'Empty file')", r)
    assert r == (False, "Empty file")

# ---- preprocess_image() ----
def test_UT04_preprocess_shape(log):
    a = preprocess_image(make_leaf("healthy", (300, 220)))
    log("UT04", "preprocess_image", "Unit", "300x220 PNG", "shape (1,128,128,3)", a.shape)
    assert a.shape == (1, 128, 128, 3)

def test_UT05_preprocess_value_range_and_rgba(log):
    a = preprocess_image(make_image((64, 64)))      # RGB source
    ok = (a.dtype == np.float32) and (a.min() >= 0) and (a.max() <= 255)
    log("UT05", "preprocess_image", "Unit", "64x64 PNG", "float32 values within 0-255", f"dtype={a.dtype}, min={a.min()}, max={a.max()}")
    assert ok

# ---- predict_disease() ----
def test_UT06_predict_early_blight(log):
    r = predict_disease(FixedModel([0.80, 0.15, 0.05]), np.zeros((1, 128, 128, 3)))
    log("UT06", "predict_disease", "Unit", "probs [0.80,0.15,0.05]", "Early Blight", r["label"])
    assert r["label"] == "Early Blight"

def test_UT07_predict_uncertain_when_low_confidence(log):
    r = predict_disease(FixedModel([0.40, 0.35, 0.25]), np.zeros((1, 128, 128, 3)))
    log("UT07", "predict_disease", "Unit", "probs [0.40,0.35,0.25]", "Uncertain", r["label"])
    assert r["label"] == "Uncertain"

# ---- get_advice() ----
def test_UT08_advice_for_healthy(log):
    r = get_advice("Healthy")
    log("UT08", "get_advice", "Unit", "label = Healthy", "text containing 'No disease detected'", r)
    assert "No disease detected" in r

def test_UT09_advice_for_unknown_label(log):
    r = get_advice("Rust")
    log("UT09", "get_advice", "Unit", "label = Rust (unknown)", "No advice available", r)
    assert r == "No advice available"

# ---- PredictionHistory ----
def test_UT10_history_add_and_count(log):
    h = PredictionHistory(); h.add("a.png", "Healthy", 0.92)
    log("UT10", "PredictionHistory.add", "Unit", "add 1 record", "count = 1", h.count())
    assert h.count() == 1

def test_UT11_history_clear(log):
    h = PredictionHistory(); h.add("a.png", "Healthy", 0.92); h.clear()
    log("UT11", "PredictionHistory.clear", "Unit", "add 1 then clear", "count = 0", h.count())
    assert h.count() == 0

# ---- is_leaf_image() (added together with the fix for D01) ----
def test_UT12_leaf_check_accepts_leaf(log):
    r = is_leaf_image(preprocess_image(make_leaf("early")))
    log("UT12", "is_leaf_image", "Unit", "early-blight leaf image", "True", r)
    assert r is True

def test_UT13_leaf_check_rejects_non_leaf(log):
    from helpers import make_non_leaf
    r = is_leaf_image(preprocess_image(make_non_leaf()))
    log("UT13", "is_leaf_image", "Unit", "dark non-leaf image", "False", r)
    assert r is False

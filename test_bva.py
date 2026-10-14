import numpy as np
import pytest
from leaf_app.core import validate_upload, predict_disease, MAX_BYTES
from helpers import make_image, pad_to

# Boundary 1: minimum image side = 32 px
BVA_DIM = [("BVA01", 31, False), ("BVA02", 32, True), ("BVA03", 33, True)]

@pytest.mark.parametrize("tid,side,expected", BVA_DIM, ids=[x[0] for x in BVA_DIM])
def test_bva_min_dimension(log, tid, side, expected):
    ok, msg = validate_upload("leaf.png", make_image((side, side)))
    log(tid, "validate_upload (min size)", "BVA", f"{side}x{side} px", "Valid" if expected else "Invalid", f"{'Valid' if ok else 'Invalid'} ({msg})")
    assert ok == expected

# Boundary 2: maximum file size = 5 MB (5,242,880 bytes)
BVA_SIZE = [("BVA04", MAX_BYTES - 1, True), ("BVA05", MAX_BYTES, True), ("BVA06", MAX_BYTES + 1, False)]

@pytest.mark.parametrize("tid,nbytes,expected", BVA_SIZE, ids=[x[0] for x in BVA_SIZE])
def test_bva_max_file_size(log, tid, nbytes, expected):
    ok, msg = validate_upload("leaf.png", pad_to(make_image((100, 100)), nbytes))
    log(tid, "validate_upload (max size)", "BVA", f"{nbytes} bytes", "Valid" if expected else "Invalid", f"{'Valid' if ok else 'Invalid'} ({msg})")
    assert ok == expected

# Boundary 3: confidence threshold = 0.60
class FixedModel:
    def __init__(self, top): self.top = top
    def predict(self, x, verbose=0):
        rest = (1 - self.top) / 2
        return np.array([[self.top, rest, rest]], dtype=np.float32)

BVA_CONF = [("BVA07", 0.59, "Uncertain"), ("BVA08", 0.60, "Early Blight"), ("BVA09", 0.61, "Early Blight")]

@pytest.mark.parametrize("tid,top,expected", BVA_CONF, ids=[x[0] for x in BVA_CONF])
def test_bva_confidence_threshold(log, tid, top, expected):
    r = predict_disease(FixedModel(top), np.zeros((1, 128, 128, 3)))
    log(tid, "predict_disease (threshold)", "BVA", f"top-class confidence = {top:.2f}", expected, r["label"])
    assert r["label"] == expected

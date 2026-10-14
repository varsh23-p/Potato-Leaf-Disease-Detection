from leaf_app.core import analyze_image
from leaf_app.history import PredictionHistory
from leaf_app.stub_model import StubLeafModel
from leaf_app.web import create_app
from helpers import make_leaf


def test_IT01_validate_preprocess_predict(log):
    r = analyze_image(StubLeafModel(), "e.png", make_leaf("early"))
    log("IT01", "Validate + Preprocess + Predict", "Integration", "early-blight leaf PNG", "label = Early Blight", r.get("label"))
    assert r["label"] == "Early Blight"

def test_IT02_predict_plus_advice(log):
    r = analyze_image(StubLeafModel(), "l.png", make_leaf("late"))
    log("IT02", "Predict + Advice", "Integration", "late-blight leaf PNG", "label = Late Blight and advice mentions 'late-blight'", f"{r.get('label')} | {r.get('advice')}")
    assert r["label"] == "Late Blight" and "late-blight" in r["advice"]

def test_IT03_web_predict_saves_history(log):
    app = create_app(model=StubLeafModel(), history=PredictionHistory())
    c = app.test_client()
    import io
    c.post("/predict", data={"leaf_image": (io.BytesIO(make_leaf("healthy")), "h.png")}, content_type="multipart/form-data")
    n = app.history.count()
    log("IT03", "Web /predict + History", "Integration", "upload h.png", "history count = 1", n)
    assert n == 1

def test_IT04_invalid_upload_not_saved(log):
    import io
    app = create_app(model=StubLeafModel(), history=PredictionHistory())
    c = app.test_client()
    resp = c.post("/predict", data={"leaf_image": (io.BytesIO(b"abc"), "x.txt")}, content_type="multipart/form-data")
    n = app.history.count()
    log("IT04", "Web /predict + Validation + History", "Integration", "upload x.txt", "HTTP 400 and history count = 0", f"HTTP {resp.status_code}, count={n}")
    assert resp.status_code == 400 and n == 0

import io
from leaf_app.history import PredictionHistory
from leaf_app.stub_model import StubLeafModel
from leaf_app.web import create_app
from helpers import make_leaf, make_non_leaf


def client():
    app = create_app(model=StubLeafModel(), history=PredictionHistory())
    return app, app.test_client()

def up(c, data, name):
    return c.post("/predict", data={"leaf_image": (io.BytesIO(data), name)}, content_type="multipart/form-data")


def test_ST01_home_page_loads(log):
    app, c = client(); r = c.get("/")
    ok = r.status_code == 200 and b'id="leaf_image"' in r.data and b'id="predict_btn"' in r.data
    log("ST01", "Home page", "System", "GET /", "HTTP 200, upload field and Predict button present", f"HTTP {r.status_code}, elements present={ok}")
    assert ok

def test_ST02_healthy_leaf_flow(log):
    app, c = client(); r = up(c, make_leaf("healthy"), "h.png")
    ok = r.status_code == 200 and b"Healthy" in r.data
    log("ST02", "Normal flow", "System", "upload healthy leaf", "HTTP 200, result 'Healthy' shown", f"HTTP {r.status_code}, 'Healthy' shown={b'Healthy' in r.data}")
    assert ok

def test_ST03_diseased_leaf_flow(log):
    app, c = client(); r = up(c, make_leaf("late"), "l.png")
    ok = r.status_code == 200 and b"Late Blight" in r.data and b"late-blight fungicide" in r.data
    log("ST03", "Normal flow", "System", "upload late-blight leaf", "result 'Late Blight' + treatment advice shown", f"HTTP {r.status_code}, label+advice shown={ok}")
    assert ok

def test_ST04_non_leaf_rejected(log):
    app, c = client(); r = up(c, make_non_leaf(), "object.png")
    ok = r.status_code == 400 and b"Not a potato leaf" in r.data
    log("ST04", "Invalid input handling", "System", "upload dark non-leaf image", "HTTP 400 and message 'Not a potato leaf image'", f"HTTP {r.status_code}, body has disease label={b'Late Blight' in r.data}")
    assert ok

def test_ST05_no_file_selected(log):
    app, c = client(); r = c.post("/predict", data={}, content_type="multipart/form-data")
    ok = r.status_code == 400 and b"No file selected" in r.data
    log("ST05", "Required-field validation", "System", "submit form without a file", "HTTP 400, 'No file selected'", f"HTTP {r.status_code}, message shown={b'No file selected' in r.data}")
    assert ok

def test_ST06_wrong_file_type_message(log):
    app, c = client(); r = up(c, b"hello", "report.pdf")
    ok = r.status_code == 400 and b"Unsupported file type" in r.data
    log("ST06", "Error messages", "System", "upload report.pdf", "HTTP 400, 'Unsupported file type'", f"HTTP {r.status_code}, message shown={b'Unsupported file type' in r.data}")
    assert ok

def test_ST07_history_shows_two_predictions(log):
    app, c = client(); up(c, make_leaf("healthy"), "a.png"); up(c, make_leaf("early", seed=3), "b.png")
    r = c.get("/history")
    ok = b"a.png" in r.data and b"b.png" in r.data and b"Early Blight" in r.data
    log("ST07", "History across functions", "System", "predict a.png, b.png then GET /history", "both records listed", f"both listed={ok}")
    assert ok

def test_ST08_clear_history(log):
    app, c = client(); up(c, make_leaf("healthy"), "a.png")
    c.post("/history/clear"); r = c.get("/history")
    ok = b"No predictions yet" in r.data
    log("ST08", "History", "System", "predict, then Clear history", "'No predictions yet.' shown", f"empty message shown={ok}")
    assert ok

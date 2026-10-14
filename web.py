import base64
from flask import Flask, request, render_template_string, redirect, url_for
from .core import analyze_image
from .history import PredictionHistory
from .stub_model import load_model

PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Potato Leaf Disease Detector</title>
<style>
body{font-family:Arial,Helvetica,sans-serif;background:#f1f6ee;margin:0;color:#1f2d1f}
header{background:#2e7d32;color:#fff;padding:16px 32px;font-size:22px;font-weight:bold}
nav{background:#e3efe0;padding:8px 32px;font-size:14px}
nav a{color:#2e7d32;margin-right:18px;text-decoration:none;font-weight:bold}
main{max-width:760px;margin:24px auto;background:#fff;padding:24px 32px;border-radius:8px;border:1px solid #cfe0cb}
h2{margin-top:0;color:#2e7d32}
input[type=file]{padding:8px;border:1px solid #9bb99a;border-radius:4px;width:58%}
button{background:#2e7d32;color:#fff;border:0;padding:10px 22px;border-radius:4px;font-size:15px}
.err{background:#fdecea;border:1px solid #e57373;color:#b71c1c;padding:10px 14px;border-radius:4px;margin-top:16px}
.res{background:#eef7ec;border:1px solid #81c784;padding:14px 18px;border-radius:4px;margin-top:16px}
.res b{font-size:20px}
table{border-collapse:collapse;width:100%}th,td{border:1px solid #9bb99a;padding:6px 10px;text-align:left}
th{background:#e3efe0}img.thumb{max-width:160px;border:1px solid #9bb99a;margin-top:10px}
</style></head><body>
<header>Potato Leaf Disease Detector</header>
<nav><a id="nav_home" href="/">Home</a><a id="nav_history" href="/history">History</a></nav>
<main>
{% if page == 'home' %}
<h2>Upload a potato leaf image</h2>
<form id="upload_form" method="post" action="/predict" enctype="multipart/form-data">
<input type="file" id="leaf_image" name="leaf_image"> <button id="predict_btn" type="submit">Predict</button>
</form>
{% if error %}<div class="err" id="error_msg">{{ error }}</div>{% endif %}
{% if result %}<div class="res">
<div>Prediction: <b id="result_label">{{ result.label }}</b></div>
<div>Confidence: <span id="confidence">{{ '%.1f'|format(result.confidence*100) }}%</span></div>
<div>Advice: <span id="advice">{{ result.advice }}</span></div>
{% if thumb %}<img class="thumb" src="data:image/png;base64,{{ thumb }}" alt="uploaded leaf">{% endif %}
</div>{% endif %}
{% else %}
<h2>Prediction history</h2>
{% if items %}<table id="history_table"><tr><th>#</th><th>File</th><th>Prediction</th><th>Confidence</th><th>Time</th></tr>
{% for i in items %}<tr><td>{{ loop.index }}</td><td>{{ i.filename }}</td><td>{{ i.label }}</td><td>{{ '%.1f'|format(i.confidence*100) }}%</td><td>{{ i.time }}</td></tr>{% endfor %}
</table>
<form method="post" action="/history/clear" style="margin-top:14px"><button id="clear_btn" type="submit">Clear history</button></form>
{% else %}<p id="empty_msg">No predictions yet.</p>{% endif %}
{% endif %}
</main></body></html>"""


def create_app(model=None, history=None):
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
    app.model = model if model is not None else load_model()
    app.history = history if history is not None else PredictionHistory()

    @app.get("/")
    def home():
        return render_template_string(PAGE, page="home", error=None, result=None, thumb=None)

    @app.post("/predict")
    def predict():
        f = request.files.get("leaf_image")
        name = f.filename if f else ""
        data = f.read() if f else b""
        res = analyze_image(app.model, name, data)
        if not res["ok"]:
            return render_template_string(PAGE, page="home", error=res["error"], result=None, thumb=None), 400
        app.history.add(name, res["label"], res["confidence"])
        thumb = base64.b64encode(data).decode() if name.lower().endswith("png") else None
        return render_template_string(PAGE, page="home", error=None, result=res, thumb=thumb)

    @app.get("/history")
    def history():
        return render_template_string(PAGE, page="history", items=app.history.all())

    @app.post("/history/clear")
    def clear_history():
        app.history.clear()
        return redirect(url_for("history"))

    return app

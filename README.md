# Potato Leaf Disease Detection 

A small Flask web application that lets a user upload a potato leaf photo and get a prediction (**Healthy**, **Early Blight** or **Late Blight**) with a confidence value and treatment advice. The project was built for **Software Testing Laboratory - Experiment 9 (Design, Implement and Test a Software Project)** at NMIMS, Mukesh Patel School of Technology Management & Engineering, Shirpur.

The main goal is **testing**: the app wraps the potato leaf classifier from Experiment 8 and adds input validation, so that bad input (wrong file type, non-leaf images, low confidence) gives a clear message instead of a wrong answer.

## Features

- Upload a leaf image (JPG / JPEG / PNG)
- Upload validation: file selected, allowed type, not empty, max 5 MB, readable image, at least 32 x 32 px
- Pre-processing to 128 x 128 RGB and disease prediction with confidence
- Rejects images that do not look like a leaf
- Reports **Uncertain** when top-class confidence is below 0.60
- Shows treatment advice for the result
- Prediction history page (view and clear)

## Project Structure

```
proj/
├── leaf_app/
│   ├── core.py          # validate_upload, preprocess_image, is_leaf_image, predict_disease, get_advice, analyze_image
│   ├── history.py       # PredictionHistory (add, all, count, clear)
│   ├── stub_model.py    # StubLeafModel (stand-in) and load_model()
│   └── web.py           # Flask routes: /, /predict, /history, /history/clear
├── tests/
│   ├── test_unit.py         # Unit tests
│   ├── test_integration.py  # Integration tests
│   ├── test_system.py       # System tests (HTTP requests)
│   ├── test_ecp.py          # Equivalence Class Partitioning
│   ├── test_bva.py          # Boundary Value Analysis
│   ├── helpers.py, conftest.py
├── selenium_test.py     # Selenium browser tests
├── Jenkinsfile          # Jenkins pipeline
├── run.py               # Starts the app
└── requirements.txt
```

## Getting Started

**Requirements:** Python 3 and pip. Google Chrome is needed only for the Selenium test.

```bash
git clone <your-repo-url>
cd <your-repo-folder>
python -m pip install -r requirements.txt
python run.py
```

Open **http://127.0.0.1:8000** in your browser and upload a leaf image.

### Using the real model (optional)

By default the app uses `StubLeafModel`, a simple colour-based stand-in with the same `predict()` interface as a Keras model. This lets the software around the model be tested quickly without TensorFlow or the dataset.

To use the Experiment 8 CNN, install TensorFlow and place the model file `potato_model.h5` next to `run.py`. `load_model()` will then load it automatically.

## Running the Tests

```bash
python -m pytest tests -v                      # all unit, integration, system, ECP, BVA tests
python -m pytest tests/test_unit.py -v         # unit tests only
python -m pytest tests/test_integration.py -v  # integration tests
python -m pytest tests/test_system.py -v       # system tests
python -m pytest tests/test_ecp.py -v          # ECP
python -m pytest tests/test_bva.py -v          # BVA
python -m pytest selenium_test.py -v           # Selenium (needs Chrome)
```

## Testing Approach

| Technique | Type | Tests | What it covers |
|---|---|---|---|
| Unit testing | White box | 13 | Each core function tested on its own |
| Integration testing | White box / grey box | 4 | Validate + Preprocess + Predict, Predict + Advice, Web + History |
| System testing | Black box | 8 | Full web flow through HTTP requests |
| Equivalence Class Partitioning | Black box | 10 | File type, image size in pixels, file size |
| Boundary Value Analysis | Black box | 9 | 31/32/33 px, 5 MB ± 1 byte, confidence 0.59/0.60/0.61 |
| Selenium | Black box | 2 | Browser automation (healthy leaf, non-leaf image) |
| Jenkins | - | - | Pipeline that runs the tests automatically |

**Result:** 44 of 44 pytest test cases pass.

### Defect found and fixed (D01)

In the first run, system test ST04 failed: a dark non-leaf image was accepted and shown as "Late Blight". A classifier always returns one of its known classes, so a leaf check was missing. The fix was `is_leaf_image()`, which rejects images with fewer than 30 % plant-coloured pixels. Two unit tests were added and the whole suite was run again.

## Jenkins

The `Jenkinsfile` defines these stages: Checkout, Install requirements, Run pytest (with JUnit report), then publish the report. Create a Pipeline job in Jenkins that uses this file.

## Tech Stack

Python, Flask, Pillow, NumPy, pytest, Selenium WebDriver, Jenkins

## Limitations

- The automated tests use a stand-in model, so they verify the application logic, not the accuracy of the CNN. The CNN's accuracy (96.75 %) was measured in Experiment 8.
- The leaf check is a simple colour rule, not a trained detector.

## Authors

- Varsha Patil (A267)

**Faculty:** Prof. Dhiraj Bhise  
B.Tech Information Technology (Final Year), NMIMS Shirpur - Academic Year 2026-27

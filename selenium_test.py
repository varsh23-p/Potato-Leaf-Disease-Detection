"""Selenium UI test for the Potato Leaf Disease Detector (Step 11).
Run:  pytest selenium_test.py -v        (needs Google Chrome; Selenium 4 downloads the driver itself)
The test starts the Flask app on port 8000 by itself, so nothing else needs to be running.
"""
import os, sys, tempfile, threading, time
import pytest
from werkzeug.serving import make_server
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "tests"))
from helpers import make_leaf, make_non_leaf
from leaf_app.web import create_app

URL = "http://127.0.0.1:8000"


@pytest.fixture(scope="module")
def server():
    srv = make_server("127.0.0.1", 8000, create_app())
    t = threading.Thread(target=srv.serve_forever, daemon=True); t.start()
    yield
    srv.shutdown()


@pytest.fixture
def driver(server):
    opts = webdriver.ChromeOptions()
    # opts.add_argument("--headless=new")      # un-comment to run without a window
    d = webdriver.Chrome(options=opts)
    yield d
    d.quit()


def save_png(data):
    f = tempfile.NamedTemporaryFile(suffix=".png", delete=False); f.write(data); f.close()
    return f.name


def wait_for(driver, element_id, timeout=10):
    """Wait until the element appears after the page reloads (fixes NoSuchElementException)."""
    return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.ID, element_id)))


def test_SE01_upload_healthy_leaf_shows_prediction(driver):
    driver.get(URL)
    driver.find_element(By.ID, "leaf_image").send_keys(save_png(make_leaf("healthy")))
    driver.find_element(By.ID, "predict_btn").click()
    label = wait_for(driver, "result_label")
    time.sleep(1)
    driver.save_screenshot("selenium_SE01.png")          # evidence
    assert label.text == "Healthy"


def test_SE02_non_leaf_image_shows_error(driver):
    driver.get(URL)
    driver.find_element(By.ID, "leaf_image").send_keys(save_png(make_non_leaf()))
    driver.find_element(By.ID, "predict_btn").click()
    err = wait_for(driver, "error_msg")
    time.sleep(1)
    driver.save_screenshot("selenium_SE02.png")          # evidence
    assert "Not a potato leaf image" in err.text

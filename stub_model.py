"""Stand-in model with the same interface as the Lab 8 Keras model.

Lab 8 model:  model.predict(x) -> array of shape (1, 3) with class probabilities
Class order (alphabetical, as produced by Keras image_dataset_from_directory):
    0 = Potato___Early_blight, 1 = Potato___Late_blight, 2 = Potato___healthy

StubLeafModel is a simple colour-statistics heuristic so that the *software around
the model* (validation, preprocessing, thresholding, UI, history) can be tested
quickly and repeatably without TensorFlow or the PlantVillage dataset.
To use the real model, place `potato_model.h5` next to run.py (see load_model()).
"""
import os
import numpy as np


class StubLeafModel:
    def predict(self, x, verbose=0):
        img = np.asarray(x[0], dtype=np.float32)
        r, g, b = img[..., 0], img[..., 1], img[..., 2]
        dark = float(np.mean((r < 70) & (g < 70) & (b < 70)))
        brown = float(np.mean((r > g + 15) & (r > b + 30) & (r > 90)))
        if dark > 0.12:
            p = [0.05, 0.90, 0.05]          # Late blight
        elif brown > 0.02:
            p = [0.90, 0.06, 0.04]          # Early blight
        else:
            p = [0.04, 0.04, 0.92]          # healthy
        return np.array([p], dtype=np.float32)


def load_model(path="potato_model.h5"):
    """Load the real Keras model if available, otherwise the stub."""
    if os.path.exists(path):
        from tensorflow import keras            # pragma: no cover
        return keras.models.load_model(path)    # pragma: no cover
    return StubLeafModel()

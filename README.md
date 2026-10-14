# Potato Leaf Disease Detection - Lab 9 project (A267)
Run the app:      python run.py            -> http://127.0.0.1:8000
Run all tests:    python -m pytest tests -v
Selenium test:    python -m pytest selenium_test.py -v   (needs Chrome)
Jenkins:          create a Pipeline job that uses the Jenkinsfile in this folder.
Real model:       put the Lab 8 model as potato_model.h5 next to run.py and install tensorflow;
                  load_model() will then use it instead of StubLeafModel.

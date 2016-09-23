import unittest
import os
import project.prediction_bot.predict as predict
#pre python 3.3.  In new versions from unittest.mock import patch
from mock import patch
import cPickle
import json

def mock_load_model(redis=None):
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/random_forest.p")
    model = cPickle.load(open(model_path,"rb"))
    return model

def mock_load_tfidf(redis=None):
    tfidf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/tfidf.p")
    tfidf = cPickle.load(open(tfidf_path,"rb"))
    return tfidf

@patch("project.prediction_bot.predict.load_tfidf", mock_load_tfidf)
@patch("project.prediction_bot.predict.load_model", mock_load_model)
class TestPredictApp(unittest.TestCase):

    def setUp(self):
        self.app = predict.app.test_client()
        self.app.testing = True

    def test_main_page(self):
        """Test that the status code 200 is returned for get."""
        results = self.app.get("/")
        self.assertEqual(results.status_code, 200)

    def test_prediction_status(self):
        """Test that the status code 200 is returned for post."""
        results = self.app.post("/score", data=json.dumps({"text":"Test data content."}))
        self.assertEqual(results.status_code, 200)

    def test_prediction_results(self):
        """Test that the right prediction is returned"""
        text = """Non-linear machine learning classification algorithm."""
        results = self.app.post("score",data=json.dumps({"text":text}))
        self.assertEqual(results.get_data(as_text=True),"Machine_learning_algorithms")
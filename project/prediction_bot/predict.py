from flask import Flask, request, jsonify
import os
import redis
import pickle

REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
APP_PORT = int(os.getenv("APP_PORT"))
DEBUG = bool(os.getenv("DEBUG"))

app = Flask(__name__)
r = redis.StrictRedis(host=REDIS_HOST,port=REDIS_PORT)

def load_model(redis):
    return pickle.loads(r['model'])

def load_tfidf(redis):
    return pickle.loads(r['tfidf'])

def transform_data(document_string,tfidf):
    #transform a single string representing a document
    #takes a string and tfidf vectorizer as input
    #returns a 1xn sparse array as output
    return tfidf.transform([document_string])

@app.route("/score",methods=["POST"])
def score():
    #capture data from post request
    req = request.get_json(force=True)
    #transform data
    text = req['text']
    #load model
    model = load_model(r)
    #load_tdidf vectorizor
    tfidf = load_tfidf(r)
    x = transform_data(text,tfidf)
    #score
    prediction = str(model.predict(x)[0])
    print(prediction)
    return prediction


@app.route("/")
def main():
    return "Hello World!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=APP_PORT,debug=DEBUG)
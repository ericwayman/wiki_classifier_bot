from flask import Flask, request, jsonify
import os
import json
import redis
import pickle

PORT = int(os.getenv("PORT"))
DEBUG = (os.getenv("DEBUG")=='True')

if "VCAP_SERVICES" in os.environ:
    services = json.loads(os.getenv("VCAP_SERVICES"))
    redis_env = services["p-redis"][0]["credentials"]
else:
    REDIS_HOST=os.getenv('REDIS_HOST')
    REDIS_PORT=os.getenv('REDIS_PORT')
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD',None)
    redis_env = dict(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)

r = redis.StrictRedis(**redis_env)
app = Flask(__name__)

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
    return jsonify({'prediction':prediction})


@app.route("/")
def main():
    return "Hello World!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
    # app.run(host='0.0.0.0', port=APP_PORT,debug=DEBUG)

# if os.environ.get('VCAP_SERVICES') is None: # running locally
#     PORT = 8080
#     DEBUG = True
# else:                                       # running on CF
#     PORT = int(os.getenv("PORT"))
#     DEBUG = False

# app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
import os
import redis
import pickle

REDIS_HOST=os.getenv('REDIS_HOST')
REDIS_PORT=os.getenv('REDIS_PORT')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD',None)
PARENT_DIRECTORY = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_DIRECTORY = os.path.join(PARENT_DIRECTORY,'tests/data')
MODEL_PATH = os.path.join(MODELS_DIRECTORY,'random_forest.p')
TFIDF_PATH = os.path.join(MODELS_DIRECTORY,'tfidf.p')


def load_redis(REDIS_HOST,REDIS_PORT,REDIS_PASSWORD=None):
    if REDIS_PASSWORD == None:
        r = redis.StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    else:
        r = redis.StrictRedis(
                        host=REDIS_HOST,
                        port=REDIS_PORT,
                        password=REDIS_PASSWORD
                        )
    return r

def save_object_to_redis(redis,object,key):
    #save model to redis
    redis.set(key,pickle.dumps(object,1))

def load_pickled_file(file_path):
    return pickle.load(open(file_path,"rb"))

def main():
    r = load_redis(REDIS_HOST,REDIS_PORT,REDIS_PASSWORD)
    model = load_pickled_file(MODEL_PATH)
    tfidf = load_pickled_file(TFIDF_PATH)
    save_object_to_redis(r,model,"model")
    save_object_to_redis(r,tfidf,"tfidf")

if __name__ == "__main__":
    main()
    print("Loaded objects to redis")
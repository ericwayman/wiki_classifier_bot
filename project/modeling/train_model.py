#train and save model to redis
import os
import psycopg2 as pg
import redis
from collections import defaultdict
import pickle
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cross_validation import StratifiedKFold
from sklearn import metrics
import redis
#environment variables
SEED=1337
NUM_FOLDS = 10

BASE_URL = os.getenv('BASE_URL')
SCHEMA = os.getenv('SCHEMA')
RAW_DATA_TABLE = os.getenv('RAW_DATA_TABLE')
REDIS_HOST=os.getenv('REDIS_HOST')
REDIS_PORT=os.getenv('REDIS_PORT')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD',None)

def database_connection():
    connection = pg.connect(
                        "dbname='{db}' user='{u}' password = '{p}' host='{h}'".format
                        (
                            db=os.getenv("DATABASE_NAME"),
                            u=os.getenv("DATABASE_USER"),
                            p=os.getenv("DATABASE_PASSWORD"),
                            h=os.getenv("DATABASE_HOST")
                        )
                    )
    return connection


def load_from_db_to_df(connection,table_with_schema):
    query = "SELECT * FROM {};".format(table_with_schema)
    df = pd.read_sql(
                    sql=query,
                    con=connection
                    )
    return df

def text_transforms(text,word_limit=3000):
    #text = text.decode("utf-8") #not needed in python 3
    text = text[:word_limit]
    return text

def preprocess_data_frame(df):
    #drop rows that correspond with articles with two labels. Take last since first category has highest count
    old_len = df.shape[0]
    duplicates = df.duplicated(subset="content",take_last=True)
    df = df[duplicates == False]
    new_len = df.shape[0]
    print("dropped {} duplicates".format(old_len-new_len))
    df = df.reset_index()
    #apply any text transformation- trimming, article, stemming words, etc...
    df['content'] = df['content'].apply(lambda x: text_transforms(text=x))
    X = df['content']
    y = df['category']
    return X,y

def initialize_tfidf():
    tfidf = TfidfVectorizer(
        analyzer = u'word',
        ngram_range=(1,2),
        lowercase='true',
        stop_words = 'english',
        strip_accents = 'ascii',
        use_idf = True
    )
    return tfidf

def vectorize_data(train,tfidf):
    '''
    Given the feature arrays train and test returns
    the tfidf vectorized arrays: X_train, X_test
    '''
    X_train = tfidf.fit_transform(train)
    return X_train.toarray()

def initialize_model(seed):
    from sklearn.ensemble import RandomForestClassifier
    model = RandomForestClassifier(
    n_estimators = 100,
    random_state = seed,
    min_samples_leaf =2
    )
    return model

def save_model(model,redis):
    #save model to redis
    redis.set("model",pickle.dumps(model,1))

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

def main():
    connection = database_connection()
    table_with_schema = '{s}.{t}'.format(s=SCHEMA,t=RAW_DATA_TABLE)
    df = load_from_db_to_df(connection,table_with_schema)
    X,y = preprocess_data_frame(df)
    tfidf = initialize_tfidf()
    X = vectorize_data(X,tfidf)
    model = initialize_model(SEED)
    model.fit(X,y)
    r = load_redis(REDIS_HOST,REDIS_PORT,REDIS_PASSWORD)
    save_model(model,r)
    r.set("tfidf",pickle.dumps(tfidf,1))

if __name__ == "__main__":
    main()


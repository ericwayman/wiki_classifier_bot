import os
import psycopg2 as pg
from wiki_scraper import CategoryData

#Fix so categories are no longer hard coded
CATEGORIES = ["Rare diseases",
                "Infectious diseases",
                "Cancer",
                "Congenital disorders",
                "Organs (anatomy)",
                "Machine learning algorithms",
                "Medical devices"
                ]
BASE_URL = os.getenv('BASE_URL')
SCHEMA = os.getenv('SCHEMA')
TABLE = os.getenv('RAW_DATA_TABLE')

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

def main():
    conn = database_connection()
    data_object= CategoryData(categories=CATEGORIES,
                                base_url=BASE_URL,
                                schema=SCHEMA,
                                table=TABLE,
                                connection=conn
                            )
    data_object.save_data_to_database()

if __name__ == "__main__":
    main()

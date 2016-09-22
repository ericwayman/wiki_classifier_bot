import project.modeling.wiki_scraper as ws
from unittest import TestCase
import uuid

import psycopg2 as pg
from psycopg2.extensions import AsIs, ISOLATION_LEVEL_AUTOCOMMIT
import os


from psycopg2.extras import DictCursor

# Local test instance
host = os.getenv('DS_TEST_HOST')
user = os.getenv("DS_TEST_USER")
#password = os.getenv("DS_TEST_PASSWORD")

class CategoryDataLocalTest(TestCase):

    #should seperate into two classes
    #basemodel with the set up functions
    #CategoryDataLocalTest for the CategoryData tests
    #seperate when testing a second module
    def setUp(self):
        self.admin_conn = pg.connect(user=user, host=host,
                                     database=user, password='')
        # Total db name length should be less than 46 characters
        self.test_db = 'wiki_' + str(uuid.uuid4()).replace("-", "_")
        self.schema = 'test'
        self.drop_database()
        self.create_database()
        self.load_schema()
        self.test_conn = pg.connect(user=user, host=host, password ='',
                                    database=self.test_db, cursor_factory=DictCursor)
    def create_database(self):
        self.admin_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = self.admin_conn.cursor()
        cur.execute('CREATE DATABASE %s;', (AsIs(self.test_db),))
        # print("Created database {}".format(self.test_db))
        cur.close()

    def load_schema(self):
        cur = self.admin_conn.cursor()
        cur.execute('DROP SCHEMA IF EXISTS %s CASCADE;',(AsIs(self.schema),))
        cur.execute('CREATE schema %s;',(AsIs(self.schema),))
        cur.close()

    def drop_database(self):
        self.admin_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = self.admin_conn.cursor()
        try:
            cur.execute('SELECT 1;')
            cur.execute('DROP DATABASE IF EXISTS %s;', (AsIs(self.test_db),))
        except pg.OperationalError as e:
            print('Not able to drop database {}'.format(self.test_db))
            print('Error: {}'.format(e))
            # Who is accessing database?
            cur.execute("SELECT * FROM pg_stat_activity where datname=%s;", (self.test_db,))
            res = cur.fetchall()
            print("pg_stat_activity: " + str(res))
            # Try again
            cur.execute("SELECT 1;")
            cur.execute("DROP DATABASE IF EXISTS %s;", (AsIs(self.test_db),))
            print("Second attempt to drop database succeeded.")
        else:
            # print('Dropped database {}'.format(self.test_db))
            pass
        cur.close()

    def tearDown(self):
        self.test_conn.close()
        self.drop_database()

    #actual tests
    def test_add_category_data_to_table(self):
        data = [('cat1','content1'),('cat2','content2'),('cat3','content3')]
        schema = self.schema
        table = 'test_table'
        ws.add_category_data_to_table(
                                    connection = self.admin_conn,
                                    schema =schema, 
                                    table = table,
                                    data = data
                                    )
        cursor = self.admin_conn.cursor()
        cursor.execute('SELECT * FROM %s;', (AsIs('{s}.{t}'.format(s=schema,t=table)),))
        result = cursor.fetchall()
        self.assertEqual(
                        [('cat1','content1'),('cat2','content2'),('cat3','content3')],
                        result
                        )
    # def test_category_data(self):
    #     pass
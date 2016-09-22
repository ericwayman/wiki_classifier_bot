from bs4 import BeautifulSoup
from os import path
import pandas as pd
import urllib2
from psycopg2.extensions import AsIs
#add def strings
class WikiScraper:

    def __init__(self,url):
        self.url = url
        self.page_links = None

    def _fetch_html(self):
        opener = urllib2.build_opener()
        resource = opener.open(self.url)
        data = resource.read()
        resource.close()
        soup = BeautifulSoup(data,"lxml")
        return soup

class CategoryScraper(WikiScraper):
    
    def find_page_links(self):
        soup = self._fetch_html()
        #find the node in the DOM containing the page links
        page_node = soup.find('div',{"id":"mw-pages"})
        children = page_node.findChildren()
        page_links = []
        for child in children:
            if 'href' in child.attrs:
                page_links.append(child.get('href'))
        #don't count FAQ link and next page link
        self.page_links = [x for x in page_links if (":FAQ" not in x) and ("Category:" not in x)]
        #before return pages can check the last link pull those links if there's another page
        return self.page_links


class TextScraper(WikiScraper):
    
    def _clean_text(self,text):
        #can  also import re to remove tags '<>'
        return text.replace('\n',' ')
    
    def extract_text(self):
        soup = self._fetch_html()
        #extract relevant text but being careful not to extract the category section
        #This grabs the text in the <p> tags, but avoids the category text contained in a <div> tag
        text = " ".join([str(s.extract()) for s in soup('p')])
        text = self._clean_text(text)
        return text

class CategoryData:

    def __init__(self,categories,base_url,schema,table,connection):
        #replace spaces with underscores in categories to fit wikipedia conventions
        self.categories = [c.replace(' ','_') for c in categories]
        self.base_url = base_url #https://en.wikipedia.org/wiki/Category:
        #self.directory = directory
        self.schema = schema
        self.table = table
        self.connection = connection
    def save_data_to_csv(self,out_file):
        data = []
        for cat in self.categories:
            cat_url = self.base_url + cat
            cat_scraper = CategoryScraper(cat_url)
            links = cat_scraper.find_page_links()
            for link in links:
                text_scraper = TextScraper('https://en.wikipedia.org'+link)
                text = text_scraper.extract_text()
                data.append((cat,text))
            print "added {} links of Data for category: {}".format(len(links),cat)
        df = pd.DataFrame.from_records(data=data, columns = ["category","text"])
        print "saving file"
        #use utf8 to avoid error letter when stemming
        df.to_csv(out_file,index=False,encoding = 'utf8')

    def _load_data(self):
        #break into calls to scrape categories and drop, create insert into table functions
        #for large amounts of categories
        data = []
        #can add an option to only load several categories at a time
        for cat in self.categories:
            cat_url = self.base_url + cat
            cat_scraper = CategoryScraper(cat_url)
            links = cat_scraper.find_page_links()
            for link in links:
                text_scraper = TextScraper('https://en.wikipedia.org'+link)
                content = text_scraper.extract_text()
                content = str.decode(content).encode('utf-8')
                data.append((cat,content))
            print "added {} links of Data for category: {}".format(len(links),cat)
        self.data = data
    #for better testing we should remove this as class method and use as a helper fucntion
    #then we can test with artificial data or a mock CategoryData object
    def save_data_to_database(self):
        self._load_data()
        print "saving file to database"
        add_category_data_to_table(connection=self.connection,schema=self.schema,table=self.table,data=self.data)

def add_category_data_to_table(connection,schema,table,data):
        table_with_schema = '{s}.{t}'.format(s=schema,t=table)
        #look into using a with statement for the cursor
        cur = connection.cursor()
        cur.execute('DROP SCHEMA IF EXISTS %s CASCADE',(AsIs(schema),))
        cur.execute('CREATE SCHEMA %s',(AsIs(schema),))
        cur.execute('CREATE TABLE %s (category text, content text)',(AsIs(table_with_schema),))
        records_list_template = ','.join(['%s'] * len(data))
        insert_query = 'INSERT INTO {ts} (category, content) VALUES {r}'.format(
                ts=table_with_schema,
                r=records_list_template
                )
        cur.execute(insert_query,data)
        connection.commit()
        print "Inserted {n} rows into {ts}".format(n=len(data),ts=table_with_schema)
        cur.close()

"""
openclassrooms Python - Project 2
bookscraper package
@author Christian Debray - christian.debray@gmail.com
"""
from scrapeindex import ScrapeIndex
from bs4 import BeautifulSoup
import re
import urllib.parse
from remotedatasource import RemoteDataSource

class CategoryIndex(ScrapeIndex):
    def __init__(self, category_url: str, data_src: RemoteDataSource = None):
        super().__init__(data_src=data_src)
        self.category_url: str = category_url
        self.category_name: str = ''
        self.total_books: int = 0
        self._read_category_info()
        self.load_generator_from_url(self.category_url)
    
    def _read_category_info(self):
        """
        Parse the category page and extract some useful infos
        """
        category_html = self.src.read_text(self.category_url)
        category_soup = BeautifulSoup(category_html, 'html.parser')
        if cat_title_tag := category_soup.css.select_one('.page-header > h1'):
            self.category_name = " ".join(cat_title_tag.stripped_strings)
    
    def list_categories(self):
        """
        reads category names and urls from the navigation menu.
        Returns a dictionary mapping category urls to category names.
        """
        category_html = self.src.read_text(self.category_url)
        category_soup = BeautifulSoup(category_html, 'html.parser')
        if items := category_soup.css.select("aside .side_categories ul.nav-list ul li > a"):
            return {urllib.parse.urljoin(self.category_url, a.attrs.get('href')) : " ".join(a.stripped_strings) for a in items}
        else:
            return {}

    def _normalize_stripped_strings(self, stripped_strings):
        return " ".join([s.strip() for s in re.split(r'[\t\n\r\f\v]+', stripped_strings)])

if __name__ == "__main__":
    cat_idx = CategoryIndex('https://books.toscrape.com/catalogue/category/books/travel_2/index.html')
    print(cat_idx.category_name, cat_idx.category_url)
    print("\nAll categories:")
    for url, cat_name in cat_idx.list_categories().items():
        print(cat_name, url)

"""
openclassrooms Python - Project 2
bookscraper package
@author Christian Debray - christian.debray@gmail.com
"""
from scrapeindex import ScrapeIndex
from bs4 import BeautifulSoup
import re
from remotedatasource import RemoteDataSource
from scraping_generators import AbstractScrapingGenerator

class CategoryIndex(ScrapeIndex):
    def __init__(self, category_url: str, scraping_generator: AbstractScrapingGenerator, data_src: RemoteDataSource = None):
        super().__init__(data_src=data_src, scraping_generator = scraping_generator)
        self.category_url: str = category_url
        self.category_name: str = ''
        self.total_books: int = 0
        category_html = self.src.read_text(self.category_url)
        self.category_soup = BeautifulSoup(category_html, 'html.parser')
        self._read_category_info()
        self.load_generator_from_url(self.category_url)
    
    def _read_category_info(self):
        """
        Parse the category page and extract some useful infos
        """
        cat_data = self.scraping_generator.gen_category_info(self.category_soup)
        self.category_name = cat_data.get('category_name', None)
    
    def list_categories(self):
        """
        Reads category names and urls from the navigation menu.
        Returns a dictionary mapping category urls to category names.
        """
        return self.scraping_generator.gen_categories_urls(base_url= self.category_url, category_soup= self.category_soup)

    def _normalize_stripped_strings(self, stripped_strings):
        return " ".join([s.strip() for s in re.split(r'[\t\n\r\f\v]+', stripped_strings)])

if __name__ == "__main__":
    from books_to_scrape_generators import BooksToScrapeGenerator
    cat_idx = CategoryIndex(
        category_url= 'https://books.toscrape.com/catalogue/category/books/travel_2/index.html',
        scraping_generator= BooksToScrapeGenerator()
    )
    print(cat_idx.category_name, cat_idx.category_url)
    print("\nAll categories:")
    for url, cat_name in cat_idx.list_categories().items():
        print(cat_name, url)
    print("\nBooks in this category:")
    for url in cat_idx.list_urls_to_scrape():
        print(url)

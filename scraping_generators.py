from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from bookdata import BookData

class AbstractScrapingGenerator(ABC):
    @abstractmethod
    def gen_category_info(self, category_soup: BeautifulSoup) -> dict[str, str|int]:
        """
        Called by CategoryIndex._read_category_info()
        Parse the category page and extract some useful infos returned as a dictionary.
        """
        pass

    @abstractmethod
    def gen_categories_urls(self, base_url, category_soup: BeautifulSoup) -> dict[str, str]:
        """
        Called by CategoryIndex.list_categories()
        reads category names and urls from the navigation menu.
        Returns a dictionary mapping category urls to category names.
        """
        pass
    
    @abstractmethod
    def gen_product_urls_from_index(self, index_soup: BeautifulSoup, base_url: str) -> list[str]:
        """
        Called by ScrapeIndex._read_url_index()
        """
        pass

    @abstractmethod
    def gen_index_next_page_url(self, index_soup: BeautifulSoup, base_url: str) -> str:
        """
        Called by ScrapeIndex._read_url_index()
        """
        pass

    @abstractmethod
    def gen_book_data(self, book_soup: BeautifulSoup, book_url: str) -> BookData:
        """
        Called by BookDataReader.read_from_html()
        Reads all data to scrape from a book product page, and writes the data into a BookData object.
        """
        pass

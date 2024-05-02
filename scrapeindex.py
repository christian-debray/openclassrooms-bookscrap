"""
openclassrooms Python - Project 2
bookscraper package
@author Christian Debray - christian.debray@gmail.com
"""
from remotedatasource import RemoteDataSource
import urllib.parse
from bs4 import BeautifulSoup
from typing import Generator
from collections.abc import Generator
from scraping_generators import AbstractScrapingGenerator
import logging
logger = logging.getLogger(__name__)

class ScrapeIndex:
    """
    Iterate over URLs to scrap and keep track of URLS already scrapped.

    The list of URLs to scrape will be generated:
      - either from a list (see the load_generator_from_list() method)
      - or from a URL where the list of URLs to scrape can be extracted (see the load_generator_from_url() method)

    The load_generator_from_url() supports paginated content and will lazily load the contents of the next page on demand.

    Usage:
     1. create a new instance of the ScrapeIndex
     2. load the URL generator
     3. iterate over the URLs with the list_urls_to_scrape() method

    ```
     scrape_idx = ScrapeIndex()
     scrape_idx.load_generator_from_url('https://example.com/path/to/index')
     for url in scrape_idx.list_urls_to_scrape():
        # do something brilliant with the url string
        (...)
    ```
    """

    def __init__(self, scraping_generator: AbstractScrapingGenerator, data_src: RemoteDataSource = None):
        self.scraping_generator: AbstractScrapingGenerator = scraping_generator
        self.index_url = ''
        self._url_map: dict[str, str|bool] = {}
        self._url_generator = self.load_generator_from_list([])
        self.src = data_src or RemoteDataSource()

    def mark_url(self, url, scraped: bool = True):
        """
        Marks a url as scraped.
        """
        self._url_map[url] = scraped

    def is_scraped(self, url: str) -> bool:
        """
        Returns True if a URL is already amrked as being scraped,
        False otherwise.
        """
        return self._url_map.get(url, False)

    def load_generator_from_list(self, url_list: list[str]):
        """
        Loads the list of URLs to scrape from a list.
        """
        self._url_generator = iter(url_list)

    def load_generator_from_url(self, index_url: str):
        """
        Loads the list of URLs to scrape from data found at a given URL.
        """
        self._url_generator = iter(self._read_url_index(index_url))
    
    def list_urls_to_scrape(self) -> Generator[str]:
        """
        Lazily lists the URLs that have not been scraped yet.
        """
        for next_url in self._url_generator:
            if False == self._url_map.get(next_url, False):
                self.mark_url(next_url)
                yield next_url

    def _read_url_index(self, index_url) -> Generator[str]:
        """
        Reads the contents found at index url and extracts a list of urls to scrape.
        Lazily proceeds to the next page if content is paginated.
        """
        next_index_url = index_url
        while next_index_url:
            index_html = self.src.read_text(next_index_url)
            index_soup = BeautifulSoup(index_html, 'html.parser')
            url_list = self.scraping_generator.gen_product_urls_from_index(index_soup=index_soup, base_url=next_index_url)
            logger.debug("Found {0} links".format(len(url_list)))
            next_index_url = self.scraping_generator.gen_index_next_page_url(index_soup= index_soup, base_url= next_index_url)
            for url in url_list:
                yield url
            if next_index_url:
                logger.debug(f"Proceed to next page: {next_index_url}")
            else:
                logger.debug("Reached the end of index")

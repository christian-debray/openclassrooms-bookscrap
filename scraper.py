"""
openclassrooms Python - Project 2
bookscraper package
@author Christian Debray - christian.debray@gmail.com
"""
from categoryindex import CategoryIndex
from scrapeindex import ScrapeIndex
from bookdatawriter import BookDataWriter
from bookdatareader import BookDataReader
from remotedatasource import RemoteDataSource
import os
import csv
import re
import datetime
import logging
logger = logging.getLogger(__name__)

class Scraper:
    """
    Main class
    """

    def __init__(self):
        self._category_indexes = {}
        # limit request speed to preserve bandwidth on the remote server:
        self._requests_delay = 2.0
        self._book_data_reader = BookDataReader()
        self._data_source = RemoteDataSource(requests_delay= self._requests_delay)
    
    def scrape_all_categories(self, url: str, output_path: str):
        """
        Scrape all categories. Output_path should be a valid path to a writable directory.
        """
        home_index = CategoryIndex(url)
        for cat_url, cat_name in home_index.list_categories().items():
            csv_output_file = os.path.join(output_path, self._gen_csv_filename(cat_name))
            self.scrape_category(cat_url, csv_output_file)

    def scrape_category(self, category_index_url: str, csv_output_file: str):
        """
        Scrape all books found in a category. The first parameter should point to the category index page.
        csv_output_file should be a valid path to a csv output file.
        Appends book data to the output csv file if the url has not been scraped yet.
        """
        category_index = self._get_category_index(category_index_url)
        logger.info(f"Scrape category {category_index.category_name} to {csv_output_file}")
        self._mark_scraped_urls_from_csv(csv_output_file, category_index)
        writer = BookDataWriter(csv_output_file)

        for url in category_index.list_urls_to_scrape():
            self.scrape_book(url, writer)

    def scrape_book(self, product_page_url: str, writer: BookDataWriter):
        """
        Scrape book data found on a product page, appends the result to the output file
        """
        logger.info(f"scrape book: {product_page_url}")
        self._data_source.set_source(product_page_url)
        book_html = self._data_source.read_text()
        if book := self._book_data_reader.read_from_html(book_html, product_page_url):
            book.product_page_url = product_page_url
            if (book.is_valid()):
                if success := writer.append_data(book):
                    logger.info(f"Exported book data to csv file")
            else:
                logger.info("Invalid book data, skip record.")

    def _get_category_index(self, category_index_url) -> CategoryIndex:
        """
        Cache category indexes and find them by the category URL.
        """
        if category_index_url not in self._category_indexes:
            self._category_indexes[category_index_url] = CategoryIndex(category_index_url)
        return self._category_indexes[category_index_url]

    def _gen_csv_filename(self, name: str) -> str:
        """
        Returns a valid csv basename with a .csv extension. Spaces and slashes are replaced by an underscore character ('_').
        """
        return re.sub(r'[\s/]+', '_', name.strip(" /")) + '.csv'

    def _mark_scraped_urls_from_csv(self, csv_file: str, urls_index: ScrapeIndex):
        """
        Read the urls found in a csv file and mark them as already scraped.
        The method first checks if the file exists.
        """
        if os.path.exists(csv_file) and os.path.isfile(csv_file) and os.stat(csv_file).st_size > 0:
            with open(csv_file, "r") as f:
                csv_reader = csv.DictReader(f)
                for row in csv_reader:
                    if url := row['product_page_url']:
                        urls_index.mark_url(url)

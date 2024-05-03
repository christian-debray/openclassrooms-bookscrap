"""
openclassrooms Python - Project 2
bookscraper package
@author Christian Debray - christian.debray@gmail.com
"""
from categoryindex import CategoryIndex
from scrapeindex import ScrapeIndex
from bookdata import BookData
from bookdatawriter import BookDataWriter
from bookdatareader import BookDataReader
from remotedatasource import RemoteDataSource, max_attempts_decorator
import os
import csv
import re
import logging
from collections.abc import Callable
from scraping_generators import AbstractScrapingGenerator

logger = logging.getLogger(__name__)

class Scraper:
    """
    Main scraper class. Pilots the scraping jobs.
    """

    SCRAPE_ALL = "scrape_all"
    SCRAPE_CATEGORY = "scrape_category"
    SCRAPE_PRODUCT = "scrape_product"
    SCRAPE_IMAGE = "scrape_image"

    def __init__(
            self,
            output_dir: str, 
            scraping_generator: AbstractScrapingGenerator,
            mode: str = "scrape_content",
            custom_url_handler: Callable = None,
            requests_delay: float = 2.0,
            timeout: tuple[float, float] = (3.05, 7.0)
            ):
        """
        Initialize the scraper.

        output_dir -- path to the directory where the csv files should be stored

        scraping_generator -- A scraping generator object that knows how to retrieve the data from the remote data source.

        mode -- If mode is "scrape_content" (default), scrape book contents to an object and export to CSV.
        Otherwise, just list URLs to scrape.

        custom_url_handler -- An optional handler can be set to add further handling of scraped urls.
        The handler will be called with two keywords parameters: `scrape_url_handler(**{url: str, scrape_type: str})`

        requests_delay -- wait between 2 requests, to save distant server's bandwidth

        timeout -- set the connect and read timeout parameters (see https://requests.readthedocs.io/en/latest/user/advanced/#timeouts)
        """
        self.scraping_generator = scraping_generator
        self._category_indexes = {}
        self._book_data_reader = BookDataReader(scraping_generator= self.scraping_generator)
        # limit request speed to preserve bandwidth on the remote server:
        self._data_source = RemoteDataSource(requests_delay= requests_delay, timeout= timeout)
        self._scrape_contents: bool = (mode == "scrape_content")
        self._custom_url_handler = custom_url_handler
        self._errors = 0
        self._output_path: str = output_dir
    
    @max_attempts_decorator(max_attempts = 2)
    def scrape_all_categories(self, url: str) -> bool:
        """
        Scrape all categories. Output_path should be a valid path to a writable directory.
        Returns True on success, or False if errors occured.
        """
        # re-use the same data source to take advantage of sessions.
        # see https://requests.readthedocs.io/en/latest/user/advanced/
        home_index = CategoryIndex(category_url = url, data_src= self._data_source, scraping_generator= self.scraping_generator)

        self._handle_url_hook(url, self.SCRAPE_ALL)
        for cat_url, cat_name in home_index.list_categories().items():
            csv_output_file = os.path.join(self._output_path, self._gen_csv_filename(cat_name))
            try:
                self.scrape_category(cat_url, csv_output_file)
            except Exception as e:
                e_type = type(e).__name__
                logger.warning(f"An error ({e_type}) occured while scraping category from URL {cat_url}, skip to next category", exc_info= True)
                self._errors += 1
        return self._errors == 0

    @max_attempts_decorator(max_attempts = 2)
    def scrape_category(self, category_index_url: str, csv_output_file: str = None) -> bool:
        """
        Scrape all books found in a category. The first parameter should point to the category index page.
        csv_output_file should be a valid path to a csv output file.
        Appends book data to the output csv file if the url has not been scraped yet.

        Returns True on success, False if errors occured.
        """
        category_index = self._get_category_index(category_index_url)
        if not csv_output_file:
            csv_output_file = os.path.join(self._output_path, self._gen_csv_filename(category_index.category_name))
        logger.info(f"Scrape category {category_index.category_name} to {csv_output_file}")
        self._handle_url_hook(category_index_url, self.SCRAPE_CATEGORY)
        self._mark_scraped_urls_from_csv(csv_output_file, category_index)
        writer = BookDataWriter(csv_output_file)
        img_dir_path = os.path.join(self._output_path, 'images', self._gen_filename(category_index.category_name))

        cat_errors = 0
        for url in category_index.list_urls_to_scrape():
            try:
                if not self.scrape_book(url, writer, img_dir_path):
                    cat_errors += 1
            except Exception as e:
                e_type = type(e).__name__
                logger.warning(f"An error ({e_type}) occured while scraping book from URL {url}, skip record", exc_info= True)
                self._errors += 1
                cat_errors += 1
        return cat_errors == 0


    @max_attempts_decorator(max_attempts = 2)
    def scrape_book(self, product_page_url: str, writer: BookDataWriter, img_dir_path: str = None):
        """
        Scrape book data found on a product page, appends the result to the output file.
        Returns True if successful.
        """
        logger.debug(f"Scrape book: {product_page_url}")
        self._handle_url_hook(product_page_url, self.SCRAPE_PRODUCT)
        if not self._scrape_contents:
            return
        self._data_source.set_source(product_page_url)
        book_html = self._data_source.read_text()
        success = False
        if book := self._book_data_reader.read_from_html(book_html, product_page_url):
            book.product_page_url = product_page_url
            if (book.is_valid()):
                if writer.append_data(book):
                    success = True
                    logger.debug(f"Exported book data to csv file")
                    # download the image as well
                    if not img_dir_path:
                        img_dir_path = os.path.join(self._output_path, 'images')
                    self._fetch_book_image(book, img_dir_path)
            else:
                logger.warning(f"Scraping produced invalid book data at {product_page_url}, skip record.")
        return success

    def _get_category_index(self, category_index_url) -> CategoryIndex:
        """
        Cache category indexes and find them by the category URL.
        """
        if category_index_url not in self._category_indexes:
            self._category_indexes[category_index_url] = CategoryIndex(
                category_url= category_index_url,
                data_src= self._data_source,
                scraping_generator= self.scraping_generator)
        return self._category_indexes[category_index_url]

    def _gen_csv_filename(self, name: str) -> str:
        """
        Returns a valid csv basename with a .csv extension. Spaces and slashes are replaced by an underscore character ('_').
        """
        return self._gen_filename(name, '.csv')

    def _gen_filename(self, name: str, suffix: str = "") -> str:
        """
        Returns a valid basename generated from the first parameter.
        Successive Spaces and slashes are replaced by a single underscore character ('_').
        Append an optional file extension
        """
        return re.sub(r'[\s/]+', '_', name.strip(" /")) + suffix

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
    
    def _handle_url_hook(self, url: str, scrape_type: str):
        """
        call a custom handler, if set
        """
        if isinstance(self._custom_url_handler, Callable):
            self._custom_url_handler(url= url, scrape_type= scrape_type)

    @max_attempts_decorator(2)
    def _fetch_book_image(self, book: BookData, image_dir: str) -> str:
        """
        Fetch the image file from an URL and store it to image directory.
        The local file will be named after the book title, with the appropriate file extension.
        Returns the local image filename on success, None on failure.
        """
        if book.image_url:
            logger.debug(f"Downloading book image from {book.image_url}")
            self._handle_url_hook(book.image_url, self.SCRAPE_IMAGE)
            if img_data := self._data_source.fetch_binary(book.image_url):
                if not os.path.exists(image_dir):
                    os.makedirs(image_dir, mode = 0o777)
                mime_type, mime_subtype = self._data_source.mime_type()
                if mime_subtype.lower() in ['jpeg', 'jpg', 'png', 'gif']:
                    img_file = os.path.join(image_dir, self._gen_filename(book.universal_product_code, f".{mime_subtype.lower()}"))
                    logger.debug(f"write image to {img_file}")
                    with open(img_file, "wb") as f:
                        f.write(img_data)
                        return img_file
        return None

import bs4
import urllib.parse
from bookdata import BookData
from scraping_generators import AbstractScrapingGenerator
import re

class BooksToScrapeGenerator(AbstractScrapingGenerator):
    """
    Scraping generator methods to scrape data from https://books.toscrape.com/.
    Implements the AbstractScrapingGenerator interface.
    """

    def gen_category_info(self, category_soup: bs4.BeautifulSoup):
        """
        called by CategoryIndex._read_category_info()
        Parse the category page and extract some useful infos
        """
        cat_info = {'category_name': '', 'product_count': 0}
        if cat_title_tag := category_soup.css.select_one('.page-header > h1'):
            cat_info['category_name'] = " ".join(cat_title_tag.stripped_strings)
        if cat_results := category_soup.css.select_one('.form-horizontal > strong:nth-child(2)'):
            results_str = (" ".join(cat_results.stripped_strings)).strip() or "0"
            try:
                cat_info['product_count'] = int(results_str)
            except Exception:
                pass
        return cat_info

    def gen_categories_urls(self, base_url, category_soup: bs4.BeautifulSoup):
        """
        called by CategoryIndex.list_categories()
        reads category names and urls from the navigation menu.
        Returns a dictionary mapping category urls to category names.
        """
        if items := category_soup.css.select("aside .side_categories ul.nav-list ul li > a"):
            return {urllib.parse.urljoin(base_url, a.attrs.get('href')) : " ".join(a.stripped_strings) for a in items}
        else:
            return {}

    def gen_product_urls_from_index(self, index_soup: bs4.BeautifulSoup, base_url: str) -> list[str]:
        """
        called by ScrapeIndex._read_url_index()
        """
        if items := index_soup.css.select('section ol.row > li article.product_pod h3 a'):
            return [urllib.parse.urljoin(base_url, link.attrs.get('href', '')) for link in items]
        else:
            return []

    def gen_index_next_page_url(self, index_soup: bs4.BeautifulSoup, base_url: str) -> str:
        """
        called by ScrapeIndex._read_url_index()
        """
        if next_link := index_soup.css.select_one('.pager .next > a'):
            return urllib.parse.urljoin(base_url, next_link.attrs['href'])
        else:
            return ''

    def gen_book_data(self, book_soup: bs4.BeautifulSoup, book_url: str) -> BookData:
        """
        Called by BookDataReader.read_from_html()
        Reads all data to scrape from a book product page, and writes the data into a BookData object.
        """
        book = BookData()
        product_page = book_soup.find(name="article", class_="product_page")
        # check we're actually on a product description page...
        if product_page is None:
            return None
        # Use the css selectors defined in our mapping class ot extract the data:
        if title_tag := book_soup.css.select_one("#content_inner > article.product_page > div.row > div.product_main > h1"):
            book.title = BookData.filter_title(self._normalize_string(title_tag.string))

        if product_code_tag := book_soup.css.select_one("#content_inner > article.product_page .table > tr:nth-child(1) > td:nth-child(2)"):
            book.universal_product_code = BookData.filter_universal_product_code(self._normalize_string(product_code_tag.string))

        if category_tag := book_soup.css.select_one(".breadcrumb > li:nth-child(3) > a:nth-child(1)"):
            book.category = BookData.filter_category(self._normalize_string(category_tag.string))

        if price_incl_tax_tag := book_soup.css.select_one("#content_inner > article.product_page .table tr:nth-child(4) > td"):
            book.price_including_tax = BookData.filter_price(self._normalize_string(price_incl_tax_tag.string))

        if price_excl_tax_tag := book_soup.css.select_one("#content_inner > article.product_page .table tr:nth-child(3) > td"):
            book.price_excluding_tax = BookData.filter_price(self._normalize_string(price_excl_tax_tag.string))

        if number_available_tag := book_soup.css.select_one("#content_inner > article.product_page > div.row > div.product_main > p.instock.availability"):
            raw = self._normalize_string(" ".join(number_available_tag.stripped_strings))
            book.number_available = BookData.filter_number_available(self._read_number_in_stock(raw))

        if product_description_tag := book_soup.css.select_one("#content_inner > article.product_page > p"):
            book.product_description = " ".join(product_description_tag.stripped_strings)

        if review_rating_tag := book_soup.css.select_one("#content_inner > article > div.row > div.col-sm-6.product_main > p.star-rating"):
            book.review_rating = BookData.filter_review_rating(self._read_review_rating(review_rating_tag))

        if image_url_tag := book_soup.css.select_one( "#product_gallery .item > img:nth-child(1)"):
            if image_url := image_url_tag.attrs.get('src', None):
                book.image_url = image_url if (len(book_url) == 0) else urllib.parse.urljoin(book_url, image_url)
        return book

    def _normalize_string(self, in_str: str) -> str:
        """
        normalizes a string for output
        """
        return " ".join([s.strip() for s in re.split(r'[\t\n\r\f\v]+', in_str)])

    def _read_number_in_stock(self, in_str) -> int:
        """
        reads number of copies available in stock
        """
        m = re.search(r"([0-9]+) available", in_str)
        if m is not None:
            return int(m.group(1))
        return 0

    def _read_review_rating(self, review_element: bs4.Tag) -> int:
        """
        reads a review rating tag and converts to int
        """
        ratings = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
        for c in review_element['class']:
            if c.lower() in ratings:
                return ratings[c.lower()]
        return None

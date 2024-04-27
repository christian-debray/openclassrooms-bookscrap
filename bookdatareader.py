"""
openclassrooms Python - Project 2
bookscraper package
@author Christian Debray - christian.debray@gmail.com
"""

import bs4
from bs4 import BeautifulSoup
import re
from bookdata import BookData
from bookdatamapping import BookDataMapping as CSSMapping

class BookDataReader:
    """
    Read data from an HTML source, and produce BookData objects.
    """
    def __init__(self):
        self._soup: BeautifulSoup

    def read_from_html(self, html_str: str) -> BookData:
        markup: BeautifulSoup = BeautifulSoup(html_str, 'html.parser')
        self._soup = markup
        book = BookData()
        product_page = markup.find(name="article", class_="product_page")
        # check we're actually on a product description page...
        if product_page is None:
            return None
        # Use the css selectors defined in our mapping class ot extract the data:
        if title_tag := markup.css.select_one(CSSMapping.title_selector):
            book.title = self._normalize_string(title_tag.string)
        if product_code_tag := markup.css.select_one(CSSMapping.universal_product_code_selector):
            book.universal_product_code = self._normalize_string(product_code_tag.string)
        if category_tag := markup.css.select_one(CSSMapping.category_selector):
            book.category = self._normalize_string(category_tag.string)
        if price_incl_tax_tag := markup.css.select_one(CSSMapping.price_including_tax_selector):
            book.price_including_tax = self._read_price(self._normalize_string(price_incl_tax_tag.string))
        if price_excl_tax_tag := markup.css.select_one(CSSMapping.price_excluding_tax_selector):
            book.price_excluding_tax = self._read_price(self._normalize_string(price_excl_tax_tag.string))
        if number_available_tag := markup.css.select_one(CSSMapping.number_available_selector):
            raw = self._normalize_string(" ".join(number_available_tag.stripped_strings))
            book.number_available = self._read_number_in_stock(raw)
        if product_description_tag := markup.css.select_one(CSSMapping.product_description_selector):
            book.product_description = " ".join(product_description_tag.stripped_strings)
        if review_rating_tag := markup.css.select_one(CSSMapping.review_rating_selector):
            book.review_rating = self._read_review_rating(review_rating_tag)
        if image_url_tag := markup.css.select_one(CSSMapping.image_url_selector):
            book.image_url = image_url_tag.attrs.get('src', None)
        return book

    def _normalize_string(self, in_str: str) -> str:
        """
        normalizes a string for output
        """
        return " ".join([s.strip() for s in re.split(r'[\t\n\r\f\v]+', in_str)])

    def _read_price(self, price_str: str) -> float:
        """
        expected input: £000.00
        """
        return float((price_str.strip())[1:].strip())

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
    
if __name__ == "__main__":
    test_html = """
<html>
    <head><title>test book soup</title></head>
    <body>
        <h1>This is NOT the book's title</h1>
        <div id="content_inner">
            <article class="product_page">
                <h1>Stil not the book's title !</h1>
                <div class="row">
                    <div class="product_main">
                            <h1>hEre's
                            my
                                Title</h1>
                    </div>
                </div>
                <table>
                    <tbody>
                        <tr>
                            <th>UPC</th>
                            <td>12145aee242</td>
                        </tr>
                    </tbody>
                </table>
            </article>
        </div>
    </body>
</html>
"""

    reader = BookDataReader()
    book = reader.read_from_html(test_html)
    assert(book is not None)
    print(book)

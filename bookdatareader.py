"""
openclassrooms Python - Project 2
bookscraper package
@author Christian Debray - christian.debray@gmail.com
"""

from bs4 import BeautifulSoup
from bookdata import BookData
from scraping_generators import AbstractScrapingGenerator

class BookDataReader:
    """
    Read data from an HTML source, and produce BookData objects.
    """
    def __init__(self, scraping_generator: AbstractScrapingGenerator):
        self.scraping_generator = scraping_generator

    def read_from_html(self, html_str: str, book_url: str = "") -> BookData:
        soup: BeautifulSoup = BeautifulSoup(html_str, 'html.parser')
        return self.scraping_generator.gen_book_data(book_soup=soup, book_url=book_url)
    
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
    from books_to_scrape_generators import BooksToScrapeGenerator
    reader = BookDataReader(scraping_generator= BooksToScrapeGenerator())
    book = reader.read_from_html(test_html)
    assert(book is not None)
    print(book)

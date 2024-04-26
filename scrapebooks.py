from remotedatasource import RemoteDataSource
from bookdatareader import BookDataReader

if __name__ == "__main__":
    source = RemoteDataSource('https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html')
    book_html = source.read_text()
    # with open("./test_data/A-Light-in-the-Attic_Books-to-Scrape-Sandbox.html") as f:
    #     book_html = f.read()
    reader = BookDataReader()
    book = reader.read_from_html(book_html)
    print(book)

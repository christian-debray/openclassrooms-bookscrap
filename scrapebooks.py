from remotedatasource import RemoteDataSource
from bookdatareader import BookDataReader
from bookdatawriter import BookDataWriter

if __name__ == "__main__":
    book_url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    csv_output_file = "data/test_book.csv"
    source = RemoteDataSource(book_url)
    book_html = source.read_text()
    # with open("./test_data/A-Light-in-the-Attic_Books-to-Scrape-Sandbox.html") as f:
    #     book_html = f.read()
    reader = BookDataReader()
    book = reader.read_from_html(book_html)
    book.product_page_url = book_url
    writer = BookDataWriter(csv_output_file)
    if success := writer.append_data(book):
        print(f"wrote to {csv_output_file}")
    print("done.")

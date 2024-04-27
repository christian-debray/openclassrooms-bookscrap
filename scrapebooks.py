from remotedatasource import RemoteDataSource
from bookdatareader import BookDataReader
from bookdatawriter import BookDataWriter
import argparse
import urllib.parse
import datetime
import os

def create_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scrapbooks",
        usage="scrapbooks [options] [url_to_scrape]",
        description="scraps book data found on given URL.")
    parser.add_argument(
        "scrape_url",
        nargs='?',
        default= "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
        help= "URL to scrape. see mode option as for how the URL will be interpreted."
        )
    parser.add_argument(
        "-o", "--output",
        required=False,
        default="",
        help= "specifies path to the output file."
        )
    parser.add_argument(
        "--mode",
        "-m",
        choices=['single', 'category', 'all'],
        default="single",
        help="scrape mode: single page, all pages of the same category, or all pages from the same base URL."
        )
    parser.add_argument(
        "--file",
        "-f",
        default="",
        help="for debugging purposes: sets a local HTML file as input, handled as a single scraping. This setting will ignore all others except ouptut."
    )

    return parser

def gen_output_file_name(scrape_url: str, extension: str= "csv") -> str:
    """
    generates a filename for the output csv, consistent with the scraped url and with a timestamp.
    """
    parts = urllib.parse.urlsplit(scrape_url)
    host = parts.netloc
    path = parts.path.replace('index.html', '')
    basename = host + '_' + path.strip('/').replace('/', '_')
    return append_timestamp(basename) + extension

def append_timestamp(in_str: str):
    now = datetime.datetime.now(datetime.timezone.utc)
    return in_str + '_' + now.strftime("%Y-%m-%d_%H-%M-%S")

if __name__ == "__main__":
    parser = create_arg_parser()
    args = parser.parse_args()
    if not args.file:
        scrape_url = args.scrape_url
        input_file = ''
        csv_output_file = args.output or ("./data/" + gen_output_file_name(scrape_url, '.csv'))
    else:
        scrape_url = ''
        input_file = args.file
        csv_output_file = args.output or ("./data/" + append_timestamp(os.path.basename(args.file)) + ".csv")

    print("scrape {0}".format(scrape_url or input_file))

    if scrape_url:
        # read book data from remote source...
        source = RemoteDataSource(scrape_url)
        book_html = source.read_text()
    elif input_file:
        # debugging with a local file...
        with open(input_file) as f:
            book_html = f.read()
    else:
        # woops...
        exit("Missing data source. Please specify URL to scrape or input HTML file.")

    # with open("./test_data/A-Light-in-the-Attic_Books-to-Scrape-Sandbox.html") as f:
    reader = BookDataReader()
    book = reader.read_from_html(book_html)
    book.product_page_url = scrape_url

    print("Export data as CSV to {0}".format(csv_output_file))

    writer = BookDataWriter(csv_output_file)
    if success := writer.append_data(book):
        print(f"wrote to {csv_output_file}")
    print("done.")

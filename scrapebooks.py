"""
openclassrooms Python - Project 2
bookscraper package
@author Christian Debray - christian.debray@gmail.com
"""
import argparse
import urllib.parse
import datetime
import os
import csv
import re
import time
from remotedatasource import RemoteDataSource
from bookdatareader import BookDataReader
from bookdatawriter import BookDataWriter
from scrapeindex import ScrapeIndex

def create_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scrapbooks",
        usage="scrapbooks [options] scrape_url",
        description="Scrap book catalog data found at the given URL.")
    parser.add_argument(
        "scrape_url",
        help= "URL to scrape. May be a single product page or a category page, or the URL of the full catalog index."
        )
    parser.add_argument(
        "-o", "--output",
        required=False,
        default="",
        help= "Specifies the path to the output file. If the output file already exists, marks the urls found in the file as scraped to avoid duplicate rows. Otherwise, or if omitted, generates a filename based on the scrape_url and the current timestamp."
        )
    parser.add_argument(
        "--file",
        "-f",
        default="",
        help="for debugging purposes: sets a local HTML file as input, handled as a single scraping. This setting will ignore all others and output the data to stdout."
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
    #
    # parse options
    #
    parser = create_arg_parser()
    args = parser.parse_args()

    #
    # set the CSV output file
    #
    output_base_dir = '.'
    csv_output_file = ''
    if args.output:
        if os.path.exists(args.output):
            if os.path.isdir(args.output):
                output_base_dir = args.output
            else:
                output_base_dir = os.path.dirname(args.output)
                csv_output_file = args.ouptut
        else:
            csv_output_file = args.output

    if not args.file:
        scrape_url = args.scrape_url
        input_file = ''
        if not csv_output_file:
            csv_output_file = os.path.join(output_base_dir, gen_output_file_name(scrape_url, '.csv'))
    else:
        scrape_url = ''
        input_file = args.file
        if not csv_output_file:
            csv_output_file = os.path.join(output_base_dir, append_timestamp(os.path.basename(args.file)) + ".csv")

    if input_file:
        # debugging with a local file...
        print(f"debugging with local file {input_file}:")
        with open(input_file) as f:
            book_html = f.read()
        reader = BookDataReader()
        book = reader.read_from_html(book_html)
        print(book)
        exit()
    elif len(scrape_url) == 0:
        # woops...
        exit("Missing data source. Please specify URL to scrape or input HTML file.")

    urls_index = ScrapeIndex()

    # if the output file already exists, add all referenced URLs to the set, and mark them as parsed.
    if os.path.exists(csv_output_file) and os.path.isfile(csv_output_file) and os.stat(csv_output_file).st_size > 0:
        with open(csv_output_file, "r") as f:
            csv_reader = csv.DictReader(f)
            for row in csv_reader:
                if url := row['product_page_url']:
                    urls_index.mark_url(url)
    #
    # Guess the page type from the path:
    #
    scrape_url = re.sub(r'/(index.[a-z]{2,4})?$', '', scrape_url) + '/'
    if scrape_url in ['https://books.toscrape.com/catalogue/category/books_1/', 'https://books.toscrape.com/']:
        print(f"scrape the entire catalog, export to {csv_output_file}")
        urls_index.load_generator_from_url(scrape_url)
    elif re.match(r'^https://books.toscrape.com/catalogue/category/books/[a-zA-Z0-9\-_]+/$', scrape_url):
        print(f"scrape a category, export to {csv_output_file}")
        urls_index.load_generator_from_url(scrape_url)
    else:
        print(f"scrape a single page, export to {csv_output_file}")
        urls_index.load_generator_from_list([scrape_url])

    data_source = RemoteDataSource()
    reader = BookDataReader()
    writer = BookDataWriter(csv_output_file)

    for url in urls_index.list_urls_to_scrape():
        print(f"scrape {url}")
        data_source.set_source(url)
        book_html = data_source.read_text()
        if book := reader.read_from_html(book_html):
            book.product_page_url = url
            if (book.is_valid()):
                if success := writer.append_data(book):
                    print(f"exported book data to csv file")
            else:
                print("Invalid book data, skip record.")
        time.sleep(2)
    
    print("done.")

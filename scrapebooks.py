"""
openclassrooms Python - Project 2
bookscraper package
@author Christian Debray - christian.debray@gmail.com
"""
import argparse
import urllib.parse
import datetime
import os
import re
from bookdatareader import BookDataReader
from bookdatawriter import BookDataWriter
from scraper import Scraper
from books_to_scrape_generators import BooksToScrapeGenerator
import logging
logger = logging.getLogger(__name__)

def create_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scrapbooks",
        usage="scrapbooks [options] scrape_url",
        description="Scrap book catalog data found at the given URL.",
        formatter_class=argparse.RawTextHelpFormatter
    )
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
    parser.add_argument(
        "--outputdir",
        "-d",
        help="""
Explicitely sets the output directory.
Can be any path, and may contain format codes to add a date or timestamp.

If set, the argument set with --output option will be interpreted as a
path relative to --outputdir.

Supports Python's date and time format codes.
(see https://docs.python.org/3/library/datetime.html#format-codes):

    %%Y current year with century as a decimal number
    %%m current month as a zero-padded decimal number
    %%d current day of the month as a zero-padded decimal number
    etc.

    ex.: scrapebook.py -d "path/to/outdir/scrap-%%Y-%%m-%%d

"""
    )
    parser.add_argument(
        "-T",
        "--append-date",
        action="store_true",
        default=False,
        help="Appends the current date to the ouptut directory. Combine this with -d."
    )
    parser.add_argument(
        "--verbosity",
        choices= [0, 1, 2],
        type= int,
        default = 0,
        help="verbosity level. 0 = errors only, 1 = info, 2 = debug. 0 is the default."
    )
    parser.add_argument(
        "-v",
        dest="verbosity",
        action="store_const",
        const=1,
        help="Sets verbosity level to 1 (info)"
    )
    parser.add_argument(
        "-q",
        dest="verbosity",
        action="store_const",
        const=0,
        help="Sets verbosity level to 0 (errors only)"
    )
    parser.add_argument(
        "-D",
        dest="verbosity",
        action="store_const",
        const=2,
        help="Sets verbosity level to 2 (debug)"
    )
    parser.add_argument(
        "-l",
        "--logfile",
        default="",
        help="Output logs to the specified logfile"
    )
    parser.add_argument(
        "--no-content",
        dest="nocontent",
        action="store_true",
        default=False,
        help="Don't scrape product contents, just extract the category and product URLs. Usually set for testing/debugging purposes."
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
    # set the CSV output parameters
    #

    # Set the ouptut directory

    # --outputdir option
    now = datetime.datetime.now(datetime.UTC)
    output_base_dir = '.'
    if args.outputdir:
        if str(args.outputdir).find("%") > 0:
            output_base_dir = now.strftime(args.outputdir)
        else:
            output_base_dir = args.outputdir

    # --output option
    csv_output_file = ''
    if args.output:
        if os.path.exists(args.output):
            if os.path.isdir(args.output):
                output_base_dir = args.output
            else:
                output_base_dir = os.path.dirname(args.output)
                csv_output_file = args.output
        else:
            output_base_dir = os.path.dirname(args.output)
            csv_output_file = args.output

    # --apend_date
    if len(output_base_dir) > 0 and output_base_dir != '.':
        if args.append_date:
            output_base_dir += now.strftime("_%Y-%m-%d")

    # create output directory if needed
    if not os.path.exists(output_base_dir):
        os.makedirs(output_base_dir, mode=0o777)

    # scrape_url argument
    if not args.file:
        scrape_url = args.scrape_url
        input_file = ''
    else:
        scrape_url = ''
        input_file = args.file
        if not csv_output_file:
            csv_output_file = os.path.join(output_base_dir, append_timestamp(os.path.basename(args.file)) + ".csv")

    #
    # configure logger
    #
    logger_config = {
        'level': logging.ERROR
    }
    if args.logfile:
        if not os.path.exists(args.logfile):
            logdir = os.path.dirname(args.logfile)
            if not os.path.exists(logdir):
                os.makedirs(logdir, mode=0o777)
            elif not os.access(logdir, os.W_OK):
                raise Exception("Can't write to logfile: directory is not accessible.")
        elif not os.path.isfile(args.logfile) or not os.access(args.logfile, os.W_OK):
            raise Exception("Can't write to logfile: Logfile is not an accessible or writable file.")
        logger_config['filename'] = args.logfile
    if args.verbosity > 0:
        lvls = {
            1: logging.INFO,
            2: logging.DEBUG
        }
        logger_config['level'] = lvls.get(args.verbosity, logging.NOTSET)
    logging.basicConfig(**logger_config)

    if input_file:
        # debugging with a local file...
        logger.info(f"debugging with local file {input_file}:")
        with open(input_file) as f:
            book_html = f.read()
        reader = BookDataReader()
        book = reader.read_from_html(book_html)
        print(book)
        exit()
    elif len(scrape_url) == 0:
        # woops...
        raise Exception("Missing data source. Please specify URL to scrape or input HTML file.")

    scraper_options = {
        'timeout': (3.5, 7),
        'requests_delay': 1.5,
        'output_dir': output_base_dir,
        'scraping_generator': BooksToScrapeGenerator()
    }

    if args.nocontent:
        def print_scraped_url(url: str = '', scrape_type: str = ''):
            print(f"{scrape_type}: {url}")
        scraper_options['mode'] = "scrape_urls"
        scraper_options['custom_url_handler'] = print_scraped_url
    scraper = Scraper(**scraper_options)

    #
    # Guess the scraping type from the path: entire catalog, category or single page
    #
    scrape_url = re.sub(r'/(index.[a-z]{2,4})?$', '', scrape_url) + '/'
    if scrape_url in ['https://books.toscrape.com/catalogue/category/books_1/', 'https://books.toscrape.com/']:
        logger.info(f"Scrape the entire catalog, export to {output_base_dir}")
        scraper.scrape_all_categories(scrape_url)
    elif re.match(r'^https://books.toscrape.com/catalogue/category/books/[a-zA-Z0-9\-_]+/$', scrape_url):
        logger.info(f"Scrape a category, export to {csv_output_file}")
        scraper.scrape_category(scrape_url, csv_output_file)
    else:
        # we need an output file...
        if not csv_output_file:
            csv_output_file = os.path.join(output_base_dir, gen_output_file_name(scrape_url, '.csv'))
        logger.info(f"Scrape a single page, export to {csv_output_file}")
        scraper.scrape_book(scrape_url, BookDataWriter(csv_output_file))
    
    logger.info("Done.")

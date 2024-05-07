# openclassrooms-bookscrap
Openclassrooms python course - project 2 - scraping tool

Scrape the product pages on https://books.toscrape.com

Our tool scrapes the data from a single product page, an entire category or the entire catalog.

This project relies on the Requests package to read content from remote sources and on BeautifulSoup 4 (bs4)
package to extract the relevant data. See requirements.txt for more infos on the dependencies.

## General workflow

1. The scraping process is launched from the command line via the `scrapebooks.py` script,
     which sets up the scraper (`scraper.py`). The scraping mode (single page, category or entire catalog)
     is guessed from the URL specified when invoking the script.

2. The `Scraper` class is instantiated and pilots the scraping process (see `scraper.py`)
    - When scraping the entire catalog, first read the list of category index pages
    (see the `ScrapeIndex` class in `scrapeindex.py`)

    - Pages to scrape are loaded by a single `RemoteDataSource` object to take advantage of sessions from the requests module.
    (see `remotedatasource.py`)

3. Initialize the scraping, for each category:
    - Load the category index with the `CategoryIndex` class (see `categoryindex.py`) in order to scrape all products pages referenced by the category.

4. Iterate scraping over each book referenced by the category:
    - Scrape each book's product page with the `BookDatareader` class. The relevant data is found with datasource-specific methods defined in the `BooksToScrapeGenerator` class (see `books_to_scrape_generators.py`)
    - Validate the data and store it inside a `BookData` object (see `bookdata.py`)
    - export scraped data as CSV with the `BookDataWriter` class (see `bookdatawriter.py`)
    - Finally download and store product image to the corresponding direactory

## Installation

first clone the repository:
```
    $ git clone git@github.com:christian-debray/openclassrooms-bookscrap.git
```

then create a pyhton virtual environment:
```
    $ cd openclassrooms-bookscrap
    $ python -m venv .env
    $ source ./env/bin/activate
```

finally, install all dependencies:
```
    $ pip install -r requirements.txt
```

## Usage
Once all packages and dependencies have been installed in a vritual environment:

```
$ python scrapbooks.py [options] [url_to_scrape]
```

### Some examples:

**normal usage: scrap a single category**

On may 2nd, 2024, this would produce no output, scrape book data of category "mystery" to directory data/scrape_cat_2024-05-02, and write INFO level logs to data/scraping_logs.log

```
python scrapebooks.py -l data/scraping_logs.log -v -T -d data/scrape_cat "https://books.toscrape.com/catalogue/category/books/mystery_3/"
```

**normal usage: scrap entire catalog**

Scrape the entire catalog and write data files to data/scraping_<current date>, no output to stdout, log warnings and errors to data/scraping_logs.log.

```
python scrapebooks.py -l data/scraping_logs.log -q -T -d data/scraping "https://books.toscrape.com"
```

**--no-content option**

Test url listing when scraping all categories, output the list to data/test_urls.txt, log info messages and errors to data/test_logs.log.
In this case, no CSV will be written, but the script will output the filenames that would have been written in normal mode.
```
python scrapebooks.py --no-content -l data/test_logs.log -v -d data/test -T "https://books.toscrape.com/" > data/test_urls.txt
```

**list urls to scrape**

Just print the urls to scrape to stdout as a list (1 url per line), and don't store any content to disk:
```
python scrapebooks.py --no-content -p -F "{url}" "https://books.toscrape.com/index.html"
```

### Command line arguments:
```
usage: scrapbooks [options] scrape_url

Scrap book catalog data found at the given URL.

positional arguments:
  scrape_url            URL to scrape. May be a single product page or a category page, or the URL of the full catalog index.

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Specifies the path to the output file. If the output file already exists, marks the urls found in the file as scraped to avoid duplicate rows. Otherwise, or if omitted, generates a filename based on the scrape_url and the current timestamp.
  --file FILE, -f FILE  for debugging purposes: sets a local HTML file as input, handled as a single scraping. This setting will ignore all others and output the data to stdout.
  --outputdir OUTPUTDIR, -d OUTPUTDIR
                        
                        Explicitely sets the output directory.
                        Can be any path, and may contain format codes to add a date or timestamp.
                        
                        If set, the argument set with --output option will be interpreted as a
                        path relative to --outputdir.
                        
                        Supports Python's date and time format codes.
                        (see https://docs.python.org/3/library/datetime.html#format-codes):
                        
                            %Y current year with century as a decimal number
                            %m current month as a zero-padded decimal number
                            %d current day of the month as a zero-padded decimal number
                            etc.
                        
                            ex.: scrapebook.py -d "path/to/outdir/scrap-%Y-%m-%d
                        
  -T, --append-date     Appends the current date to the ouptut directory. Combine this with -d.
  --verbosity {0,1,2}   verbosity level. 0 = errors only, 1 = info, 2 = debug. 0 is the default.
  -v                    Sets verbosity level to 1 (info)
  -q                    Sets verbosity level to 0 (errors only)
  -D                    Sets verbosity level to 2 (debug)
  -l LOGFILE, --logfile LOGFILE
                        Output logs to the specified logfile
  --no-content          Don't scrape product contents, just extract the category and product URLs. Usually set for testing/debugging purposes.
  --print-urls, -p      Ouptut the scraped urls to stdout, using the format specified by the -F option
  --print_urls-format PRINT_URLS_FORMAT, -F PRINT_URLS_FORMAT
                        Specify the format to use when printing urls. Accepts two fields in brackets: '{scrape_type}' and '{url}'.
```

## Output

The ouptut is stored to CSV files in an output directory specified from the command line.
Images found on the product pages are stored as well, in an images/ subdirectory.

Output directory file structure:

 - <output_dir_name>/
   - CSV files (1 CSV file per category)
   - images/
      - <category_name>/
        - image files in JPEG format (1 book = 1 image file named after the book's Universal Product Code)

## Handling existing data
If an existing output file is specified, or a CSV file is found in the specified output directory,
then the scraping process will skip the URLs found in the existing file to avoid duplicate content and append the new URLs.

## Data validation

The scraper performs some basic data filtering to ensure data integrity on the fly (see the `BookData` class in `bookdata.py`).

However, once the scraping process is completed, we can also check the quality of the scraped data with an additional tool provided with this package:
**validate.py**.

This tool requires an additional data file, mapping the expected category names with the expected number of books per category.



```
usage: validate [-h] -d DATA_DIRECTORY --categories-specs CATEGORIES_SPECS
                [--validate-categories VALIDATE_CATEGORIES [VALIDATE_CATEGORIES ...]]

validate scraping data found in directory

options:
  -h, --help            show this help message and exit
  -d DATA_DIRECTORY     Path to the base directory where the scraping data is stored.
  --categories-specs CATEGORIES_SPECS, -s CATEGORIES_SPECS
                        path to a csv file listing category names and expected produtc counts.
  --validate-categories VALIDATE_CATEGORIES [VALIDATE_CATEGORIES ...]
                        Specify categories to validate as a space separated list of category names.
```

example:

```
$ python validate.py -d data/scraping_2024-05-03 --categories-spec test_data/categories.csv
```
If the data stored in data/scraping_2024-05-03, the validation script will ouptut:
```
Starting validation...

    Validated:
        50/50 categories
        1000/1000 products
        1000/1000 images
    
Data is valid !
```
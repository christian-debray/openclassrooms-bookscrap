# openclassrooms-bookscrap
Openclassrooms python course - project 2 - scraping tool

(work in progress...)

Scrapes the data from a single product page, an entire category or the entire catalog.
The ouptut is stored to a CSV file.
If an existing output file is specified, then the scraping process will skip the URLs found in the existing file to avoid duplicate content and append the new URLs.

The scraper performs some basic data filtering.

## Usage
once all packages and dependencies have been installed in a vritual environment:

```
$ python scrapbooks.py [options] [url_to_scrape]
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
                        Specifies the path to the output file. If the output file already exists, marks the urls found in the file
                        as scraped to avoid duplicate rows. Otherwise, or if omitted, generates a filename based on the scrape_url
                        and the current timestamp.
  --file FILE, -f FILE  for debugging purposes: sets a local HTML file as input, handled as a single scraping. This setting will
                        ignore all others and output the data to stdout.
  --verbosity {0,1,2}   verbosity level. 0 = no logs, 1 = info, 2 = debug. 0 is the default.
  -v                    Sets verbosity level to 1 (info)
  -q                    Sets verbosity level to 0 (info)
  -D                    Sets verbosity level to 2 (debug)
  -l LOGFILE, --logfile LOGFILE
                        Output logs to the specified logfile
```

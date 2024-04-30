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

  - **url_to_scrape:**
    a URL to scrape. May be a single product page or a category page, or the URL of the full catalog index.

options:
| option | description |
|--------|-------------|
| -h, --help | show this help message and exit |
| -o OUTPUT, --output OUTPUT | Specifies the path to the output file. If the output file already exists, marks the urls found in the file as scraped to avoid duplicate rows. Otherwise, or if omitted, generates a filename based on the url_to_scrape and the current timestamp. |
| --file FILE, -f FILE | for debugging purposes: sets a local HTML file as input, handled as a single scraping. This setting will ignore all others and print the scraped data to stdout |

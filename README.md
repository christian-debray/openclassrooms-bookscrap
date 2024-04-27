# openclassrooms-bookscrap
Openclassrooms python course - project 2 - scraping tool

(work in progress...)

So far, we can read the data form one book.
For the moment, book URL is hard-coded in scrapebooks.py

## Usage
once all packages and dependencies have been installed in a vritual environment:

`$ python scrapbooks.py [options] [url_to_scrape]`

### Command line arguments:

  - **scrape_url:**
    an URL to scrape. see mode option as for how the URL will be interpreted.

options:
| option | description | default |
|--------|-------------|---------|
| -h, --help | show this help message and exit | |
| -o OUTPUT, --output OUTPUT | specifies path to the output file. | If empty, the file will be stored in the "data" subdir and and named after the input url/file with a timestamp. |
| --mode {single,category,all}, -m {single,category,all} | scrape mode: single page, all pages of the same category, or all pages from the same base URL. | https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html |
| --file FILE, -f FILE | for debugging purposes: sets a local HTML file as input, handled as a single scraping. This setting will ignore all others except ouptut. | |

If the output file doesn't exist, creates the file and adds the CSV headers before appending the data.

# openclassrooms-bookscrap
Openclassrooms python course - project 2 - scraping tool

(work in progress...)

So far, we can read the data form one book.
For the moment, book URL is hard-coded in scrapebooks.py

## Usage
once all packages and dependencies have been installed in a vritual environment:

    `$ python scrapebooks.py`

Reads book data from https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html
and appends the scraped data to data/test_book.csv

If the file doesn't exist, creates the file and adds the CSV headers before appending the data.

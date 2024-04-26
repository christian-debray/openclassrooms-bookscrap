"""
openclassrooms Python - Project 2
bookscraper package
@author Christian Debray - christian.debray@gmail.com
"""

class BookDataMapping:
    """
    static class holding mapping info
    to extract book data from an HTML doc on https://books.toscrape.com/
    We map each field of our book data to a (hopefuly) unique CSS selector
    """
    product_page_url_selector = None
    title_selector = "#content_inner > article.product_page > div.row > div.product_main > h1"
    universal_product_code_selector = "#content_inner > article.product_page > table > tbody > tr:nth-child(1) > td"
    price_including_tax_selector = "#content_inner > article.product_page > .table > tbody:nth-child(1) > tr:nth-child(4) > td:nth-child(2)"
    price_excluding_tax_selector = "#content_inner > article.product_page > .table > tbody:nth-child(1) > tr:nth-child(3) > td:nth-child(2)"
    # <i></i>  In stock (22 available)
    number_available_selector = "#content_inner > article.product_page > div.row > div.product_main > p.instock.availability"
    product_description_selector = "#content_inner > article.product_page > p"
    category_selector = ".breadcrumb > li:nth-child(3) > a:nth-child(1)"
    # review_rating: read the second class name of p.start_rating (One, Two, Three, Four, Five)
    review_rating_selector = "#content_inner > article > div.row > div.col-sm-6.product_main > p.star-rating"
    # read the src attribute
    image_url_selector = "#product_gallery .item > img:nth-child(1)"

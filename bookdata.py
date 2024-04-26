"""
openclassrooms Python - Project 2
bookscraper package
@author Christian Debray - christian.debray@gmail.com
"""

class BookData:
    """
    Data Transport object holding book data object.
    """
    def __init__(self):
        self.product_page_url: str = ""
        self.universal_product_code: str = ""
        self.title: str = ""
        self.price_including_tax: float = 0.0
        self.price_excluding_tax: float = 0.0
        self.number_available: int = 0
        self.product_description: str = ""
        self.category: str = ""
        self.review_rating: int = 0
        self.image_url: str = ""

    def export(self):
        """
        export this book's data as a dictionary
        """
        d = {
            "product_page_url": self.product_page_url,
            "universal_product_code": self.universal_product_code,
            "title": self.title,
            "price_including_tax": self.price_including_tax,
            "price_excluding_tax": self.price_excluding_tax,
            "number_available": self.number_available,
            "product_description": self.product_description,
            "category": self.category,
            "review_rating": self.review_rating,
            "image_url": self.image_url
        }
        return d

    def __repr__(self):
        return repr(self.export())


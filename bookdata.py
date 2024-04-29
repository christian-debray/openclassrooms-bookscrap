"""
openclassrooms Python - Project 2
bookscraper package
@author Christian Debray - christian.debray@gmail.com
"""
import re
import locale

class BookData:
    """
    Data Transport object holding book data object.
    Provides some basic data validation, except for product_page url and image_url.
    
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

    @classmethod
    def filter_universal_product_code(self, input_v) -> str:
        """
        Filters input and returns a valid universal product code, or empty string.
        valid if alphanumeric string.
        """
        filtered = str(input_v).strip()
        pattern = r'^[a-z0-9]+$'
        return filtered if re.match(pattern, filtered) else ""

    @classmethod
    def filter_title(self, input_v) -> str:
        """
        Filters a book title and returns the filtered value.
        All values accepted, just strips leading and ending spaces.
        """
        return str(input_v).strip()

    @classmethod
    def filter_price(self, input_v, loc: str= '') -> float:
        """
        Filters price value and returns the price as a float, or 0.0.
        Expects a valid representation of a positive float or a positive price with a preceeding currency symbol.
        
        The input value may be locale dependent.
        This method relies on Python's locale module to parse the input string,
        and uses the default locale (as returned by locale.getlocale()).
        
        The locale can be forced with the second parameter.

        valid input ex.:
        £5612.67
        £ 5,612.67
        € 5 612,67

        invalid prices:
        -£5612.67
        £ -5612.67
        2425%
        £132.22.2425
        """
        if loc:
            old_locale = locale.getlocale()
            locale.setlocale(locale.LC_ALL, loc)
        try:
            # 1. check the input is a valid representation of a price
            # 2. strip the optional leading currency symbol
            # 3. finally interpret the numeric string according to locale conventions
            patt = re.compile(r'^[^\d.,\-]{0,3}\s?([0-9,.\s]+)$')
            trim = re.compile(r'\s')
            if match := patt.fullmatch(str(input_v).strip()):
                # locale.delocalize() removes the thousands separator
                filtered = locale.delocalize(trim.sub('', match.group(1)))
                # correctly interpret the radix character
                return locale.atof(filtered)
            else:
                return 0.0
        except Exception:
            return 0.0
        finally:
            if loc:
                locale.setlocale(locale.LC_ALL, f"{old_locale[0]}.{old_locale[1]}")

    @classmethod
    def filter_number_available(self, input_v) -> int:
        """
        filters a number_available value. Expects a representation of a positive int.
        Returns the filtered input, or 0 if input is not valid.
        """
        return self.filter_positive_integer(input_v)

    @classmethod
    def filter_positive_integer(self, input_v) -> int:
        try:
            filtered = int(str(input_v).strip())
            return filtered if filtered > 0 else 0
        except Exception:
            return 0

    @classmethod
    def filter_category(self, input_v) -> str:
        """
        filter the category string
        """
        patt = re.compile(r'^[\w\- ]+$')
        filtered = str(input_v).strip()
        return filtered if patt.match(filtered) else ""

    @classmethod
    def filter_review_rating(self, input_v) -> int:
        """
        filters the review rating. Expects a representation of a positive integer between 0 and 5.
        """
        f = self.filter_positive_integer(input_v)
        return f if (f >= 0 and f <= 5) else 0

    def is_valid(self):
        """
        Returns True if the data held by this object is considered valid and safe for further processing.
        Checks for required fields to be set.
        """
        return len(self.universal_product_code) > 0

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


if __name__ == "__main__":
    # test data filters:
    universal_product_code_tests = {
        'ae562df677njdv': 'ae562df677njdv',
        " \t\n  ae562df677njdv \t \r\n": 'ae562df677njdv',
        "ehfh  565": "",
        "\n": ""
    }
    for t, e in universal_product_code_tests.items():
        filtered = BookData.filter_universal_product_code(t)
        assert filtered == e, f'filter_universal_product_code({t}) = {filtered} != {e}'

    locale.setlocale(locale.LC_ALL, '')
    price_tests = {
        "£5612.67":  5612.67,
        "£ 5,612.67": 5612.67,
        "€ 5\u202f612,67": 5612.67,
        "€ 5 612,67": 5612.67,
        "": 0.0,
        "12": 12.0,
        "12.56": 12.56,
        "12,56": 1256,
        "£ 5675/234.567:13": 0.0,
        "£132.22.2425": 0.0,
        "(5, 7": 57.0,
        "_676868": 676868,
        "123_69": 0.0,
        ".58": 0.58,
        "EUR 6786.66": 6786.66,
        "EUR 6,786.66": 6786.66,
        "£ -5612.67": 0.0,
        "-5612.67": 0.0,
        1234.56: 1234.56,
        -1234.56: 0.0
        }
    for p, expected in price_tests.items():
        l = "fr_FR.UTF-8" if (str(p).find('€') >= 0) else "en_GB.UTF-8"
        filtered = BookData.filter_price(p, l)
        assert filtered == expected, f"filter_price({p}) = {filtered} != {expected}"

    available_tests = {
        '12': 12,
        '12.56': 0,
        '1+3': 0,
        '0o777': 0,
        '-42': 0
    }
    for t, e in available_tests.items():
        filtered = BookData.filter_number_available(t)
        assert filtered == e, f"filter_number_available({t}) = {filtered} != {expected}"
    
    category_tests = {
        "Autobiography": "Autobiography",
        "   Autobiography  ": "Autobiography",
        "Sports and Games": "Sports and Games",
        "Sports-and-Games": "Sports-and-Games",
        "Sports\u0020and Games": "Sports and Games",
        "Sports\u200band Games": "",
        123: "123",
        123.56: "",
        "123,56": "",
        "-42": "-42"
    }
    for t, e in category_tests.items():
        filtered = BookData.filter_category(t)
        assert filtered == e, f"filter_category({t}) = {filtered} != {e}"

    review_tests = {
        0: 0,
        "1": 1,
        True: 0,
        42: 0,
        "4.678": 0,
        -4: 0,
        "-4": 0,
        " \t 4  \n ": 4
    }

    for t, e in review_tests.items():
        filtered = BookData.filter_review_rating(t)
        assert filtered == e, f"filter_review_rating({t}) = {filtered} != {e}"
    print("Test completed")
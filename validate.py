import os
import re
import csv
import argparse
import logging
logger = logging.getLogger(__name__)

class ScrapingDataValidator:
    """
    Validate data produced by the scraping utility
    """
    def __init__(self, data_dir: str, expected_categories: dict[str, int], expected_product_fields: dict[str, str]):
        self.data_dir = data_dir
        self.expected_categories = expected_categories
        self.expected_product_fields = expected_product_fields
        if not os.path.exists(self.data_dir) or not os.path.isdir(self.data_dir):
            raise FileNotFoundError("Data directory not found")
        self.errors = []
        # Some parameters used by csv.DictReader:
        self._csv_format = {
            'delimiter' : ",",
            'quotechar' : '"',
            'escapechar' : "\\"
        }
        self._restval_error_str = "__MISSING.FIELD.ERROR__"
        self._restkey = "overflow"
        self._count_validated_categories = 0
        self._count_validated_products = 0
        self._count_validated_images = 0

    def _validation_error(self, error_msg):
        print(error_msg)
        self.errors.append(error_msg)

    def validate_all(self):
        """
        Validate all the data found in data_dir.
        expected_categories -- map category names
        (as spelled on the website) to the expected number of books
        """
        self.errors = []
        for cat_name, cat_product_count in self.expected_categories.items():
            self.validate_category_contents(cat_name, cat_product_count)
        return len(self.errors) == 0

    def validate_category_contents(self, category_name: str, expected_product_count: int):
        """
        Validate one category:

        - check the corresponding CSV filename is found in the data directory
        - check CSV format
        - check row count
        - check existence of image file for each product
        """
        logger.info(f"Validating category {category_name}...")
        self._count_validated_categories += 1
        category_csv_path = self._expected_category_csv_path(category_name)
        category_images_path = self._expected_category_image_dir(category_name)
        if not os.path.exists(category_csv_path):
            self._validation_error(f"Missing CSV file for category {category_name} - expected: {category_csv_path}")
            return
        validate_images = True
        if not os.path.exists(category_images_path) or not os.path.isdir(category_images_path):
            self._validation_error(f"Can't find images directory for category {category_name} - expected: {category_images_path}")
            validate_images = False
        
        with open(category_csv_path, "r") as csv_f:
            try:
                cat_csv_reader = csv.DictReader(csv_f, strict=True, restkey= self._restkey, restval=self._restval_error_str, **self._csv_format)
                row_count = 0
                for row in cat_csv_reader:
                    if row_count == 0:
                        if not self._validate_csv_fields(
                            csv_filename= category_csv_path,
                            field_list= list(row.keys()),
                            expected_fields= self.expected_product_fields):
                                return
                    row_count += 1
                    self._validate_product_row(
                        row = row,
                        row_n = row_count,
                        category_name= category_name,
                        category_csv_path= category_csv_path,
                        category_images_path = category_images_path,
                        validate_images= validate_images
                    )

                if row_count != expected_product_count:
                    self._validation_error(f"Wrong product count for category {category_name} in {category_csv_path}. Expected {expected_product_count}, found {row_count}")
            except csv.Error as csv_err:
                self._validation_error(f"Malformed CSV file {category_csv_path}: {csv_err}")

    def _validate_csv_fields(self, csv_filename: str, field_list: list[str], expected_fields: list[str]) -> bool:
        """
        Validates the field names found in a CSV file.
        """
        f1 = set(field_list)
        f_r = set(expected_fields)
        missing_fields = f_r.difference(f1)
        unexpected_fields = f1.difference(f_r)
        if len(missing_fields) > 0:
            self._validation_error("Missing fields in CSV file {0}: {1}".format(csv_filename, ", ".join(missing_fields)))
        if len(unexpected_fields) > 0:
            self._validation_error("Unexpected fields in CSV file {0}: {1}".format(csv_filename, ", ".join(unexpected_fields)))
        return 0 == len(missing_fields) + len(unexpected_fields)

    def _validate_product_row(self, row: dict, row_n: int, category_name: str, category_csv_path: str, category_images_path: str, validate_images: bool = True):
        """
        Validates a single row from a CSV file.
        Checks for product image as well when the validate_image parameter is set to True.
        """
        self._count_validated_products += 1
        for field_n in self.expected_product_fields:
            if row.get(field_n) == self._restval_error_str:
                self._validation_error(f"Field not set for product at row #{row_n}: {field_n} (in category {category_name}, {category_csv_path})")
        if row.get(self._restkey, None) is not None:
            self._validation_error(f"Malformed record at row #{row_n} (in category {category_name}, {category_csv_path})")
        if validate_images and (product_code := row.get("universal_product_code", None)):
            self._count_validated_images += 1
            expected_img_file = os.path.join(category_images_path, f"{product_code}.jpeg")
            if not os.path.exists(expected_img_file) or not os.path.isfile(expected_img_file):
                self._validation_error(f"Image file not found for product {product_code} at row #{row_n} (in category {category_name}, {category_csv_path})")

    def _expected_category_csv_path(self, category_name: str) -> str:
        """
        Returns the full path to category csv file.
        """
        return os.path.join(self.data_dir, self._expected_category_basename(category_name, '.csv'))
    
    def _expected_category_image_dir(self, category_name: str) -> str:
        """
        Returns the full path to catgeory image directory.
        """
        return os.path.join(self.data_dir, 'images', self._expected_category_basename(category_name))

    def _expected_category_basename(self, category_name: str, extension: str = "") -> str:
        """
        Return the expected basename for a category.
        """
        return re.sub(r'[\s/]+', '_', category_name) + extension

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    parser = argparse.ArgumentParser(
        prog="validate",
        description="validate scraping data found in directory",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "-d",
        required = True,
        dest= "data_directory",
        help="Path to the base directory where the scraping data is stored."
    )
    parser.add_argument(
        "--categories-specs",
        "-s",
        required= True,
        dest="categories_specs",
        help="path to a csv file listing category names and expected produtc counts."
    )
    parser.add_argument(
        "--validate-categories",
        dest="validate_categories",
        action="extend",
        nargs="+",
        type= str,
        default = [],
        help="Specify categories to validate as a space separated list of category names."
    )
    args = parser.parse_args()

    # expected fields in categories_specs_csv: ["category", "product_count"]
    with open(args.categories_specs, "r") as categories_specs_csv:
        cat_specs_reader = csv.DictReader(categories_specs_csv)
        expected_categories = {}
        if cat_specs_reader.fieldnames != ['category', 'product_count']:
            raise Exception("Wrong categories spec format. Expecting columns 'category' and 'product_count'")
        for row in cat_specs_reader:
            expected_categories[row.get("category")] = int(row.get("product_count"))
    
    expected_product_fields = [
        "product_page_url",
        "universal_product_code",
        "title",
        "price_including_tax",
        "price_excluding_tax",
        "number_available",
        "product_description",
        "category",
        "review_rating",
        "image_url"]
    validator = ScrapingDataValidator(
        data_dir= args.data_directory,
        expected_categories= expected_categories,
        expected_product_fields= expected_product_fields)
    
    print("Starting validation...")
    if len(args.validate_categories) == 0:
        validator.validate_all()
        total_expected_categories = len(expected_categories)
        total_expected_products = sum(list(expected_categories.values()))
        total_expected_images = total_expected_products
    else:
        for cat in args.validate_categories:
            validator.validate_category_contents(cat, expected_categories[cat])
        total_expected_categories = len(args.validate_categories)
        total_expected_products = sum([expected_categories[c] for c in args.validate_categories])
        total_expected_images = total_expected_products
    summary= f"""
    Validated:
        {validator._count_validated_categories}/{total_expected_categories} categories
        {validator._count_validated_products}/{total_expected_products} products
        {validator._count_validated_images}/{total_expected_images} images
    """
    print(summary)
    if len(validator.errors) > 0:
        print("Validation Failed! Found at least {0} errors in {1}".format(len(validator.errors), validator.data_dir))
    else:
        print("Data is valid !")

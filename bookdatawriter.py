"""
openclassrooms Python - Project 2
bookscraper package
@author Christian Debray - christian.debray@gmail.com
"""
from bookdata import BookData
import os, pathlib
import csv

class BookDataWriter:
    """
    Export Book Data objects to a CSV file
    """
    def __init__(self, filename: str):
        # check path to output file exists and is writable
        path = os.path.dirname(filename) or os.path.curdir()
        self.path = os.path.abspath(path)
        if not(os.path.exists(path) and os.access(path, os.W_OK)):
            raise FileNotFoundError("Can't output to CSV file: base dir is not accessible (check the base directory exists and is writable)")
        self.basename = os.path.basename(filename)
        self.full_file_path = os.path.join(path, self.basename)
        if os.path.exists(self.full_file_path) and not os.access(self.full_file_path, os.W_OK):
            raise FileNotFoundError("Existing output file is not writable.")
        if os.path.exists(self.full_file_path) and not os.path.isfile(self.full_file_path):
            raise FileExistsError("Ouptut path is not a file")
        
        self.delimiter = ","
        self.newline = ""
        self.quotechar='"'
        self.escapechar="\\"
        # create an empty book to set the CSV field names
        b = BookData()
        self.csv_fields = b.export().keys()

    def append_data(self, book_data: BookData):
        """
        writes the data found in a BookData object to the end of the ouptut csv file
        """
        if not os.path.exists(self.full_file_path):
            p = pathlib.Path(self.full_file_path)
            p.touch(0o666)

        with open(self.full_file_path, newline=self.newline, mode="a") as f:
            writer = csv.DictWriter(f, fieldnames=self.csv_fields, delimiter=self.delimiter, quotechar=self.quotechar, escapechar=self.escapechar)
            # if the file is empty, also add a header
            stat = os.stat(self.full_file_path)
            if stat.st_size == 0:
                writer.writeheader()
            # now write the actual data
            success = writer.writerow(book_data.export())

        return success
    

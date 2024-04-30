"""
openclassrooms Python - Project 2
bookscraper package
@author Christian Debray - christian.debray@gmail.com
"""
import requests

class RemoteDataSource:
    """
    wrap remote connection utility
    """

    def __init__(self, url: str = None):
        self.url:str
        self.response: requests.Response
        self.session: requests.Session = requests.session()
        if url:
            self.set_source(url)

    def set_source(self, url: str) -> requests.Response:
        """
        Connects to a remote data source and stores the response.
        raises an HTTPError if connection error occured.
        """
        self.url = url
        self.response = self.session.get(self.url, timeout= 1.0)
        self.final_url = self.response.url
        if self.response.status_code != requests.codes.ok:
            self.response.raise_for_status()
        return self.response

    def source_url(self) -> str:
        """
        Returns the URL of the current data source
        """
        return self.response.url if self.response else None

    def read_text(self, url: str = None) -> str:
        """
        Reads text content from a source URL.
        Returns the content as a string.
        """
        if url:
            self.set_source(url)
        return self.response.content

if __name__ == "__main__":
    ds = RemoteDataSource('https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html')
    assert(isinstance(ds.response, requests.Response))
    assert(ds.response.status_code == requests.codes.ok)
    content = ds.read_text()
    assert(len(content) > 0)
    print("extracted {0} characters. First 100:\n{1}\n{2}".format(len(content), content[:100], '(...)' if len(content) > 100 else ''))

    err: Exception = None
    try:
        ds.set_source('https://books.toscrape.com/not/found/foo/bar')
    except requests.HTTPError as e:
        err = e
        print("Request failed (HTTP error): ", err)
    except Exception as e:
        err = e
        print("Request failed: ", err)
    assert(err is not None)


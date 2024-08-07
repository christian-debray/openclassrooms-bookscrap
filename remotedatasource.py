"""
openclassrooms Python - Project 2
bookscraper package
@author Christian Debray - christian.debray@gmail.com
"""
import requests
import time
import functools
import logging
import re
logger = logging.getLogger(__name__)

def max_attempts_decorator(max_attempts):
    """
    Limit attempts when connecting to a remote URL.
    Abort when timeouts occur max_attempts times.
    """
    def decorate_max_attempts(func):
        @functools.wraps(func)
        def wrapper_max_attempts(*args, **kwargs):
            for attempts in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except (requests.ReadTimeout, requests.ConnectTimeout, requests.Timeout, requests.ConnectionError) as t_err:
                    if attempts < max_attempts:
                        logger.warning("Connection timed out, trying again...")
                    else:
                        logger.error("Connection timed out, max attempts reached. Abandon.", exc_info=True)
                        return False
        return wrapper_max_attempts
    return decorate_max_attempts


class RemoteDataSource:
    """
    wrap remote connection utility
    """

    def __init__(self, url: str = None, requests_delay: float = 0, timeout = (3.05, 6.05)):
        self.url:str
        self.response: requests.Response
        self.session: requests.Session = requests.session()
        self.requests_delay: float = requests_delay
        self._timeout = timeout
        if url:
            self.set_source(url)

    def set_source(self, url: str) -> requests.Response:
        """
        Connects to a remote data source and stores the response.
        raises an HTTPError if connection error occured.
        """
        if self.requests_delay > 0:
            time.sleep(self.requests_delay)
        self.url = url
        self.response = self.session.get(self.url, timeout= self._timeout)
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
        #
        # TODO: handle encoding
        #
        return self.response.text

    def fetch_binary(self, url: str = None) -> bytes:
        """
        fetches binary content
        """
        if url:
            self.set_source(url)
        return self.response.content

    def mime_type(self) -> tuple[str, str]:
        """
        Returns the content Type of the response as a string as a tuple: (type, subtype)
        see https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types#important_mime_types_for_web_developers
        """
        if self.response and self.response.status_code == requests.codes.ok:
            if type_match := re.match(r'(image|text)/([a-z\+]+)', self.response.headers['content-type']):
                return (type_match.group(1), type_match.group(2))
        return None

if __name__ == "__main__":
    ds = RemoteDataSource('https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html')
    assert(isinstance(ds.response, requests.Response))
    assert(ds.response.status_code == requests.codes.ok)
    content = ds.read_text()
    assert(len(content) > 0)
    print("extracted {0} characters. First 100:\n{1}\n{2}".format(len(content), content[:100], '(...)' if len(content) > 100 else ''))

    print(ds.mime_type())

    ds.set_source("https://books.toscrape.com/media/cache/fe/72/fe72f0532301ec28892ae79a629a293c.jpg")
    print(ds.mime_type())

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


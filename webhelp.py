#!/usr/bin/env python3
# webhelp.py - Web functions helping Module by Sergey 2014
# Pylib - Python useful modules (github.com/snsokolov/pylib)

"""
Accessing web helping functions module

"""

# Standard modules
import unittest
import unittest.mock
import sys
import os
import argparse
import re
import random
import subprocess
import getpass
import shutil
import tempfile

# Additional modules
import urllib.request
import random
import warnings


###############################################################################
# Webhelp Class
###############################################################################


class Webhelp(urllib.request.FancyURLopener, object):
    """ Customized version of Fancy URL opener """

    user_agents = [
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) " +
        "Gecko/20071127 Firefox/2.0.0.11",

        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; " +
        "SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",

        "Mozilla/5.0 (compatible; Konqueror/3.5; Linux) " +
        "KHTML/3.5.5 (like Gecko) (Kubuntu)",

        "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) " +
        "Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12",
    ]

    version = random.choice(user_agents)

    def __init__(self):
        warnings.simplefilter("ignore", DeprecationWarning)
        urllib.request.FancyURLopener.__init__(self)

###############################################################################
# Executable code
###############################################################################


def get_page_str(url):
    """Return web page content using a custom version of URL opener."""
    page = Webhelp().open(url)
    page_str = str(page.read())
    page.close()
    return page_str


def get_url_dir(url):
    """Return the url directory - url minus the text after last '/'."""
    return re.sub("[^/]*$", "", url)

def get_url_(url):
    """Return the url directory name - url minus the text after last '/'."""
    return re.sub("[^/]*$", "", url)


def download_file(url, target_dir="", prefix=""):
    """Download file from the url."""
    print("Downloading: ", url)
    file_name = url.split("/")[-1]
    if prefix:
        file = prefix + file_name
    else:
        file = file_name
    if target_dir:
        # Create the target directory if not exists.
        if not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)
        file = target_dir + "/" + file
    try:
        print(file)
        Webhelp().retrieve(url, file)
    except ValueError:
        # Don't leave empty files
        os.remove(file)
        return 0
    return 1


def get_linked_img_urls(page_str, url_dir=""):
    """Return urls of all linked images in the page string."""
    regexp = "<a [^>]*href=[\"]?(\S+\.jp[e]?g)[^>]*><img"
    urls = re.findall(regexp, page_str, re.I)
    for (i, url) in enumerate(urls):
        if not re.match("^http", url):
            urls[i] = url_dir + url
    return urls


def download_linked_imgs(url, target_dir="", prefix=""):
    """Download all linked images from url provided """
    page_str = get_page_str(url)
    urls = get_linked_img_urls(page_str, get_url_dir(url))
    for url in urls:
        download_file(url, target_dir, prefix)
    if not urls:
        print("W: No linked imgs found.")


def download_dir(dir_url, start, stop, target_dir="", prefix=""):
    """Download files in the directory."""
    for num in range(start, stop+1):
        num_str = str(num)
        # Padding
        if num < 10:
            num_str = "0" + num_str
        file_url = dir_url + "/" + num_str + ".jpg"
        status = download_file(file_url, target_dir, prefix)
        if not status:
            if num == start:
                print("W: Can't download dir %s, breaking the loop" % dir_url)
                return 0

            print("W: Can't download %s, breaking the loop" % file_url)
            break
    return 1


def download_dirs(dirs_url, target_dir, start, cnt=1, dir_start=0, dir_stop=200, ):
    """Download directory of directories."""
    for num in range(start, start+cnt):
        num_str = str(num)
        # Padding
        if num < 10:
            num = "0" + num_str
        dir_url = dirs_url + "/" + num_str
        status = download_dir(dir_url, dir_start, dir_stop, target_dir, num_str+"_")
        if not status:
            break



###############################################################################
# Unit Tests
###############################################################################


class unitTests(unittest.TestCase):

    IMG_URL = "http://www.google.com/images/srpr/logo11w.png"

    def test_Webhelp_class_retrieve(self):
        """Webhelp class URL retrieve."""
        d = Webhelp()
        (file, headers) = d.retrieve(self.IMG_URL)
        self.assertGreater(os.path.getsize(file), 0)
        os.remove(file)

    def test_get_url_dir(self):
        self.assertEqual(get_url_dir("fdfd/fdf.ht"), "fdfd/")

    def test_download_file(self):
        """Download a file from url and add a prefix."""
        with tempfile.TemporaryDirectory() as temp_dir:
            download_file(self.IMG_URL, temp_dir, "prefix_")
            self.assertTrue(os.path.exists(temp_dir + "/prefix_logo11w.png"))

    def test_download_file_bad_address(self):
        """Download a file from bad address"""
        with tempfile.TemporaryDirectory() as temp_dir:
            download_file("http://www.google.com/images/srpr/l.png", temp_dir)
            self.assertEqual(len(os.listdir(temp_dir)), 0)

    def test_get_linked_urls(self):
        """Detect linked urls."""
        page_str = (
            "<><a fd href=http:/d.jpg cvc><img fdg>" +
            "df<A href=\"f.jpeg\" ><img f>")
        self.assertEqual(
            get_linked_img_urls(page_str), ["http:/d.jpg", "f.jpeg"])
        self.assertEqual(
            get_linked_img_urls(page_str, url_dir="a/"),
            ["http:/d.jpg", "a/f.jpeg"])

    @unittest.mock.patch.object(Webhelp, 'open')
    @unittest.mock.patch.object(Webhelp, 'retrieve')
    def test_webhelp_functions(self, mock_retrieve, mock_open):
        """Web Helping functions testing."""
        with tempfile.TemporaryFile('r+') as temp_file:
            temp_file.write("<><a fd href=1.jpg><img dd>")
            temp_file.seek(0)
            mock_open.return_value = temp_file
            with tempfile.TemporaryDirectory() as temp_dir:
                download_linked_imgs("http://one/too/g.html", temp_dir, "prf_")
                mock_retrieve.assert_called_with("http://one/too/1.jpg",
                                                 temp_dir+"/prf_1.jpg")
                mock_open.assert_called_with("http://one/too/g.html")


if __name__ == "__main__":
    if sys.argv[-1] == "-ut":
        unittest.main(argv=[" "])

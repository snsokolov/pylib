#!/usr/bin/env python
# webhelp.py - Web functions helping Module
#
# Copyright (C) 2014 Sergey Sokolov, License MIT

"""
Accessing web helping functions module

"""

# Standard modules
import unittest
import sys
import os
import argparse
import re
import random
import subprocess
import getpass
import shutil

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
    """ Return web page content using a custom version of URL opener """
    page = Webhelp().open(url)
    page_str = str(page.read())
    page.close()
    return page_str


def get_url_dir(url):
    """ Return the url directory name """
    return re.sub("[^/]*$", "", url)


def download_file(url, prefix="", target_dir=""):
    """ Download file from the url """
    filename = url.split("/")[-1]
    if prefix:
        filename = prefix + filename
    if target_dir:
        filename = target_dir + "/" + filename
    Webhelp().retrieve(url, filename)


def get_linked_img_urls(page_str, prefix=""):
    """ Return urls of all linked images in the page string """
    regexp = "<a [^>]*href=[\"]?(\S+\.jp[e]?g)[^>]*><img"
    urls = re.findall(regexp, page_str, re.I)
    for (i, url) in enumerate(urls):
        if not re.match("http", url):
            urls[i] = prefix + url
    return urls


def download_linked_imgs(url, prefix="", target_dir="", test=False):
    """ Download all linked images from url provided """
    page_str = get_page_str(url)
    urls = get_linked_img_urls(page_str, prefix=get_url_dir(url))
    if test:
        return
    for url in urls:
        print("Downloading: ", url)
        download_file(url, prefix, target_dir, test)


###############################################################################
# Unit Tests
###############################################################################


class unitTests(unittest.TestCase):

    tmp_area = "/tmp/ut" + getpass.getuser()
    test_area = tmp_area + "/t" + str(random.randrange(10000))
    tmp_file = test_area + "/f" + str(random.randrange(10000))

    def write_file(self, filename, file_str, append=0):
        """ Write string into a file (will overwrite existing file) """
        fh = open(filename, "a+" if append else "w", newline="\n")
        fh.write(file_str + "\n")
        fh.close()

    def setUp(self):
        os.makedirs(self.test_area, exist_ok=True)

    def test_webhelp_functions(self):
        """ Helping functions testing """

        # Get page string
        self.write_file(self.tmp_file, "<html>")
        self.assertEqual(get_page_str(self.tmp_file), "b'<html>\\n'")

        # Get url dir
        self.assertEqual(get_url_dir("fdfd/fdf.ht"), "fdfd/")

        # File download
        dwnl_file = self.test_area + "/prefix_logo11w.png"
        download_file(
            "http://www.google.com/images/srpr/logo11w.png",
            "prefix_", self.test_area)
        self.assertTrue(os.path.exists(dwnl_file))
        os.remove(dwnl_file)

        # Get linked img urls
        page_str = (
            "<><a fd href=http:/d.jpg cvc><img fdg>" +
            "df<A href=\"f.jpeg\" ><img f>")
        self.assertEqual(
            get_linked_img_urls(page_str), ["http:/d.jpg", "f.jpeg"])
        self.assertEqual(
            get_linked_img_urls(page_str, prefix="a/"),
            ["http:/d.jpg", "a/f.jpeg"])

        self.write_file(self.tmp_file, page_str)
        download_linked_imgs(self.tmp_file, test=True)

    def test_Webhelp_class__basic_functionality(self):
        """ Webhelp class basic testing """
        d = Webhelp()

    def test_xcleanup(self):
        shutil.rmtree(self.tmp_area)

if __name__ == "__main__":
    if sys.argv[-1] == "-ut":
        unittest.main(argv=[" "])

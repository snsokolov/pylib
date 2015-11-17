#!/usr/bin/env python3
# tableprinter.py - Table printer Module by Sergey 2014
# Pylib - Python useful modules (github.com/snsokolov/pylib)

"""
Table Printer Class implementation Module

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


###############################################################################
# Tableprinter Class
###############################################################################


class TablePrinter:
    """ Table Printer class """

    def __init__(self, columns=[]):
        """ Default constructor """
        self.columns = []
        self.widths = []
        self.printed_header = 0

        for column in columns:
            self.add_column(column)

    def add_column(self, name, width=0):
        """ Adding a column to the printer """
        self.columns.append(name)
        if width == 0:
            width = len(name)
        self.widths.append(width)

    def sprint_line(self, width):
        result = ""
        for i in range(width):
            result += "-"
        result += " "
        return result

    def sprint_column(self, value, width):
        result = str(value)
        result = result[:width]
        while len(result) <= width:
            result += " "
        return result

    def sprint(self, values):
        """ Printing a row to a string """
        result = ""
        if not self.printed_header:
            for (i, width) in enumerate(self.widths):
                result += self.sprint_column(self.columns[i], width)
            result = re.sub("\s+$", "", result)
            result += "\n"
            for (i, width) in enumerate(self.widths):
                result += self.sprint_line(width)
            result = re.sub("\s+$", "", result)
            result += "\n"
            self.printed_header = 1

        for (i, width) in enumerate(self.widths):
            result += self.sprint_column(values[i], width)
        result = re.sub("\s+$", "", result)
        result += "\n"

        return result

    def resize_column(self, column, width):
        """ Resize a column to a given value """
        found_column = 0
        for (i, column_name) in enumerate(self.columns):
            if column_name == column:
                found_column = 1
                if width > self.widths[i]:
                    self.widths[i] = width
                break
        assert(found_column), "Can't find a column: " + column

###############################################################################
# Unit Tests
###############################################################################


class unitTests(unittest.TestCase):

    def test_TablePrinter_class__basic_functionality(self):
        """ Table Printer class basic testing """
        p = TablePrinter()
        p.add_column("Name", 3)
        p.add_column("Value")
        self.assertEqual(p.columns, ["Name", "Value"])
        self.assertEqual(p.widths, [3, 5])
        self.assertEqual(p.sprint_line(3), "--- ")
        self.assertEqual(p.sprint_column("Name", 3), "Nam ")
        self.assertEqual(p.sprint_column(52, 4), "52   ")
        self.assertEqual(
            p.sprint(["ar", 10]), "Nam Value\n--- -----\nar  10\n")
        self.assertEqual(p.sprint(["ar", 10]), "ar  10\n")
        p.resize_column("Name", 6)
        self.assertEqual(p.widths, [6, 5])


if __name__ == "__main__":
    if sys.argv[-1] == "-ut":
        unittest.main(argv=[" "])

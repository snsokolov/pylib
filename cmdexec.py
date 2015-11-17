#!/usr/bin/env python3
# cmdexec.py - Commands Execution Module by Sergey 2014
# Pylib - Python useful modules (github.com/snsokolov/pylib)

"""
Module to execute shell commands with the confirmation

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
# Executable code
###############################################################################


def runcmd(cmd):
    """ Runs cmdline and returns the output """
    prc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    return prc.communicate()[0].decode().rstrip()


def runcmd_comment(cmd, comment):
    """ Runs cmdline and returns the output, also prints the commentary """
    print("\n%s - '%s'" % (comment, cmd))
    return runcmd(cmd)


def confirm_run(cmd, comment, test=False):
    """ Ask for the confirmation (unless 'test' argument is set) and executes
    the command. Also prints the commentary and result to STDOUT """
    if not test:
        print("\n%s - '%s'" % (comment, cmd))
        if input(self.CONFIRMATION) not in ("Y", "y"):
            print("Skipped")
            return

    cmdout = runcmd(cmd)
    if not test:
        print(cmdout)
        print("OK")

    return cmdout


###############################################################################
# Unit Tests
###############################################################################


class unitTests(unittest.TestCase):

    def test_cmdexec__basic_module_functions(self):
        """ Module basic functions """
        self.assertEqual(runcmd("echo 1 | grep 0"), "")
        self.assertEqual(runcmd("echo 1 | grep 1"), "1")
        self.assertEqual(confirm_run("echo 0", "", True), "0")


if __name__ == '__main__':
    if sys.argv[-1] == "-ut":
        unittest.main(argv=[" "])

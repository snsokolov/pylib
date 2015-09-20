#!/usr/bin/env python
# cmdexec.py - Commands Execution Module
#
# Copyright (C) 2014 Sergey Sokolov, License MIT

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
# Cmdexec Class
###############################################################################


class Cmdexec:
    """ CMD execution class wrapper. Wraps standard subprocess module to
    provide a convinient way to execute shell commands"""

    CONFIRMATION = "Proceed Y/N?: "

    def __init__(self, cmd, comment):
        """ Default class constructor """
        self.cmd = cmd
        self.comment = comment
        self.comment_line = "\n%s - '%s'" % (self.comment, self.cmd)

    def runcmd(self):
        """ Runs cmdline and returns the output """
        prc = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE)
        return prc.communicate()[0].decode().rstrip()

    def print_comment(self):
        """ Prints the commentary """
        print(self.comment_line)

    def confirm_run(self, test=False):
        """ Ask for the confirmation (unless 'test' argument is set) and executes
        the command. Also prints the commentary and result to STDOUT """
        if not test:
            self.print_comment()
            if input(self.CONFIRMATION) not in ("Y", "y"):
                print("Skipped")
                return

        cmdout = self.runcmd()
        if not test:
            print(cmdout)
            print("OK")

        return cmdout


###############################################################################
# Executable code
###############################################################################


def runcmd(cmd, comment):
    """ Runs cmdline and returns the output """
    return Cmdexec(cmd, comment).runcmd()


def runcmd_comment(cmd, comment):
    """ Runs cmdline and returns the output, also prints the commentary """
    ce = Cmdexec(cmd, comment)
    ce.print_comment()
    return ce.runcmd()


def confirm_run(cmd, comment, test=False):
    """ Ask for the confirmation (unless 'test' argument is set) and executes
    the command. Also prints the commentary and result to STDOUT """
    return Cmdexec(cmd, comment).confirm_run(test)


###############################################################################
# Unit Tests
###############################################################################


class unitTests(unittest.TestCase):

    def test_Cmdexec_class__basic_functionality(self):
        """ Cmdexec class basic testing """
        ce = Cmdexec("echo 0", "printing 0")
        self.assertEqual(ce.cmd, "echo 0")
        self.assertEqual(ce.runcmd(), "0")
        self.assertEqual(ce.confirm_run(True), "0")
        ce = Cmdexec("echo 1 | grep 0", "")
        self.assertEqual(ce.runcmd(), "")

    def test_cmdexec__basic_module_functions(self):
        """ Module basic functions """
        self.assertEqual(runcmd("echo 1 | grep 1", ""), "1")
        self.assertEqual(confirm_run("echo 0", "", True), "0")


if __name__ == '__main__':
    if sys.argv[-1] == "-ut":
        unittest.main(argv=[" "])

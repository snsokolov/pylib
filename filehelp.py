#!/usr/bin/env python3
# filehelp.py - File operations helping Module by Sergey 2014
# Pylib - Python useful modules (github.com/snsokolov/pylib)

"""
File helping functions Module

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
import datetime
import time


###############################################################################
# Executable code
###############################################################################


def write_file(filename, file_str, append=0):
    """ Write string into a file (will overwrite existing file) """
    fh = open(filename, "a+" if append else "w", newline="\n")
    fh.write(file_str + "\n")
    fh.close()


def append_file(filename, file_str):
    """ Append string to a file """
    write_file(filename, file_str, append=1)


def write_cmdfile(filename, cmd, append=0):
    """ Write command to a file """
    write_file(filename, cmd, append)
    os.chmod(filename, 0x1f8)


def read_file(filename):
    """ Read a string from a file """
    fh = open(filename, "r")
    file_str = fh.read()
    file_str = re.sub("$\n", "", file_str)
    fh.close()
    return file_str


def search_file(pattern, filename):
    """ Search file and return only the first match """
    if not os.path.exists(filename):
        raise Exception("Can't open file for reading! " + filename)

    fh = open(filename, "r")
    for line in fh:
        allmatch = re.findall(pattern, line)
        if allmatch:
            fh.close()
            return allmatch[0]

    fh.close()
    return None


def search_file_all(pattern, filename):
    """ Search file and return all matches """
    if not os.path.exists(filename):
        raise Exception("Can't open file for reading! " + filename)

    matches = []
    fh = open(filename, "r")
    for line in fh:
        allmatch = re.findall(pattern, line)
        if allmatch:
            matches += allmatch

    fh.close()
    return matches


def replace_file(pattern, substr, filename):
    """ Replaces pattern with a sub-string in the file """
    file_handle = open(filename, "r")
    file_string = file_handle.read()
    file_handle.close()

    file_string = re.sub(pattern, substr, file_string)

    file_handle = open(filename, "w", newline="\n")
    file_handle.write(file_string)
    file_handle.close()


def expand_path(path):
    """ Expand path with ~ and env """
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    path = os.path.abspath(path)
    return path


def expand_paths(paths):
    return [expand_path(path) for path in paths]


def dir_list(path):
    result = []
    if os.path.exists(path):
        for dirname in os.listdir(path):
            dirpath = os.path.join(path, dirname)
            if os.path.isdir(dirpath):
                result.append(dirpath)
    return result


def file_list(path):
    result = []
    if os.path.exists(path):
        for filename in os.listdir(path):
            filepath = path + "/" + filename
            if not os.path.isdir(filepath):
                result.append(filepath)
    return result


def file_head(f, n):
    """ Returns head of the file as a string """
    prc = subprocess.Popen(
        "head -n " + str(n) + " " + os.path.normpath(f),
        shell=True, stdout=subprocess.PIPE)
    return prc.communicate()[0].decode().rstrip()


def file_tail(f, n):
    """ Returns tail of the file as a string """
    prc = subprocess.Popen(
        "tail -n " + str(n) + " " + os.path.normpath(f),
        shell=True, stdout=subprocess.PIPE)
    return prc.communicate()[0].decode().rstrip()


def filename_strip_ext(filename):
    """ Return file name w/o extension and dirs """
    base = os.path.basename(filename)
    # Strip file extension
    return os.path.splitext(base)[0]


def filename_ext(filename):
    """ Return file name extension """
    base = os.path.basename(filename)
    return os.path.splitext(base)[1][1:]


def file_get_mdatetime(filename):
    """ Calulating the modification datetime of the file """
    return datetime.datetime.utcfromtimestamp(os.path.getmtime(filename))


def file_is_modified(filename, lastupdate):
    """ Return true if file was modified since the last update time """
    now = datetime.datetime.utcnow()
    update = file_get_mdatetime(filename)
    return now >= update and update >= lastupdate


def files_are_modified(filenames, lastupdate):
    """ Return true if one of files was modified """
    for filename in filenames:
        if file_is_modified(filename, lastupdate):
            return True
    return False


def get_datetime_str():
    """ Date Time string for a log file """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def append_logfile(filename, file_str):
    """ Write/Append string into a logfile """
    file_str = "[" + get_datetime_str() + "]" + file_str
    write_file(filename, file_str, append=1)


def dirstat(dir, size_unit="M", skip_dirs=[]):
    """ Calculates directory stats: size, files, directories """
    unit_pow = {"B": 0, "K": 1, "M": 2, "G": 3}
    size = 0
    filenum = 0
    dirnum = 0
    for path, dirs, files in os.walk(dir):
        skip = 0
        for skip_dir in skip_dirs:
            if re.search(skip_dir, path):
                skip = 1
        if skip:
            continue
        for d in dirs:
            dirnum += 1
        for f in files:
            filenum += 1
            size += os.path.getsize(os.path.join(path, f))
    # Converting size into MB
    size_div_pow = 0
    size_div_pow = unit_pow[size_unit]
    size = int(size/1024**size_div_pow)
    return size, filenum, dirnum


def find_files(dir, patterns=[]):
    result = []
    for path, dirs, files in os.walk(dir):
        for file in files:
            skip = 1 if patterns else 0
            for pattern in patterns:
                if re.search(pattern, file):
                    skip = 0
            if not skip:
                result.append(path + "/" + file)
    return result


def gitroot(dir=""):
    """ Get the Git root directory of any path inside the repo """
    # Supress errors from Git
    git_cmd = "git rev-parse --show-toplevel " + dir + " 2> " + os.devnull
    if dir:
        original_cwd = os.getcwd()
        os.chdir(dir)
    try:
        sub_out = subprocess.check_output(git_cmd, shell=True)
        cmd_out = sub_out.decode().rstrip(). splitlines()[0]
    except:
        cmd_out = ""
    if dir:
        os.chdir(original_cwd)
    return cmd_out


def main():

    # Empty
    pass

###############################################################################
# Unit Tests
###############################################################################


class unitTests(unittest.TestCase):

    tmp_area = "/tmp/ut" + getpass.getuser()
    test_area = tmp_area + "/t" + str(random.randrange(10000))
    tmp_file = test_area + "/f" + str(random.randrange(10000))

    def setUp(self):
        os.makedirs(self.test_area, exist_ok=True)

    def test_filehelp_functions(self):
        """ Helping functions testing """

        # Read and write file
        write_file(self.tmp_file, "bar")
        self.assertEqual(read_file(self.tmp_file), "bar")
        append_file(self.tmp_file, "bar")
        self.assertEqual(read_file(self.tmp_file), "bar\nbar")
        write_cmdfile(self.tmp_file, "cmd")
        self.assertEqual(read_file(self.tmp_file), "cmd")

        # Search file
        append_file(self.tmp_file, "cmd")
        self.assertEqual(search_file("dd", self.tmp_file), None)
        self.assertEqual(search_file("cm", self.tmp_file), "cm")
        self.assertEqual(search_file_all("cm", self.tmp_file), ["cm", "cm"])

        # Replace file
        replace_file("cmd", "bar", self.tmp_file)

        # Expand path
        self.assertEqual(expand_path("/tmp/p/.."), expand_path("/tmp"))
        self.assertEqual(expand_paths(["/tmp/p/.."]), [expand_path("/tmp")])

        # Dir list
        dir_test = os.path.join(self.test_area, "dir_test")
        os.makedirs(dir_test, exist_ok=True)
        self.assertEqual(dir_list(self.test_area), [dir_test])

        # File list
        self.assertEqual(file_list(self.test_area), [self.tmp_file])

        # File head
        self.assertEqual(file_head(self.tmp_file, 1), "bar")

        # File tail
        append_file(self.tmp_file, "foo")
        self.assertEqual(file_tail(self.tmp_file, 2), "bar\nfoo")

        # Strip ext
        self.assertEqual(filename_strip_ext("/tmp/a.b"), "a")

        # Ext
        self.assertEqual(filename_ext("/tmp/a.b"), "b")

        # Modification date
        os.system("touch " + os.path.normpath(self.tmp_file))
        now = datetime.datetime.utcnow()
        now_minus_1s = now - datetime.timedelta(seconds=1)
        self.assertGreater(
            file_get_mdatetime(self.tmp_file), now_minus_1s)

        # Log file
        self.assertEqual(get_datetime_str()[0], "2")
        append_logfile(self.tmp_file, "cmd")
        self.assertEqual(search_file("\[2", self.tmp_file), "[2")

        # Dir stat
        self.assertEqual(
            dirstat(self.test_area, size_unit="B"),
            (os.path.getsize(self.tmp_file), 1, 1))
        self.assertEqual(
            dirstat(self.test_area), (0, 1, 1))
        self.assertEqual(
            dirstat(self.test_area, skip_dirs=[self.test_area]),
            (0, 0, 0))

        # Find files
        files_area = self.test_area + "/files"
        subdir = files_area + "/sub"
        file1 = files_area + "/1.ry"
        file2 = subdir + "/2.py"
        os.makedirs(subdir, exist_ok=True)
        write_file(file1, "")
        write_file(file2, "")
        self.assertEqual(
            expand_paths(find_files(files_area)), expand_paths([file1, file2]))
        self.assertEqual(
            expand_paths(find_files(files_area, patterns=["\.py", "\.p"])),
            expand_paths([file2]))

        # Getting GIT Root directory
        original_cwd = os.getcwd()
        repodir = self.test_area + "/repo"
        repotest = repodir + "/test"
        os.makedirs(repotest, exist_ok=True)
        os.chdir(repodir)
        # Test that there is no repo
        self.assertEqual(gitroot(), "")
        # Create empty repo
        os.system("git init -q")
        os.chdir(original_cwd)
        # Test from test directory inside the repo
        self.assertEqual(
            expand_path(gitroot(repotest)), expand_path(repodir))

    def test_xcleanup(self):
        pass
        # shutil.rmtree(self.tmp_area)


if __name__ == "__main__":
    if sys.argv[-1] == "-ut":
        unittest.main(argv=[" "])
    main()

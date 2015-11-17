#!/usr/bin/env python3
# fastlist.py - Fast list implementation Module by Sergey 2015
# Pylib - Python useful modules (github.com/snsokolov/pylib)

"""
Fast list class implementation Module

"""

# Standard modules
import unittest
import sys
import re
import random

# Additional modules
import bisect
import array

###############################################################################
# Fastlist Class
###############################################################################


class Arrl(array.array):
    """ Array of signed long int (+-2**31 or 2*10**9 """
    def __new__(self, l=[]):
        return super().__new__(self, "l", l)


class Arrq(array.array):
    """ Array of signed long long int (+-2**63 or 9*10**18) """
    def __new__(self, l=[]):
        return super().__new__(self, "q", l)


class Fastlist(object):
    """ Fastlist representation """

    def __init__(self, l=[], load=5000, sorted=0, base=list):
        self._load = load
        self._sorted = sorted
        self._base = base
        self._lists = []
        self._starts = []
        self._mins = self._base()
        self._insert_list(0)
        self._irev = 0
        self._ii = 0
        self._il = 0
        self.extend(l)

    def _index_location(self, index):
        if len(self._lists[0]) == 0:
            raise IndexError("List index out of range")
        if index == 0:
            return (0, 0)
        if index == -1:
            return (len(self._lists) - 1, len(self._lists[-1]) - 1)
        if self._sorted:
            raise RuntimeError("No index access to the sorted list, exc 0, -1")
        length = len(self)
        if index < 0:
            index = length + index
        if index >= length:
            raise IndexError("List index out of range")
        il = bisect.bisect_right(self._starts, index) - 1
        return (il, index - self._starts[il])

    def _insert_list(self, il):
        self._lists.insert(il, self._base())
        if self._sorted:
            if len(self._mins) != 0:
                self._mins.insert(il, self._lists[il-1][-1])
        else:
            if il == 0:
                self._starts.insert(il, 0)
            else:
                start = self._starts[il-1] + len(self._lists[il-1])
                self._starts.insert(il, start)

    def _del_list(self, il):
        del self._lists[il]
        if self._sorted:
            del self._mins[il]
        else:
            del self._starts[il]

    def _rebalance(self, il):
        illen = len(self._lists[il])
        if illen >= self._load * 2:
            self._insert_list(il)
            self._even_lists(il)
        if illen <= self._load * 0.2:
            if il != 0:
                self._even_lists(il-1)
            elif len(self._lists) > 1:
                self._even_lists(il)

    def _even_lists(self, il):
        tot = len(self._lists[il]) + len(self._lists[il+1])
        if tot < self._load * 1:
            self._lists[il] += self._lists[il+1]
            self._del_list(il+1)
            if self._sorted:
                self._mins[il] = self._lists[il][0]
        else:
            half = tot//2
            ltot = self._lists[il] + self._lists[il+1]
            self._lists[il] = ltot[:half]
            self._lists[il+1] = ltot[half:]
            if self._sorted:
                self._mins[il] = self._lists[il][0]
                self._mins[il+1] = self._lists[il+1][0]
            else:
                self._starts[il+1] = self._starts[il] + len(self._lists[il])

    def _obj_location(self, obj, l=0):
        if not self._sorted:
            raise RuntimeError("No by-value access to an unsorted list")
        il = 0
        if len(self._mins) > 1 and obj > self._mins[0]:
            if l:
                il = bisect.bisect_left(self._mins, obj) - 1
            else:
                il = bisect.bisect_right(self._mins, obj) - 1
        if l:
            ii = bisect.bisect_left(self._lists[il], obj)
        else:
            ii = bisect.bisect_right(self._lists[il], obj)
        return (il, ii)

    def insert(self, index, obj):
        (il, ii) = self._index_location(index)
        self._lists[il].insert(ii, obj)
        for j in range(il + 1, len(self._starts)):
            self._starts[j] += 1
        self._rebalance(il)

    def append(self, obj):
        if len(self._mins) == 0:
            self._mins.append(obj)
        if len(self._lists[-1]) >= self._load:
            self._insert_list(len(self._lists))
        self._lists[-1].append(obj)

    def extend(self, iter):
        for n in iter:
            self.append(n)

    def pop(self, index=None):
        if index is None:
            index = -1
        (il, ii) = self._index_location(index)
        item = self._lists[il].pop(ii)
        if self._sorted:
            if ii == 0 and len(self._lists[il]) > 0:
                self._mins[il] = self._lists[il][0]
        else:
            for j in range(il + 1, len(self._starts)):
                self._starts[j] -= 1
        self._rebalance(il)
        return item

    def clear(self):
        self._lists = []
        self._starts = Arrl()
        self._mins = self._base()
        self._insert_list(0)

    def as_list(self):
        return list(sum(self._lists, self._base()))

    def insort(self, obj, l=0):
        if len(self._mins) == 0:
            self._mins.append(obj)
        (il, ii) = self._obj_location(obj, l)
        self._lists[il].insert(ii, obj)
        if ii == 0:
            self._mins[il] = obj
        self._rebalance(il)

    def insort_left(self, obj):
        self.insort(obj, l=1)

    def add(self, obj):
        if self._sorted:
            self.insort(obj)
        else:
            self.append(obj)

    def __str__(self):
        return str(self.as_list())

    def __setitem__(self, index, obj):
        if isinstance(index, int):
            (il, ii) = self._index_location(index)
            self._lists[il][ii] = obj
        elif isinstance(index, slice):
            raise RuntimeError("Slice assignment is not supported")

    def __getitem__(self, index):
        if isinstance(index, int):
            (il, ii) = self._index_location(index)
            return self._lists[il][ii]
        elif isinstance(index, slice):
            rg = index.indices(len(self))
            if rg[0] == 0 and rg[1] == len(self) and rg[2] == 1:
                return self.as_list()
            return [self.__getitem__(index) for index in range(*rg)]

    def __iadd__(self, obj):
        if self._sorted:
            [self.insort(n) for n in obj]
        else:
            [self.append(n) for n in obj]
        return self

    def __delitem__(self, index):
        if isinstance(index, int):
            self.pop(index)
        elif isinstance(index, slice):
            rg = index.indices(len(self))
            [self.__delitem__(rg[0]) for i in range(*rg)]

    def __len__(self):
        if self._sorted:
            return sum([len(l) for l in self._lists])
        return self._starts[-1] + len(self._lists[-1])

    def __contains__(self, obj):
        if self._sorted:
            it = self.lower_bound(obj)
            return not it.iter_end() and obj == it.iter_getitem()
        else:
            for n in self:
                if obj == n:
                    return True
            return False

    def __bool__(self):
        return len(self._lists[0]) != 0

    def __iter__(self):
        if not self._irev:
            self._il = self._ii = 0
        else:
            self._il = len(self._lists) - 1
            self._ii = len(self._lists[self._il]) - 1
        return self

    def __reversed__(self):
        self._irev = 1
        self.__iter__()
        return self

    def _iter_fix(self):
        if not self._irev:
            if (self._il != len(self._lists) - 1 and
                    self._ii == len(self._lists[self._il])):
                self._il += 1
                self._ii = 0
        else:
            if self._il != 0 and self._ii == -1:
                self._il -= 1
                self._ii = len(self._lists[self._il]) - 1

    def __next__(self):
        item = self.iter_getitem()
        if not self._irev:
            self._ii += 1
        else:
            self._ii -= 1
        return item

    def iter_end(self):
        if not self._irev:
            return (self._il == len(self._lists) - 1 and
                    self._ii == len(self._lists[self._il]))
        else:
            return (self._il == 0 and self._ii == -1)

    def iter_getitem(self):
        if self.iter_end() or len(self._lists[0]) == 0:
            raise StopIteration("Iteration stopped")
        self._iter_fix()
        return self._lists[self._il][self._ii]

    def iter_del(self):
        item = self._lists[self._il].pop(self._ii)
        if self._sorted:
            if self._ii == 0 and len(self._lists[self._il]) > 0:
                self._mins[self._il] = self._lists[self._il][0]
        else:
            for j in range(self._il + 1, len(self._starts)):
                self._starts[j] -= 1
        self._rebalance(self._il)
        return item

    def lower_bound(self, obj):
        (self._il, self._ii) = self._obj_location(obj, l=1)
        return self

    def upper_bound(self, obj):
        (self._il, self._ii) = self._obj_location(obj)
        return self

###############################################################################
# Unit Tests
###############################################################################


class unitTests(unittest.TestCase):

    def test_Fastlist_class__performance_vs_sortedcontainers(self):
        # Performance (100k - 1.32 vs 0.9)
        # mmax = 100000
        mmax = 3000
        d = Fastlist([], load=5000, sorted=1, base=list)
        # d = sortedcontainers.SortedList()
        for i in range(mmax):
            d.add(i // 100 + i % 100)
            d.add((i // 100 + i % 100) * 2)
            d.pop(0)

    def test_Fastlist_class__basic_functionality(self):
        """ Fastlist class basic unsorted testing """

        # Basic internal structure - list of lists with same avg. size
        d = Fastlist([1, 2, 4, 3], load=4)
        self.assertEqual(list(map(list, d._lists)), [[1, 2, 4, 3]])
        self.assertEqual(list(d._starts), [0])

        # Appending more items, making sure that list is splitted once its
        # size is more than load
        d.append(6)
        self.assertEqual(list(map(list, d._lists)), [[1, 2, 4, 3], [6]])
        self.assertEqual(list(d._starts), [0, 4])

        # Appending more to make sure that list is splitted one more time
        for i in range(5):
            d.append(1)
        self.assertEqual(list(d._starts), [0, 4, 8])

        # Checking length
        self.assertEqual(len(d), 10)

        # Pop and see combined lists
        for i in range(10):
            d.pop()
        self.assertEqual(list(d), [])

    def test_Fastlist_class__insert(self):
        """ Insert. Insert new element at certain index and shift the rest """

        # Insert at 0
        d = Fastlist([0], load=2)
        d.insert(0, 1)
        self.assertEqual(d[0], 1)
        self.assertEqual(len(d), 2)

        # Insert at the end of the list
        d.insert(-1, -1)
        self.assertEqual(d[-2], -1)

        # Do not allow iserts greater than length (opposite to list)
        try:
            d.insert(10, 10)
            self.assertTrue(0)
        except IndexError:
            pass

        """ Sorted """
        # Insert at 0
        d = Fastlist([0], load=2, sorted=1)
        d.insert(0, 1)
        self.assertEqual(d[0], 1)
        self.assertEqual(len(d), 2)

        # Insert at the end of list
        d.insert(-1, -1)
        self.assertEqual(d.as_list()[-2], -1)

        # Do not allow iserts greater than length (opposite to list)
        try:
            d.insert(10, 10)
            self.assertTrue(0)
        except RuntimeError:
            pass

    def test_Fastlist_class__append(self):
        """ Append. Add element to the end of the list """

        d = Fastlist(load=2)
        [d.append(i) for i in range(100)]
        self.assertEqual(d[99], 99)

        """ Sorted """
        d = Fastlist(load=2, sorted=1)
        [d.append(i) for i in range(100)]
        self.assertEqual(d[-1], 99)

    def test_Fastlist_class__exted(self):
        """ Extend. Extend the list by appending all elements from iter """

        d = Fastlist([1, 2, 3], load=2)
        d.extend([i for i in range(100)])
        self.assertEqual(d[102], 99)

        """ Sorted """
        d = Fastlist([1, 2, 3], load=2, sorted=1)
        d.extend([i for i in range(100)])
        self.assertEqual(d[-1], 99)

    def test_Fastlist_class__pop(self):
        """ Pop. Return element and remove from the list """

        # Pop from various locations
        d = Fastlist([3, 4, 5, 6, 7], load=3)
        self.assertEqual(d.pop(), 7)
        self.assertEqual(d.pop(0), 3)
        self.assertEqual(d.pop(-1), 6)

        # Check for empty list exception
        try:
            Fastlist(load=2).pop()
            self.assertTrue(0)
        except IndexError:
            pass

        """ Sorted list """
        # Pop from various locations
        d = Fastlist([3, 4, 5, 6, 7], load=3, sorted=1)
        self.assertEqual(d.pop(), 7)
        self.assertEqual(d.pop(0), 3)
        self.assertEqual(d.pop(-1), 6)

        # Check for empty list exception
        try:
            Fastlist(load=2, sorted=1).pop()
            self.assertTrue(0)
        except IndexError:
            pass

        # Check for index exception
        try:
            Fastlist([1, 2, 3], load=2, sorted=1).pop(1)
            self.assertTrue(0)
        except RuntimeError:
            pass

    def test_Fastlist_class__clear(self):
        """ Clear. Clear all lists """
        d = Fastlist([10, 20, 30, 40], load=4)
        d.clear()
        self.assertEqual(list(map(list, d._lists)), [[]])
        self.assertEqual(len(d), 0)
        [d.append(i) for i in range(100)]
        self.assertEqual(d[-1], 99)

        """ Sorted list """
        d = Fastlist([10, 20, 30, 40], load=4, sorted=1)
        d.clear()
        self.assertEqual(list(map(list, d._lists)), [[]])
        self.assertEqual(len(d), 0)
        [d.append(i) for i in range(100)]
        self.assertEqual(d[-1], 99)

    def test_Fastlist_class__as_list(self):
        """ As list. Return list representation of object """
        l = [10, 20, 30, 40]
        d = Fastlist(load=2)
        d.extend(l)
        self.assertEqual(d.as_list(), l)

        """ Sorted list """
        l = [20, 10, 30, 40]
        d = Fastlist(load=2, sorted=1)
        d.extend(l)
        self.assertEqual(d.as_list(), l)

    def test_Fastlist_class__insort(self):
        """ Insort. Insert element in sorted order """

        # No insort for unsorted lists
        try:
            Fastlist([1, 2, 3], load=2).insort(1)
            self.assertTrue(0)
        except RuntimeError:
            pass

        """ Sorted list """
        l = [10, 30, 30, 30, 40]
        d = Fastlist(l, load=2, sorted=1)
        d.insort(5)
        self.assertEqual(d[0], 5)
        d.insort(50)
        self.assertEqual(d[-1], 50)
        d.insort_left(30)
        self.assertEqual(d.as_list()[2], 30)

    def test_Fastlist_class__bound(self):
        """ lower/upper bounds. Return iterator to lower or upper bound """

        # No bounds for unsorted lists
        try:
            Fastlist([1, 2, 3], load=2).lower_bound(1)
            self.assertTrue(0)
        except RuntimeError:
            pass

        """ Sorted list """
        l = [(1, 0), (3, 0), (3, 0), (3, 0), (4, 0)]
        d = Fastlist(l, load=2, sorted=1)
        d.lower_bound((3, 0))
        self.assertEqual((d._il, d._ii), (0, 1))
        d.upper_bound((3, 0))
        self.assertEqual((d._il, d._ii), (2, 0))
        d.upper_bound((0, 0))
        self.assertEqual((d._il, d._ii), (0, 0))
        d.lower_bound((5, 0))
        self.assertEqual((d._il, d._ii), (2, 1))

    def test_Fastlist_class__setitem(self):
        """ Setitem L[i] = k , L[i:j] is not supported  """

        # Assign value
        d = Fastlist([4, 2, 1, 5], load=2)
        d[2] = 5
        self.assertEqual(d.as_list(), [4, 2, 5, 5])

        # Check for empty list exception
        try:
            Fastlist(load=2)[0] = 1
            self.assertTrue(0)
        except IndexError:
            pass

        # Check for index greater than length exception
        try:
            Fastlist([1, 2], load=2)[2] = 1
            self.assertTrue(0)
        except IndexError:
            pass

        """ Sorted list """
        # Assign value
        d = Fastlist([4, 2, 1, 5], load=2, sorted=1)

        try:
            d[2] = 5
            self.assertTrue(0)
        except RuntimeError:
            pass

        # Check for empty list exception
        try:
            Fastlist(load=2, sorted=1)[0] = 1
            self.assertTrue(0)
        except IndexError:
            pass

        # Check for index greater than length exception
        try:
            Fastlist([1, 2], load=2, sorted=1)[2] = 1
            self.assertTrue(0)
        except RuntimeError:
            pass

    def test_Fastlist_class__getitem(self):
        """ Getitem a = L[i] or a = L[i:j] """

        d = Fastlist([4, 2, 1, 5], load=2)
        self.assertEqual(d[0], 4)
        self.assertEqual(d[-1], 5)
        self.assertEqual(d[3], 5)
        self.assertEqual(d[1:3], [2, 1])
        self.assertEqual(d[3:10], [5])
        self.assertEqual(d[:], d.as_list())

        # Check for index greater than length exception
        try:
            a = Fastlist([1, 2], load=2)[2]
            self.assertTrue(0)
        except IndexError:
            pass

        """ Sorted list """
        d = Fastlist([4, 2, 1, 5], load=2, sorted=1)
        self.assertEqual(d[0], 4)
        self.assertEqual(d[-1], 5)

        # Allowed to read whole sorted array
        self.assertEqual(d[:], d.as_list())

        # Not allowed any indexes other than 0 and -1
        try:
            self.assertEqual(d[1:3], 4)
            self.assertTrue(0)
        except RuntimeError:
            pass

    def test_Fastlist_class__iadd(self):
        """ Inplace Add list L += [] """

        d = Fastlist([4, 2, 1], load=3)
        b = Fastlist(d, load=4)
        b += [3, 1]
        self.assertEqual(b.as_list(), d.as_list() + [3, 1])

        """ Sorted list """
        # Insorting elements instead of appending
        d = Fastlist([1, 3, 5], load=3, sorted=1)
        b = Fastlist(d, load=4, sorted=1)
        b += [0, 4]
        self.assertEqual(b.as_list(), [0, 1, 3, 4, 5])

    def test_Fastlist_class__delitem(self):
        """ Delitem del L[i] or L[i:j] """

        d = Fastlist([1, 2, 3, 4, 5, 6], load=3)
        del(d[0])
        del(d[-1])
        self.assertEqual(d.as_list(), [2, 3, 4, 5])
        del(d[2:])
        self.assertEqual(d.as_list(), [2, 3])

        """ Sorted list """
        d = Fastlist([1, 2, 3, 4, 5, 6], load=3, sorted=1)
        del(d[0])
        del(d[-1])
        self.assertEqual(d.as_list(), [2, 3, 4, 5])
        try:
            del(d[2:])
            self.assertTrue(0)
        except RuntimeError:
            pass

    def test_Fastlist_class__len(self):
        """ Len len L """

        d = Fastlist()
        self.assertEqual(len(d), 0)
        d += [1]
        self.assertEqual(len(d), 1)

        """ Sorted list """
        d = Fastlist(sorted=1)
        self.assertEqual(len(d), 0)
        d += [1]
        self.assertEqual(len(d), 1)

    def test_Fastlist_class__contains(self):
        """ Contains a in L """

        d = Fastlist(load=1)
        self.assertFalse(1 in d)
        d += [1, 3, 4]
        self.assertTrue(1 in d)

        """ Sorted list """
        d = Fastlist(load=2, sorted=1)
        self.assertFalse(1 in d)
        d += [1, 3, 3, 3, 3, 3, 4]
        self.assertTrue(1 in d)
        self.assertTrue(4 in d)
        self.assertFalse(0 in d)
        self.assertFalse(5 in d)

    def test_Fastlist_class__bool(self):
        """ Bool if(L) """

        d = Fastlist()
        self.assertFalse(d)
        d += [1, 3, 4]
        self.assertTrue(d)

        """ Sorted list """
        d = Fastlist(sorted=1)
        self.assertFalse(d)
        d += [1, 3, 4]
        self.assertTrue(d)

    def test_Fastlist_class__stress(self):
        """ Insert, Append, Add, Pop unsorted stress test """
        stress = 500

        l = [random.randint(0, 100) for n in range(20)]
        d = Fastlist(l, load=5)
        for i in range(stress):
            sel = random.randint(0, 7)
            index = random.randint(-1, len(l)-1)
            data = random.randint(0, 100)
            if not l:
                sel = 0
            if sel == 0:
                l.insert(index, data)
                d.insert(index, data)
            elif sel == 1:
                l.append(data)
                d.append(data)
            elif sel == 2:
                l.extend([data, data+1])
                d.extend([data, data+1])
            elif sel == 3:
                l.pop(index)
                d.pop(index)
            elif sel == 4:
                l[index] = data
                d[index] = data
            elif sel == 5:
                self.assertEqual(d[index], l[index])
            elif sel == 6:
                l += [data, data*2]
                d += [data, data*2]
            elif sel == 7:
                del(l[index])
                del(d[index])
            self.assertEqual(len(d), len(l))
            self.assertEqual(data in d, data in l)
        self.assertEqual(list(d), l)

        l = [random.randint(0, 100) for n in range(20)]
        d = Fastlist(l, load=5, sorted=1)
        for i in range(stress):
            sel = random.randint(0, 7)
            index = random.randint(-1, 0)
            data = random.randint(0, 100)
            if not l:
                sel = 0
            if sel == 0:
                l.insert(index, data)
                d.insert(index, data)
            elif sel == 1:
                l.append(data)
                d.append(data)
            elif sel == 2:
                l.extend([data, data+1])
                d.extend([data, data+1])
            elif sel == 3:
                l.pop(index)
                d.pop(index)
            elif sel == 4:
                l[index] = data
                d[index] = data
            elif sel == 5:
                self.assertEqual(d[index], l[index])
            elif sel == 6:
                del(l[index])
                del(d[index])
            self.assertEqual(len(d), len(l))
        self.assertEqual(list(d), l)

        l = sorted([random.randint(0, 100) for n in range(15)])
        d = Fastlist(l, load=5, sorted=1)
        for i in range(stress):
            l.sort()
            sel = random.randint(0, 3)
            index = random.randint(-1, 0)
            data = random.randint(0, 100)
            if not l:
                sel = 0
            if sel == 0:
                l.insert(index, data)
                d.insort(data)
            elif sel == 1:
                l.pop(index)
                d.pop(index)
            elif sel == 2:
                self.assertEqual(d[index], l[index])
            elif sel == 3:
                del(l[index])
                del(d[index])
            self.assertEqual(len(d), len(l))
            self.assertEqual(data in d, data in l)
        self.assertEqual(list(d), sorted(l))

    def test_Fastlist_class__iterators(self):
        """ Iterator functions """

        # Iterator
        d = Fastlist([i for i in range(30)], load=3)
        it = iter(d)
        self.assertEqual(next(it), 0)
        self.assertEqual(next(it), 1)
        self.assertEqual([n for n in d], d.as_list())

        # Reverse iterator
        d = Fastlist([i for i in range(30)], load=3)
        it = reversed(d)
        self.assertEqual(next(it), 29)
        self.assertEqual(next(it), 28)
        self.assertEqual([n for n in reversed(d)], list(reversed(d.as_list())))

        # Iter end and iter getitem
        d = Fastlist([i for i in range(30)], load=3)
        it = iter(d)
        self.assertFalse(it.iter_end())
        self.assertEqual(it.iter_getitem(), 0)
        [next(it) for i in range(30)]
        self.assertTrue(it.iter_end())
        try:
            self.assertEqual(it.iter_getitem(), 0)
            self.assertTrue(0)
        except StopIteration:
            pass

        # Iter delete
        d = Fastlist([1, 2, 3], load=2)
        it = iter(d)
        next(it)
        it.iter_del()
        self.assertEqual(d.as_list(), [1, 3])

        """ Sorted list """

        # Iter delete
        d = Fastlist([1, 2, 3], load=2, sorted=1)
        it = iter(d)
        next(it)
        it.iter_del()
        self.assertEqual(d.as_list(), [1, 3])

        # Lower bound
        d = Fastlist([1, 2, 2, 2, 2, 3], load=2, sorted=1)
        d.lower_bound(2)
        self.assertEqual(d.iter_getitem(), 2)
        next(d)
        self.assertEqual(d.iter_getitem(), 2)

        # Upper bound
        d = Fastlist([1, 2, 2, 2, 2, 3], load=2, sorted=1)
        d.upper_bound(2)
        self.assertEqual(d.iter_getitem(), 3)
        self.assertEqual(next(d), 3)
        try:
            next(d)
            self.assertTrue(0)
        except StopIteration:
            pass

    def test_Fastlist_class__array(self):
        """ Using array as a base class """

        d = Fastlist(load=2, sorted=1, base=Arrl)
        [d.append(i) for i in range(100)]
        self.assertEqual(d[-1], 99)

        """ Sorted list """
        l = [10, 30, 30, 30, 40]
        d = Fastlist(l, load=2, sorted=1, base=Arrq)
        d.insort(5)
        self.assertEqual(d[0], 5)
        d.insort(50)
        self.assertEqual(d[-1], 50)
        d.insort_left(30)
        self.assertEqual(d.as_list()[2], 30)


if __name__ == "__main__":
    if sys.argv[-1] == "-ut":
        unittest.main(argv=[" "])

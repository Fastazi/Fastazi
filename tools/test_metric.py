import pytest
from metric import apfd

# tests: a, b, c, d, e, ....
# faults: 1, 2, 3, 4, 5, ...
# fault_matrix = {'a': [1, 5],
#                 'b': [6, 7],
#                 'c': [1, 2, 3, 4, 5, 6, 7],
#                 'd': [5],
#                 'e': [8, 9, 10]}

fault_matrix = set()
fault_matrix.add('c')

def test1():
    prioritization = ['a', 'b', 'c', 'd', 'e']
    actual = apfd(prioritization, fault_matrix)
    expected = 0.5
    assert(actual == expected), "actual: {} | expected: {}".format(actual, expected)

def test2():
    prioritization = ['e', 'c', 'd', 'b', 'a']
    actual = apfd(prioritization, fault_matrix)
    expected = 0.7
    assert(actual == expected), "actual: {} | expected: {}".format(actual, expected)
    
def test3():
    prioritization = ['c', 'e', 'b', 'a', 'd']
    actual = apfd(prioritization, fault_matrix)
    expected = 0.9
    assert(actual == expected), "actual: {} | expected: {}".format(actual, expected)

def test4():
    prioritization = ['b', 'a', 'd', 'c', 'e']
    actual = apfd(prioritization, fault_matrix)
    expected = 0.5
    assert(actual == expected), "actual: {} | expected: {}".format(actual, expected)

def test4():
    prioritization = ['b', 'a', 'e', 'd', 'c']
    actual = apfd(prioritization, fault_matrix)
    expected = 0.1
    assert(actual == expected), "actual: {} | expected: {}".format(actual, expected)


#!/usr/bin/env python
#Licence LGPL v2.1

# Tests for coordinate conversion functions

def getIntegerAsBlock(i):
    x = unsignedToSigned(i % 4096, 2048)
    i = int((i - x) / 4096)
    y = unsignedToSigned(i % 4096, 2048)
    i = int((i - y) / 4096)
    z = unsignedToSigned(i % 4096, 2048)
    return x,y,z


def unsignedToSigned(i, max_positive):
    if i < max_positive:
        return i
    else:
        return i - 2*max_positive


def int64(u):
	while u >= 2**63:
		u -= 2**64
	while u <= -2**63:
		u += 2**64
	return u

# Convert location to integer
def getBlockAsInteger(p):
	return int64(p[2]*16777216 + p[1]*4096 + p[0])


sample_p = (1, -1, 1)
result_i = getBlockAsInteger(list(sample_p))
result_p = getIntegerAsBlock(result_i)
print(sample_p, result_i, result_p)
assert result_p == sample_p, "Test 1 failed"

sample_p = (1, 1, 1)
result_i = getBlockAsInteger(list(sample_p))
result_p = getIntegerAsBlock(result_i)
print(sample_p, result_i, result_p)
assert result_p == sample_p, "Test 2 failed"

sample_p = (-1, -1, -1)
result_i = getBlockAsInteger(list(sample_p))
result_p = getIntegerAsBlock(result_i)
print(sample_p, result_i, result_p)
assert result_p == sample_p, "Test 3 failed"

sample_p = (-1, 0, 0)
result_i = getBlockAsInteger(list(sample_p))
result_p = getIntegerAsBlock(result_i)
print(sample_p, result_i, result_p)
assert result_p == sample_p, "Test 4 failed"

sample_p = (-1, 1, 1)
result_i = getBlockAsInteger(list(sample_p))
result_p = getIntegerAsBlock(result_i)
print(sample_p, result_i, result_p)
assert result_p == sample_p, "Test 5 failed"

sample_p = (0, -1, -1)
result_i = getBlockAsInteger(list(sample_p))
result_p = getIntegerAsBlock(result_i)
print(sample_p, result_i, result_p)
assert result_p == sample_p, "Test 6 failed"

sample_p = (0, 0, 0)
result_i = getBlockAsInteger(list(sample_p))
result_p = getIntegerAsBlock(result_i)
print(sample_p, result_i, result_p)
assert result_p == sample_p, "Test 7 failed"

sample_p = (-1, -1, 1)
result_i = getBlockAsInteger(list(sample_p))
result_p = getIntegerAsBlock(result_i)
print(sample_p, result_i, result_p)
assert result_p == sample_p, "Test 8 failed"

sample_p = (10, 10, 10)
result_i = getBlockAsInteger(list(sample_p))
result_p = getIntegerAsBlock(result_i)
print(sample_p, result_i, result_p)
assert result_p == sample_p, "Test 9 failed"

sample_p = (-10, -10, -10)
result_i = getBlockAsInteger(list(sample_p))
result_p = getIntegerAsBlock(result_i)
print(sample_p, result_i, result_p)
assert result_p == sample_p, "Test 10 failed"

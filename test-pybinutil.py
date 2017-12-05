from __future__ import print_function

import pybinutil as pbu

print("## to_bit()")
n = [
    ("0x00", [0]),
    ("0x01", [1]),
    ("0x8000", [0x80, 0x00]),     # 0x8000
    ("0x8001", [0x80, 0x01]),     # 0x8001
    ("0xff", [0xff])            # 0xff
    ]
for k, v in n:
    print("%s => %s" % (k, pbu.to_bit(bytearray(v))))

print("## to_bit()")
n = [
    ("0x00", [0]),
    ("0x01", [1]),
    ("0x8000", [0x80, 0x00]),     # 0x8000
    ("0x8001", [0x80, 0x01]),     # 0x8001
    ("0xff", [0xff])            # 0xff
    ]
for k, v in n:
    print("%s => %s" % (k, pbu.to_bit(bytearray(v))))

print("## to_hex()")
n = [
    ("0x00", [0]),
    ("0x01", [1]),
    ("0x8000", [0x80, 0x00]),     # 0x8000
    ("0x8001", [0x80, 0x01]),     # 0x8001
    ("0xff", [0xff])            # 0xff
    ]
for k, v in n:
    print("%s => %s" % (k, pbu.to_hex(bytearray(v))))

print("## to_int()")
n = [
    ("0x00", [0]),
    ("0x01", [1]),
    ("0x8000", [0x80, 0x00]),     # 0x8000
    ("0x8001", [0x80, 0x01]),     # 0x8001
    ("0xff", [0xff])            # 0xff
    ]
for k, v in n:
    print("%s => %s" % (k, pbu.to_int(bytearray(v))))
print("- to_int(reverse=True)")
for k, v in n:
    print("%s => %s" % (k, pbu.to_int(bytearray(v), True)))

print("## int_to()")
n = [
    0,
    1,
    32768,     # 0x8000
    32769,     # 0x8001
    255        # 0xff
    ]
for i in n:
    print("%d => %s" % (i, pbu.to_bit(pbu.int_to(i))))

print("- fixed width")
w = [ 4, 1 ]
for j in w:
    for i in n:
        print("%d => %s" % (i, pbu.to_bit(pbu.int_to(i, j))))

print("## bit_get()")
n = [
    0,
    1,
    32768,     # 0x8000
    32769,     # 0x8001
    255        # 0xff
    ]
for i in n:
    ba = pbu.int_to(i)
    print("- %s" % pbu.to_bit(ba))
    for j in range(len(ba)*8):
        print("    %s" % pbu.bit_get(ba, j, 6))

print("## bit_set()")
# 0010 0011 1100 0010
ba0 = bytearray(2)
pbu.bit_set(ba0, 2)
pbu.bit_set(ba0, 6, "1111")
pbu.bit_set(ba0, 14)
print(pbu.to_bit(ba0))

print("- implicit")
for i in range(17):
    ba0 = bytearray(2)
    pbu.bit_set(ba0, i)
    print(" ", pbu.to_bit(ba0))

print("- 1")
for i in range(17):
    ba0 = bytearray(2)
    pbu.bit_set(ba0, i, "1")
    print(" ", pbu.to_bit(ba0))

print("- 10")
for i in range(17):
    ba0 = bytearray(2)
    pbu.bit_set(ba0, i, "10")
    print(" ", pbu.to_bit(ba0))

print("- 01")
for i in range(17):
    ba0 = bytearray(2)
    pbu.bit_set(ba0, i, "01")
    print(" ", pbu.to_bit(ba0))

print("- 110")
for i in range(17):
    ba0 = bytearray(2)
    pbu.bit_set(ba0, i, "110")
    print(" ", pbu.to_bit(ba0))

print("## int_to_bit()")
n = [ 0, 1,
     32768,     # 0x8000
     32769,     # 0x8001
     255        # 0xff
     ]
w = [ 32, 8 ]
for j in w:
    for i in n:
        print("%d %d => %s" % (i, j, pbu.int_to_bit(i, j)))

print("## bit_find()")
n = [ 0, 1,
     32768,     # 0x8000
     32769,     # 0x8001
     255        # 0xff
     ]
w = [ 16, 8 ]
for j in w:
    print("- bit len = %d" % j)
    for i in n:
        p, q = pbu.bit_find(i, j)
        fmt = "  %%0%dx => " % int(j/4)
        if p != None:
            fmt += "%%d %%0%dx" % int(j/4)
            print(fmt % (i, p, q))
        else:
            fmt += "None %%0%dx" % int(j/4)
            print(fmt % (i, q))

print("## bit_count()")
n = [ 0, 1,
     32768,     # 0x8000
     32769,     # 0x8001
     255        # 0xff
     ]
w = [ 32, 8 ]
for j in w:
    for i in n:
        fmt = "0x%%0%dx => %%d" % (int(j/4))
        print(fmt % (i, pbu.bit_count(i, j)))

print("## bit_count(zero=True)")
n = [ 0, 1,
     32768,     # 0x8000
     32769,     # 0x8001
     255        # 0xff
     ]
w = [ 32, 8 ]
for j in w:
    for i in n:
        fmt = "0x%%0%dx => %%d" % (int(j/4))
        print(fmt % (i, pbu.bit_count(i, j, zero=True)))



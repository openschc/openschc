from __future__ import print_function

try:
    from pybinutil import byteutil as by
    from pybinutil import bitutil as bi
    print("# pybinutil test")
except:
    import byteutil as by
    import bitutil as bi
    print("# module test")

#
# test for byteutil
#
print("## to_bit()")
n = [
    ("0x00", [0]),
    ("0x01", [1]),
    ("0x8000", [0x80, 0x00]),     # 0x8000
    ("0x8001", [0x80, 0x01]),     # 0x8001
    ("0xff", [0xff])            # 0xff
    ]
for k, v in n:
    print("%s => %s" % (k, by.to_bit(bytearray(v))))

print("## to_bit()")
n = [
    ("0x00", [0]),
    ("0x01", [1]),
    ("0x8000", [0x80, 0x00]),     # 0x8000
    ("0x8001", [0x80, 0x01]),     # 0x8001
    ("0xff", [0xff])            # 0xff
    ]
for k, v in n:
    print("%s => %s" % (k, by.to_bit(bytearray(v))))

print("## to_hex()")
n = [
    ("0x00", [0]),
    ("0x01", [1]),
    ("0x8000", [0x80, 0x00]),     # 0x8000
    ("0x8001", [0x80, 0x01]),     # 0x8001
    ("0xff", [0xff])            # 0xff
    ]
for k, v in n:
    print("%s => %s" % (k, by.to_hex(bytearray(v))))

print("## to_int()")
n = [
    ("0x00", [0]),
    ("0x01", [1]),
    ("0x8000", [0x80, 0x00]),     # 0x8000
    ("0x8001", [0x80, 0x01]),     # 0x8001
    ("0xff", [0xff])            # 0xff
    ]
for k, v in n:
    print("%s => %s" % (k, by.to_int(bytearray(v))))
print("- to_int(reverse=True)")
for k, v in n:
    print("%s => %s" % (k, by.to_int(bytearray(v), True)))

print("## int_to()")
n = [
    0,
    1,
    32768,     # 0x8000
    32769,     # 0x8001
    255        # 0xff
    ]
for i in n:
    print("%d => %s" % (i, by.to_bit(by.int_to(i))))

print("- fixed width")
w = [ 4, 1 ]
for j in w:
    for i in n:
        print("%d => %s" % (i, by.to_bit(by.int_to(i, j))))

#
# test for bitutil
#
print("## bit_get()")
n = [
    0,
    1,
    32768,     # 0x8000
    32769,     # 0x8001
    255        # 0xff
    ]
for i in n:
    ba = by.int_to(i)
    print("- %s" % by.to_bit(ba))
    for j in range(len(ba)*8):
        print("    %s" % bi.bit_get(ba, j, 6))

print("## bit_set()")
# 0010 0011 1100 0010
ba0 = bytearray(2)
bi.bit_set(ba0, 2)
bi.bit_set(ba0, 6, "1111")
bi.bit_set(ba0, 14)
print(by.to_bit(ba0))

print("- implicit")
for i in range(17):
    ba0 = bytearray(2)
    bi.bit_set(ba0, i)
    print(" ", by.to_bit(ba0))

print("- 1")
for i in range(17):
    ba0 = bytearray(2)
    bi.bit_set(ba0, i, "1")
    print(" ", by.to_bit(ba0))

print("- 10")
for i in range(17):
    ba0 = bytearray(2)
    bi.bit_set(ba0, i, "10")
    print(" ", by.to_bit(ba0))

print("- 01")
for i in range(17):
    ba0 = bytearray(2)
    bi.bit_set(ba0, i, "01")
    print(" ", by.to_bit(ba0))

print("- 110")
for i in range(17):
    ba0 = bytearray(2)
    bi.bit_set(ba0, i, "110")
    print(" ", by.to_bit(ba0))

print("## int_to_bit()")
n = [ 0, 1,
     32768,     # 0x8000
     32769,     # 0x8001
     255        # 0xff
     ]
w = [ 32, 8 ]
for j in w:
    for i in n:
        print("%d %d => %s" % (i, j, bi.int_to_bit(i, j)))

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
        p, q = bi.bit_find(i, j)
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
        print(fmt % (i, bi.bit_count(i, j)))

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
        print(fmt % (i, bi.bit_count(i, j, zero=True)))



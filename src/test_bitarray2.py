from bitarray import BitBuffer

print("""
      ## set_bit()
      """)
a = BitBuffer()
a.set_bit(0)
a.set_bit(0)
a.set_bit(1)
a.set_bit(1)
a.set_bit(1)
a.set_bit(0)
a.set_bit(1)
print(a.get_content()) # 0011 1010 : \x3a
print(a)
assert str(a) == r"b'\x3a'/7"

a.set_bit(1, 0)
a.set_bit(0, 3)
print(a.get_content()) # 1010 1010 : \xaa
print(a)
assert str(a) == r"b'\xaa'/7"

print("""
## add_bits()
      """)
a = BitBuffer()
a.add_bits(7, 4) # rule : 0111
a.add_bits(2, 3) # dtag : 010
print("added bits:", a.count_added_bits())
print("padding bits:", a.count_padding_bits())
print("remaining bits:", a.count_remaining_bits())
assert a.count_added_bits() == 7
assert a.count_padding_bits() == 1
assert a.count_remaining_bits() == 7
a.add_bits(3, 3) # win  : 011
a.add_bits(6, 3) # fcn  : 110
print(a.get_content())
print(a)
# 0111 0100 1111 0000 : \x74f0
assert str(a) == r"b'\x74\xf0'/13"

print("""
## copy()
      """)
b = a.copy()
assert str(b) == str(a)
assert id(b) != id(a)
assert id(b._content) != id(a._content)

print("""
## get_bits()
      """)
print(b.get_bits(4), ": rule = 7, rpos =", b._rpos)
print(b.get_bits(3), ": dtag = 2, rpos =", b._rpos)
print("added bits:", b.count_added_bits())
print("padding bits:", b.count_padding_bits())
print("remaining bits:", b.count_remaining_bits())
assert b.count_added_bits() == 13
assert b.count_padding_bits() == 3
assert b.count_remaining_bits() == 6
print(b.get_bits(3), ": win  = 3, rpos =", b._rpos)
print(b.get_bits(3), ": fcn  = 6, rpos =", b._rpos)
print("remaining bits:", b.count_remaining_bits())
assert b.count_remaining_bits() == 0

print("""
## get_bits(position)
      """)
b = a.copy()
print(b.get_bits(4, 0), ": rule = 7, rpos =", b._rpos)
print(b.get_bits(3, 4), ": dtag = 2, rpos =", b._rpos)
print("added bits:", b.count_added_bits())
print("padding bits:", b.count_padding_bits())
print("remaining bits:", b.count_remaining_bits())
assert b.count_added_bits() == 13
assert b.count_padding_bits() == 3
assert b.count_remaining_bits() == 13
print(b.get_bits(3, 7), ": win  = 3, rpos =", b._rpos)
print(b.get_bits(3,10), ": fcn  = 6, rpos =", b._rpos)
print("remaining bits:", b.count_remaining_bits())
assert b.count_remaining_bits() == 13

print("""
## __add__
      """)
# the header size is 27 bits.
# frag: 0000 0001 0000 0002 0000 0003 111
c = BitBuffer([1, 2, 3])
c.add_bits(7, 5)
b = a + c
print("a =", a)
print("c =", c)
print("a + c =", b)
assert str(b) == r"b'\x74\xf0\x08\x10\x19\xc0'/42"

print("""
### print out
      """)
a.display()
print(a)


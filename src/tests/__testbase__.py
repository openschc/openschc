_l=[f for f in locals() if str(f).startswith("test_")]

for l in _l:
    f = locals()[l]
    f()


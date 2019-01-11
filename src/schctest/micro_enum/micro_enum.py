def _enummeta(**kwargs):
    return type("EnumMeta", (), kwargs)

def enum(**kwargs):
    d = {}
    for kv in kwargs.items():
        d[kv[0]] = _enummeta(name=kv[0], value=kv[1])
    return type("Enum", (), d)

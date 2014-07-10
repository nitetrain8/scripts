

def encode(pwd, key):
    pwd = pwd.encode('ascii')
    if type(key) is str:
        key = key.encode('ascii')
    elif type(key) not in (bytes, bytearray):
        raise TypeError("Key must be str or bytes")
    if len(pwd) != len(key):
        raise ValueError("Key and pwd must be same length")
    hash = bytearray(len(pwd))
    for i, (p, k) in enumerate(zip(pwd, key)):
        h = p ^ k
        hash[i] = h
    return hash


def decode(hash, key):

    pwd = bytearray(len(hash))
    for i, (h, k) in enumerate(zip(hash, key)):
        p = h ^ k
        pwd[i] = p
    return pwd.decode('utf-8')


def testhash(strs=None):
    from random import randint
    if strs is None:
        strs = [
            "Hello world",
            "bye world",
            "foo",
            "supercalifradulisticexpialodocis",
            "The quick brown fox jumped over the lazy dog",
        ]

    if type(strs) is str:
        strs = [strs]

    for s in strs:
        key = bytes(randint(0, 255) for _ in range(len(s)))

        hash = encode(s, key)
        result = decode(hash, key)

        print(s, result, s == result)
        assert decode(encode(s, key), key) == s


if __name__ == '__main__':
    testhash()

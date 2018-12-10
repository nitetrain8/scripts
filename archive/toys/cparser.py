"""

Created by: Nathan Starkweather
Created on: 04/09/2016
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'

import logging

logger = logging.getLogger(__name__)
_h = logging.StreamHandler()
_f = logging.Formatter("%(created)s %(name)s %(levelname)s (%(lineno)s): %(message)s")
_h.setFormatter(_f)
logger.addHandler(_h)
logger.propagate = False
logger.setLevel(logging.DEBUG)
del _h, _f


import string

identifier_chars = string.ascii_letters + string.digits + "_"
start_identifier_chars = string.ascii_letters + "_"

def tokenize_c_limited(s):
    tokens, _ = _parse_c_limited_inner(s, 0)
    return tokens


def _parse_c_limited_inner(s, pos):
    n = len(s)
    typs = []
    cur_type = None
    cur_ident = None
    in_comment = False
    tokens = []
    id_start = 0

    def getchar():
        nonlocal s, pos
        c = s[pos]
        pos += 1
        return c

    def unget():
        nonlocal s, pos
        pos -= 1

    while pos < n:
        try:
            c = getchar()
        except IndexError:
            break
        # consume whitespace
        if c in string.whitespace:
            continue
        # consume comments
        elif c == '/':
            c = getchar()
            if c == '/':  # line comment
                while c != '\n':
                    try:
                        c = getchar()
                    except IndexError:
                        raise IndexError("EOF parsing line comment") from None
            elif c == '*':  # block comment
                while True:
                    c = getchar()
                    if c == '*':
                        c = getchar()
                        if c == '/':
                            break
                continue
        elif c == ';':
            tokens.append(c)
            continue
        elif c == ',':
            tokens.append(c)
            continue
        elif c in start_identifier_chars:
            id_start = pos - 1
            while True:
                c = getchar()
                if c not in identifier_chars:
                    token = s[id_start:pos - 1]
                    tokens.append(token)
                    pos -= 1
                    break
        elif c == '{':
            tokens.append('{')
            toks, pos = _parse_c_limited_inner(s, pos)
            tokens.extend(toks)
        elif c == '*':
            tokens.append(c)
        elif c == '#':  # ignore preprocessor. the real tokenizer step comes after preprocessing anyway.
            while True:
                c = getchar()
                if c == '\n':
                    break
            continue
        elif c == '}':
            tokens.append('}')
            break
        else:
            raise ValueError("Token %s at position %d" % (c, pos - 1))
    return tokens, pos


def parse_tokens_limited(tokens):
    typs = _parse_tokens_limited_inner(tokens)
    return typs


modifiers = [
    'const'
]

toplevel_kw = [
    'typedef',
]

known_macros = [
    'PyObject_VAR_HEAD'
]

reserved = toplevel_kw.copy()
reserved.append('struct')
reserved.extend(('int', 'long', 'char', 'unsigned'))


def _parse_tokens_limited_inner(tokens):
    n = len(tokens)
    pos = 0
    slots = []
    current_type = ""
    have_valid_type = False

    def gettok():
        nonlocal tokens, pos
        tok = tokens[pos]
        pos += 1
        return tok

    while pos < n:
        tok = gettok()
        if tok in toplevel_kw:
            continue
        elif tok in known_macros:
            current_type = ""
            have_valid_type = False
            continue
        elif tok in modifiers:
            current_type += tok
            continue
        elif tok.isidentifier():
            if not current_type:
                current_type = tok
                if tok not in reserved:
                    have_valid_type = True
                continue
            elif have_valid_type:
                slots.append((current_type, tok))
                continue
            else:
                current_type += " " + tok
                have_valid_type = True
                continue
        elif tok == ",":
            assert current_type
            while True:
                tok = gettok()
                if tok == ';':
                    break
                slots.append((current_type, tok))
            pos -= 1
            continue
        elif tok == '*':
            current_type += " *"
            continue
        elif tok == ';':
            current_type = ""
            have_valid_type = False
            continue
        elif tok == '{':
            if current_type:
                if have_valid_type:
                    *typ, name = current_type.split()
                    typ = ''.join(typ)
                    slots.append((typ, name))
                    current_type = ''
                    have_valid_type = False
                else:
                    raise ValueError(current_type, pos)
            continue
        elif tok == '}':
            continue
        else:
            raise ValueError("Invalid token: %s pos %d" % (tok, pos))



    return slots


def extract_pytypeobject_fields():
    with open("C:/.replcache/pytypeobject.txt", 'r') as f:
        pto = f.read()
    tokens = tokenize_c_limited(pto)
    print(tokens)
    typs = parse_tokens_limited(tokens)
    print(typs)
    import sys
    f = sys.stdout
    f.write("slots = [\n")
    for typ, name in typs:
        if name.startswith('tp_'):
            f.write("    (\"%s\", \"%s\"),\n" % (typ, name))
    f.write("]")


def list_unique_typedefs():
    with open("C:/.replcache/pytypeobject.txt", 'r') as f:
        pto = f.read()
    tokens = tokenize_c_limited(pto)
    typs = parse_tokens_limited(tokens)
    seen = set()
    import sys
    f = sys.stdout
    for typ, _ in typs:
        if typ in seen:
            continue
        seen.add(typ)
        f.write(typ)
        f.write('\n')

if __name__ == '__main__':
    list_unique_typedefs()

import json

from Op import Op


SEP = b'\0'
WATERMARK = b'Rick' + SEP


def mem(*space):
    return json.dumps(space).encode() + SEP


def ins(*space):
    return b''.join(space) + Op.END


def code(mem, ins):
    return WATERMARK + mem + ins


def i32(n):
    return n.to_bytes(4, 'big')


def write(code, path):
    with open(path, 'wb') as file:
        file.write(code)

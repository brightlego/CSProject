import functools
import datetime

def lcprng(seed, a=4294967297, c=875810, m=11111111111111111111111):
    while True:
        yield seed
        seed = (a*seed + c) % m


def get_random_hex(seed, length, word_size=8):
    out = ""
    for i, _ in zip(lcprng(seed), range(length)):
        out += f"{i%2**(word_size):x}"

    out = out.ljust(length * word_size // 4, '0')
    return out


def gen_seed():
    time = datetime.datetime.now()
    seed = time.timestamp()
    seed *= 1000000
    return int(seed)

def hash_(text):
    if isinstance(text, str):
        text = bytes(text, "utf-8")

    if len(text) == 0:
        text = b"\0\0"
    elif len(text) == 1:
        text = b"\1" + text
    else:
        text = b"\2" + text

    for _ in range(text[0] + 5):
        seed = functools.reduce(lambda a, b : a*b + (a-b), text[:max(text[0], 2)])
        text = [i ^ j for i, j in zip(text, lcprng(seed))]

    seed = functools.reduce(lambda a, b : a*b + (a - b), text)
    return get_random_hex(seed, 32)


if __name__ == '__main__':
    print(hash_("abcd"))
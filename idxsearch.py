#!/usr/bin/python2

import argparse, os, struct, sys

# usage: idxsearch.py -k 8 869a mkidx.out.00
parser = argparse.ArgumentParser()

parser.add_argument("-k", "--key-size", type=int, default = 8, help="length of key")
parser.add_argument("-v", "--val-size", type=int, default = 8, help="length of value")
parser.add_argument("-d", "--debug", default=False, nargs="?", help="debug output")
parser.add_argument("key")
parser.add_argument("files", nargs="+")

args = parser.parse_args()

struct_format = "=" + str(args.key_size) + "sQ"

if args.key.startswith("0x"):
    args.key = args.key[2:]

args.key = " "*(args.key_size - len(args.key)) + args.key

chunk_size = args.key_size + args.val_size

def read_chunk(fd):
    chunk = os.read(fd, chunk_size)
    return struct.unpack(struct_format, chunk)

found = False

for f in args.files:
    file_size = os.stat(f).st_size
    chunks = file_size / chunk_size - 1
    chunk = chunks / 2

    if args.debug:
        print "[Opened %s with %s chunks]" % (f, chunks)

    fd = os.open(f, os.O_RDONLY)

    chunk_max = chunks
    chunk_min = 0
    while chunk_max >= chunk_min:

        mid = chunk_min + ((chunk_max - chunk_min)/2)

        if args.debug:
            print "New bounds [%s, %s, %s]" % (chunk_min, mid, chunk_max)

        os.lseek(fd, (mid) * chunk_size, os.SEEK_SET)
        (key, value) = read_chunk(fd)

        if key == args.key:
            print value
            found = True
            break
        elif key < args.key:
            chunk_min = mid + 1
        else:
            chunk_max = mid - 1
    os.close(fd)

    if found:
        sys.exit(0)

if not found:
    print "not found"
    sys.exit(1)

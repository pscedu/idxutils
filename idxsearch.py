#!/usr/bin/python2

import argparse
import os
import struct
import sys

# usage: idxsearch.py -k 8 869a mkidx.out.00
parser = argparse.ArgumentParser()

parser.add_argument("-k", "--key-size", type=int, default = 8, help="length of key")
parser.add_argument("-v", "--val-size", type=int, default = 8, help="length of value")
parser.add_argument("key")
parser.add_argument("file")

args = parser.parse_args()

args.key = " "*(args.key_size - len(args.key)) + args.key

chunk_size = args.key_size + args.val_size

def read_chunk(fd):
    chunk = os.read(fd, chunk_size)
    return struct.unpack("8sQ", chunk)

file_size = os.stat(args.file).st_size
chunks = file_size / chunk_size
chunk = chunks / 2

fd = os.open(args.file, os.O_RDONLY)
os.lseek(fd, chunk*chunk_size, os.SEEK_SET)

max = chunks
min = 0
while 0 <= chunk and chunk < chunks:
    (key, value) = read_chunk(fd)
    if args.key > key:
        min = chunk
        chunk = (chunk + max) / 2	
    elif args.key < key:
        max = chunk
        chunk = chunk / 2 
    else:
        print value
        os.close(fd)
        sys.exit(0)
    os.lseek(fd, chunk * chunk_size, os.SEEK_SET)
        
os.close(fd)
print "key not found."
sys.exit(1)

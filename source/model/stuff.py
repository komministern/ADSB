#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np      # Would be nice to eliminate this dependancy

def asciistring_to_binstring(asciis):
    bins = ""
    for c in asciis:
        bins += int_to_binstring(ord(c), 8)
        #bins += np.binary_repr(ord(c), 8)
    return bins

def binstring_to_asciistring(bins):
    asciis = ""
    for b in split_len(bins, 8):
        asciis += chr(binstring_to_int(b))
    return asciis

def int_to_binstring(decnum, nbrofbits):
    return np.binary_repr(decnum, nbrofbits)

def binstring_to_int(bins):
    decnum = 0
    rank = 1
    for i in reversed(bins):
        decnum += rank * int(i)
        rank *= 2
    return decnum

def binstring_to_sint(bins):        # Only works for 16 bit numbers.
    ui = binstring_to_int(bins)
    if ui > 32767:
        ui -= 65536
    return ui


def split_len(seq, length):
    return [seq[i:i+length] for i in range(0, len(seq), length)]




if __name__ == "__main__":

    s = 'ab hello'
    b = asciistring_to_binstring(s)
    print b
    s2 = binstring_to_asciistring(b)
    print s2


#!/usr/bin/env python

# Yachao Guo 2021

import sys
import os

if len(sys.argv) != 3:
    print("Usage: python replace_words_in_kaldi_text.py <kaldi-text> <only-hotword-path> ")
    exit(1)
else:
    text_ground = sys.argv[1]
    only_hotword = sys.argv[2]


def text_Convert_hotword(text, word):
    file_load = open(text, "r")
    file_write = open(word, "a")
    for line in file_load:
        arr = []
        arr_out = []
        arr = line.strip().split(" ")
        arr_out.append(arr[0])
        for x in arr:
            if x.startswith("__"):
                arr_out.append(x)
                print(x)
        j = len(arr_out)
        i = 0
        if j > 0:
            for y in arr_out:
                if i != j - 1:
                    file_write.write(y + " ")
                    i = i + 1
                else:
                    file_write.write(y)
                    file_write.write("\n")
        else:
            file_write.write("\n")

    file_load.close()
    file_write.close()


def main():
    os.mknod(only_hotword)
    text_Convert_hotword(text_ground, only_hotword)


if __name__ == '__main__':
    main()


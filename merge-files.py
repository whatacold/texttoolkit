#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys


def usage():
    print('''
Usage: {} <merged-file> <separator> <file1> <file2> [<file3> ...]
''')
    sys.exit(1)


def merge_multi_lines(separator, *multi_lines):
    '''Merge every line of `multi_lines` into a new line, which are
delimited by the separator.'''
    merged_lines = []
    line_no = 0

    while True:
        cols = []
        eof_cnt = 0
        for lines in multi_lines:
            if line_no >= len(lines):  # reach the end
                cols.append('')
                eof_cnt += 1
            else:
                cols.append(lines[line_no])

        if eof_cnt == len(multi_lines):
            break
        else:
            merged_lines.append(separator.join(cols))
        line_no += 1

    return '\n'.join(merged_lines)


def main():
    if len(sys.argv) < 5:
        usage()

    merged_file = sys.argv[1]
    separator = sys.argv[2]
    multi_lines = []

    # read in files
    for fname in sys.argv[3:]:
        with open(fname) as f:
            lines = []
            for line in f.readlines():
                lines.append(line.strip('\n'))
            multi_lines.append(lines)

    with open(merged_file, "w") as f:
        f.write(merge_multi_lines(separator, *multi_lines) + '\n')


if __name__ == '__main__':
    main()

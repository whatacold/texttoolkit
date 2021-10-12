#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys


def usage(argv):
    sys.stderr.write('''Usage: {} <joined-file> <delimiter> <column-file1> <column-file2> [...column-files]

Take a line from every `column-file`, and join them into a line of
`joined-file`.
The line is delimited by `delimiter`, which  is a non-newline character
such as ',', ':'.

At least 2 column-files should exist.
''')
    sys.exit(1)


def column_split(joined_file, delimiter, col_files):
    '''Take every line of each `col_files`, and join them into `joined_file`,
delimited by `delimiter`.
'''
    # open the files
    col_fh = []
    for f in col_files:
        col_fh.append(open(f, "rb"))

    delimiter = bytes(delimiter, encoding='utf-8')
    with open(joined_file, 'wb') as joined_fh:
        while True:
            cols = []
            for f in col_fh:
                line = f.readline()
                if not line:
                    break

                line = line[0:-1] if line[-1] == 10 else line  # strip \n
                cols.append(line)

            print(cols)
            if len(cols) != len(col_files):  # at least one file has reached its eof
                break
            else:
                joined_fh.write(delimiter.join(cols) + b'\n')

    for f in col_fh:
        f.close()


def main(argv):
    if len(argv) < 5:
        usage(argv)

    joined_file = argv[1]
    delimiter = argv[2]
    column_split(joined_file, delimiter, argv[3:])


if __name__ == '__main__':
    main(sys.argv)

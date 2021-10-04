#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import re


'''A simple compilation database generator, or cdg in short.

It works by parsing the output of the GNU make command.'''

file_name_regex = re.compile(r"[\w./+\-]+\.(s|cc?|cpp|cxx)\b",
                             re.IGNORECASE)
enter_dir_regex = re.compile(r"^\s*make(?:\[\d+\])?: Entering directory [`\'\"](?P<dir>.*)[`\'\"]\s*$",
                             re.MULTILINE)
leave_dir_regex = re.compile(r"^\s*make(?:\[\d+\])?: Leaving directory .*$",
                             re.MULTILINE)
compilers_regex = re.compile(r'\b(g?cc|[gc]\+\+|clang\+?\+?|icecc|s?ccache)\s')


def parse(make_output):
    '''Parse the make output into a list of objects.

Per https://clang.llvm.org/docs/JSONCompilationDatabase.html
'''
    result = []
    pwd = ""
    path_stack = []
    for line in make_output.replace('\r', '').split('\n'):
        line = line.strip()

        enter_dir_match = enter_dir_regex.match(line)
        if enter_dir_match:
            pwd = enter_dir_match.group('dir')
            path_stack.append(pwd)
            # logger.debug("stack after append: {}".format(path_stack))
            continue
        elif leave_dir_regex.match(line):
            # logger.debug("stack before pop: {}".format(path_stack))
            path_stack.pop()
            if path_stack:
                pwd = path_stack[-1]
            continue

        match = compilers_regex.search(line)
        if not match:
            continue

        # look backward and discard anything before delimiters
        i = match.start()
        while i > 0:
            j = i - 1
            if line[j] in (' ', '\t', '\n', ';', '&'):
                break
            i -= 1
        line = line[i:]

        file_match = file_name_regex.search(line)
        # logger.debug(line, file_match)
        if not file_match:
            continue

        # To workaround that there is no "entering directory..."
        if not pwd:
            pwd = "/path/to/your/project/"
            path_stack.append(pwd)

        # Special handling for projects like Redis, which has output like "printf xxx; cc xxx"
        command = line
        ri = command.rfind(';')
        if -1 != ri:
            command = command[:ri]
        ri = command.rfind('&&')
        if -1 != ri:
            command = command[:ri]

        result.append({
            "directory": pwd.strip(),
            "file": file_match.group(0).strip(),
            "command": command.strip(),
        })

    return result

def usage():
    print('usage')
    sys.exit(1)

def main():
    make_output = sys.stdin.read()
    if not make_output:
        usage()

    sys.stdout.write(json.dumps(parse(make_output),
                                indent=2))
    sys.stdout.write('\n')

if __name__ == '__main__':
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import re


'''A simple compilation database generator, or cdg in short.

It works by parsing the output of the GNU make command.'''

file_name_regex = re.compile(r"[\w./+\-]+\.(s|cc?|cpp|cxx)\b",
                             re.IGNORECASE)
enter_dir_regex = re.compile(r"^\s*(?:make|ninja)(?:\[\d+\])?: Entering directory [`\'\"](?P<dir>.*)[`\'\"]\s*$",
                             re.MULTILINE)
leave_dir_regex = re.compile(r"^\s*(?:make|ninja)(?:\[\d+\])?: Leaving directory .*$",
                             re.MULTILINE)
compilers_regex = re.compile(r'\b(g?cc|[gc]\+\+|clang\+?\+?|icecc|s?ccache)(?:.exe)?"?\s')


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
        if line[match.start():match.end()].rstrip()[-1] == '"':
            while i > 0:
                i -= 1
                if line[i] == '"' and (i == 0 or line[i-1] != '\\'):
                    break
        else:
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

        # Special handling for projects like Redis,
        # which has output like "printf xxx; cc xxx"
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
    print('''Usage: {} [compilation-db-file]

[compilation-db-file] is optional, which is `compile_commands.json` by default.
Specify it if you want to write to another file, and specify `-` for stdout.

This CLI program takes GNU make output from stdin from a pipe,
parse it, and write the json string to a file.
'''.format(sys.argv[0]))
    sys.exit(1)


def main():
    make_output = sys.stdin.read().strip()
    if not make_output:
        usage()

    db = json.dumps(parse(make_output),
                    indent=2) + '\n'
    file_name = 'compile_commands.json' if len(sys.argv) == 1 else sys.argv[1]
    if '-' != file_name:
        with open(file_name, "w") as f:
            f.write(db)
    else:
        sys.stdout.write(db)


if __name__ == '__main__':
    main()

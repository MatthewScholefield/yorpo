import re
from argparse import ArgumentParser
from glob import glob
from os import chdir
from os.path import join, abspath


class Source:
    def __init__(self, excluded: list = None):
        self.include_lines = []
        self.local_includes = ['#include "{}"'.format(i) for i in excluded or []]
        self.other_lines = []

        self.seen = set(excluded or [])

    def add(self, filename):
        if filename in self.seen:
            return
        with open(filename) as f:
            deps, source = extract_deps(f.read())
        for dep in sorted(set(deps) - self.seen):
            self.add(dep)
        for line in source.split('\n'):
            if re.match(r'\s*#include', line):
                self.include_lines.append(line)
            else:
                self.other_lines.append(line)
        self.other_lines.extend(['', '', ''])
        self.seen.add(filename)

    def compile(self):
        source = '\n\n'.join([
            '\n'.join(sorted(set(self.include_lines))),
            '\n'.join(sorted(set(self.local_includes))),
            '\n'.join(self.other_lines)
        ])
        return re.sub(r'\n([ \t]*\n){2,}', '\n\n\n', source)


def extract_deps(file_source: str):
    deps = []
    parts = []
    last_pos = 0
    for m in re.finditer(r'^\s*#include\s*"([^"]+)"\s*', file_source, re.MULTILINE):
        a, b = m.span()
        parts.append(convert_from_header(file_source[last_pos:a]))
        last_pos = b
        deps.append(m.group(1))
    parts.append(convert_from_header(file_source[last_pos:]))
    return deps, ''.join(parts)


def convert_from_header(file_source: str):
    return file_source.replace('#pragma once', '')


def main():
    parser = ArgumentParser(description='Tool to merge C/C++ source files')
    parser.add_argument('source_root')
    parser.add_argument('out_file', type=abspath)
    parser.add_argument('-e', '--exclude', nargs='+', help='Files to not concatenate')
    args = parser.parse_args()

    chdir(args.source_root)

    sources = sum([glob(join('**', ext), recursive=True) for ext in ['*.c', '*.cpp', '*.cxx']], [])

    source = Source(args.exclude)
    for filename in sources:
        source.add(filename)

    with open(args.out_file, 'w') as f:
        f.write(source.compile())


if __name__ == '__main__':
    main()

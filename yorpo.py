import re
from argparse import ArgumentParser
from glob import glob
from os import chdir, walk
from os.path import join, abspath, basename, relpath, splitext, isdir, isfile


class Source:
    def __init__(self, excluded: list = None):
        self.include_lines = []
        self.local_includes = []
        self.other_lines = []

        self.excluded = set(excluded or [])
        self.seen = set()

    def add(self, filename):
        if filename in self.seen:
            return
        with open(filename) as f:
            deps, source = extract_deps(f.read())
        for dep in sorted(set(deps) - self.seen):
            if dep in self.excluded:
                self.seen.add(dep)
                self.local_includes.append('#include "{}"'.format(dep))
            else:
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


LANGUAGE_MAP = {
    '.c': 'c',
    '.h': 'c',
    '.cpp': 'cpp',
    '.cxx': 'cpp',
    '.cc': 'cpp',
    '.hpp': 'cpp',
    '.hxx': 'cpp',
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.jsx': 'jsx',
    '.tsx': 'tsx',
    '.java': 'java',
    '.go': 'go',
    '.rs': 'rust',
    '.rb': 'ruby',
    '.sh': 'bash',
    '.bash': 'bash',
    '.zsh': 'bash',
    '.md': 'markdown',
    '.json': 'json',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.toml': 'toml',
    '.html': 'html',
    '.css': 'css',
    '.scss': 'scss',
    '.sql': 'sql',
    '.xml': 'xml',
}


def get_language(filename: str) -> str:
    _, ext = splitext(filename)
    return LANGUAGE_MAP.get(ext.lower(), '')


def collect_files(root: str, exclude: list = None) -> list:
    """Recursively collect all text files from root, sorted by relative path."""
    excluded = set(exclude or [])
    files = []
    for dirpath, dirnames, filenames in walk(root):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith('.'))
        for filename in sorted(filenames):
            if filename.startswith('.'):
                continue
            filepath = join(dirpath, filename)
            rel = relpath(filepath, root)
            if basename(rel) not in excluded and rel not in excluded:
                files.append(rel)
    return files


def _fence_for(content: str) -> str:
    """Return the shortest backtick fence that does not appear in content."""
    max_run = 0
    run = 0
    for ch in content:
        if ch == '`':
            run += 1
            max_run = max(max_run, run)
        else:
            run = 0
    return '`' * max(3, max_run + 1)


def merge_to_markdown(root: str, files: list, out_file: str):
    """Merge files into a single markdown file with annotated relative paths."""
    sections = []
    for rel_path in files:
        filepath = join(root, rel_path)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except (UnicodeDecodeError, IOError):
            continue
        lang = get_language(rel_path)
        fence = _fence_for(content)
        sections.append('### `{}`\n\n{}{}\n{}\n{}'.format(rel_path, fence, lang, content, fence))
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write('\n\n---\n\n'.join(sections))
        f.write('\n')


def main():
    parser = ArgumentParser(description='Tool to merge source files')
    parser.add_argument('sources', nargs='+',
                        help='Source directory or list of files to process')
    parser.add_argument('out_file', type=abspath)
    parser.add_argument('-e', '--exclude', nargs='+', help='Files to not include')
    parser.add_argument('-x', '--extension', help='Filter files by extension (e.g., .tex, .py)')
    parser.add_argument('-m', '--markdown', action='store_true',
                        help='Merge all files into a single markdown file with annotated relative paths')
    args = parser.parse_args()

    # Determine if we're working with explicit file list or directories
    input_files = []
    input_dirs = []
    for path in args.sources:
        if isfile(path):
            input_files.append(abspath(path))
        elif isdir(path):
            input_dirs.append(abspath(path))
        else:
            parser.error(f"'{path}' is not a valid file or directory")

    if args.markdown:
        # Markdown mode
        if input_files and input_dirs:
            parser.error("Cannot mix files and directories in markdown mode")
        if input_files:
            # Use explicit file list
            root = abspath('.')
            files = [relpath(f, root) for f in input_files]
        else:
            # Use directory (use first directory if multiple provided)
            root = input_dirs[0]
            files = collect_files(root, args.exclude)

        # Filter by extension if specified
        if args.extension:
            ext = args.extension if args.extension.startswith('.') else '.' + args.extension
            files = [f for f in files if splitext(f)[1].lower() == ext.lower()]

        merge_to_markdown(root, files, args.out_file)
    else:
        # C/C++ mode
        if input_files:
            # Use explicit file list
            excluded = set(args.exclude or [])
            source = Source(args.exclude)
            for filepath in sorted(input_files):
                source.add(filepath)
            with open(args.out_file, 'w') as f:
                f.write(source.compile())
        else:
            # Use directory mode (existing behavior)
            if len(input_dirs) > 1:
                parser.error("Cannot specify multiple directories in C/C++ mode")
            chdir(input_dirs[0])
            excluded = set(args.exclude or [])

            # Use custom extensions if provided, otherwise default to C/C++
            extensions = [args.extension] if args.extension else ['*.c', '*.cpp', '*.cxx']
            # Ensure extensions start with dot and have wildcard
            extensions = [ext if ext.startswith('.') else '.' + ext for ext in extensions]
            extensions = ['*' + ext for ext in extensions]

            sources = {
                i
                for ext in extensions
                for i in glob(join('**', ext), recursive=True)
                if basename(i) not in excluded
            }

            source = Source(args.exclude)
            for filename in sorted(sources):
                source.add(filename)

            with open(args.out_file, 'w') as f:
                f.write(source.compile())


if __name__ == '__main__':
    main()

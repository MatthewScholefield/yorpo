# Yorpo

*Tool to merge C/C++ source files*

Often for things like coding competitions or school assignments
it's required to submit a single source file. However, developing
out of a single file is cumbersome and limits growth of the project.
This tool solves that problem by effortlessly concatenating sources,
properly resolving header dependencies.

## Usage

```bash
yorpo source_folder_root/ out_file.c
```

Optionally, you can pass `--exclude file1.c file2.cpp ... filen.cpp`
to keep certain local `#include` directives.

## Installation

```bash
pip3 install --user yorpo
```

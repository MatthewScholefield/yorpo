# Yorpo

*Tool to merge source files*

Often for things like coding competitions or school assignments it's required to
submit a single source file. However, developing out of a single file is
cumbersome and limits growth of the project. Yorpo solves that problem by
effortlessly concatenating sources.

Yorpo also works as a general **file merger** tool: it can merge any set of
files into a single annotated Markdown document, which is especially useful for
providing a codebase as context to an LLM.

## Usage

### C/C++ merge (default)

Recursively merges all `.c`/`.cpp`/`.cxx` files, resolving local `#include`
dependencies and deduplicating system includes:

```bash
yorpo source_folder_root/ out_file.c
```

Optionally pass `--exclude file1.c file2.cpp ...` to keep certain local
`#include` directives intact instead of inlining them.

### Markdown merge (`-m` / `--markdown`)

Merges **all** text files under a directory into a single Markdown file where
each file is introduced by its relative path and wrapped in a fenced code block
with automatic language detection:

```bash
yorpo -m source_folder_root/ context.md
```

Example output:

````markdown
### `src/main.py`

```python
print("hello")
```

---

### `README.md`

```markdown
# My project
```
````

The `--exclude` flag works the same way in both modes.

## Installation

```bash
pip3 install --user yorpo
```

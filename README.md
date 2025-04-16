# Org Chart Generator

# Overview

Converts text file into an org chart in one of three formats: text, Visio-formatted text, or Mermaid flowchart.

# Dependencies
- Python 3.13+
- graphviz (only needed for SVG output)

# Usage
`python main.py [filename] [-f format]`

- -f: one of 'tree', 'visio', 'mermaid'
- filename: path to the input text file
- -h: print this help message

# Example
`python main.py org-sample.txt -f tree`

# Format of the input file
- Each line is indented below the position/person it reports to
- Lines without indentation are ignored
- Lines starting with '#' are ignored
- Empty lines are ignored

# Output formats
- tree: tab-indented tree
- visio: text file suitable for import into Visio Org Chart
- mermaid: Mermaid flowchart
- svg: SVG image (using graphviz)

# License
[MIT License](LICENSE.md)
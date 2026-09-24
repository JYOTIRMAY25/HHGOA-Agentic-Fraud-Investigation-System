#!/usr/bin/env python3
"""Debug schema parser."""
import re

with open('tigergraph/schema/schema.gsql') as f:
    content = f.read()

content_no_comments = re.sub(r'//.*', '', content)

STATEMENT_STARTERS = [
    'DROP GRAPH', 'CREATE GRAPH', 'USE GRAPH',
    'CREATE VERTEX', 'CREATE DIRECTED EDGE', 'CREATE EDGE',
    'CREATE QUERY', 'INTERPRET QUERY', 'ALTER',
]

statements = []
current = None
for line in content_no_comments.split('\n'):
    stripped = line.strip()
    if stripped == '':
        continue
    is_new = any(stripped.startswith(s) for s in STATEMENT_STARTERS)
    if is_new:
        if current is not None:
            statements.append(current)
        current = stripped
    else:
        if current is not None:
            current += ' ' + stripped
if current is not None:
    statements.append(current)

# Filter out DROP/CREATE/USE GRAPH
deploy_stmts = [s for s in statements if not (s.startswith('DROP GRAPH') or s.startswith('CREATE GRAPH') or s.startswith('USE GRAPH'))]

# Add semicolons
formatted = []
for s in deploy_stmts:
    if not s.endswith(';'):
        s += ';'
    formatted.append(s)

# Print vertex statements
for s in formatted:
    if 'CREATE VERTEX' in s:
        print("=" * 80)
        print(s)
        print("=" * 80)
        print()

#!/usr/bin/env python3
"""Parse and generate deployment-ready GSQL with proper statement boundaries."""
import re

with open('tigergraph/schema/schema.gsql') as f:
    lines = f.readlines()

# GSQL keywords that start a new statement
STATEMENT_STARTERS = [
    'DROP GRAPH',
    'CREATE GRAPH',
    'USE GRAPH',
    'CREATE VERTEX',
    'CREATE DIRECTED EDGE',
    'CREATE EDGE',
    'CREATE QUERY',
    'INTERPRET QUERY',
    'ALTER',
]

statements = []
current = None

for line in lines:
    stripped = line.strip()
    
    # Skip comments and empty lines
    if stripped.startswith('//') or stripped == '':
        continue
    
    # Check if this line starts a new statement
    is_new = False
    for starter in STATEMENT_STARTERS:
        if stripped.startswith(starter):
            is_new = True
            break
    
    if is_new:
        if current is not None:
            statements.append(current)
        current = stripped
    else:
        if current is not None:
            current += ' ' + stripped

if current is not None:
    statements.append(current)

# Now each statement should be a complete GSQL statement
# Some may need semicolons added
gsql_lines = []
for stmt in statements:
    # Add semicolon if missing
    if not stmt.endswith(';'):
        stmt += ';'
    gsql_lines.append(stmt)

result = '\n'.join(gsql_lines) + '\n'

with open('tigergraph/schema/schema_deploy.gsql', 'w') as f:
    f.write(result)

print("Generated schema_deploy.gsql:")
print("=" * 60)
for line in gsql_lines:
    print(line[:120] + "..." if len(line) > 120 else line)
print(f"\nTotal statements: {len(gsql_lines)}")

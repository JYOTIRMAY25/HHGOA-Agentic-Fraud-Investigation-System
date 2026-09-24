import os, json

base = 'D:/task4'

# Check .vscode/mcp.json
p = os.path.join(base, '.vscode', 'mcp.json')
print('mcp.json exists:', os.path.exists(p))
if os.path.exists(p):
    with open(p) as f:
        config = json.load(f)
    print('Servers:', list(config.get('servers', {}).keys()))
    for name, s in config['servers'].items():
        print('  %s: type=%s, command=%s, args=%d' % (name, s['type'], s['command'], len(s['args'])))

# Check .env.example
p2 = os.path.join(base, '.env.example')
print('.env.example exists:', os.path.exists(p2))
if os.path.exists(p2):
    with open(p2) as f:
        content = f.read()
    for v in ['TG_HOST','TG_GRAPHNAME','TG_USERNAME','TG_PASSWORD','TG_SECRET','TG_TGCLOUD']:
        print('  %s: %s' % (v, 'FOUND' if v in content else 'MISSING'))
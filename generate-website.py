#!/usr/bin/env python

# re-generate while working:
#>  find generate-website.py templates/* | entr ./generate-website.py

import json
import os
import shutil
from collections import defaultdict
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime
from urllib.parse import quote

OUTPUT = 'website-generated'

env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

with open('data/contributions.json', 'r') as f:
    contributions = json.load(f)

def make_key(node_type, id):
    return f'{node_type}_{int(id):04}'
    
children = defaultdict(list)
for node_type in contributions:
    for id, contrib in contributions[node_type].items():
        try:
            children[make_key(contrib['parent']['node_type'], contrib['parent']['id'])].append((node_type, id))
        except KeyError:
            # root, no parent
            pass
    
with open('data/people.json', 'r') as f:
    people = json.load(f)


template = env.get_template('larallonge.js')
with open(os.path.join(OUTPUT, f"larallonge.js"), 'w') as f:
    f.write(template.render(contributions=json.dumps(contributions, ensure_ascii=False),
                            children=json.dumps(children, ensure_ascii=False)))
print('JS script generated')
    
template = env.get_template('watch.html')
with open(os.path.join(OUTPUT, f"watch.html"), 'w') as f:
    f.write(template.render())
print('Watch page generated')

template = env.get_template('listen.html')
with open(os.path.join(OUTPUT, f"listen.html"), 'w') as f:
    f.write(template.render())
print('Listen page generated')
    
template = env.get_template('larallonge.html')
nodes = []
for node_type in ('dance', 'film'):
    for id, node in contributions[node_type].items():
        nodes.append({'id': id,
                      'node_type': node_type,
                      'date': node['date'],
                      'key': make_key(node_type, id)})
nodes.sort(key=lambda n: n['date'], reverse=True)
with open(os.path.join(OUTPUT, 'index.html'), 'w') as f:
    f.write(template.render(nodes=nodes))

shutil.copy('data/contributions.json', OUTPUT)
    
print(f'Website generated! on { datetime.now() }')

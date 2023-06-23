#!/usr/bin/env python

# re-generate while working:
#>  find generate-website.py templates/* data/* | entr ./generate-website.py

import json
import os
import shutil
from collections import defaultdict
from jinja2 import Environment, FileSystemLoader, select_autoescape
from jinja2_markdown import MarkdownExtension
from datetime import datetime
from urllib.parse import quote

OUTPUT = 'website-generated'

env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape(['html', 'xml'])
)
env.add_extension(MarkdownExtension)

with open('data/contributions.json', 'r') as f:
    contributions = json.load(f)

def make_key(node_type, id):
    return f'{node_type}_{int(id):04}'
    
children = defaultdict(list)
people_contribs = defaultdict(list)
for node_type in contributions:
    for id, contrib in contributions[node_type].items():
        for part in contrib['participations']:
            if node_type in ('film', 'dance'):
                link = f'watch.html?node_type={ node_type }&id={ id }'
            elif node_type == 'music':
                link = f'listen.html?id={ id }'
            else:
                link = ''
            people_contribs[part['person']].append({ 'tree': contrib['tree'],
                                                     'node_type': node_type,
                                                     'id': id,
                                                     'details': part.get('details', ''),
                                                     'link': link })
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


for tmpl in ('watch', 'listen', 'select', 'about', 'people'):
    template = env.get_template(f'{tmpl}.html')
    with open(os.path.join(OUTPUT, f"{tmpl}.html"), 'w') as f:
        f.write(template.render(showLogo=False if tmpl in ('watch, listen') else True,
                                people=people,
                                people_contribs=people_contribs))
    print(f'{tmpl} page generated')
    
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
    f.write(template.render(showLogo=True, nodes=nodes))

shutil.copy('data/contributions.json', OUTPUT)
    
print(f'Website generated! on { datetime.now() }')

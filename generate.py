#!/usr/bin/env python

import os, ffmpy3, subprocess
from collections import OrderedDict as od
import random

# 1 orig folders with following convention
# films are named f0001.mov, f0002.mp4 etc
# musics are named m0001.wav, m0002.wav etc
# dance sessions are named d0001.mov, d0002.mp4 etc

ORIG = "orig"
COMPUTED = "computed"

FILTER = '"nullsrc=size=1280x360 [background]; \
[0:v] setpts=PTS-STARTPTS, scale=640x360 [left]; \
[1:v] setpts=PTS-STARTPTS, scale=640x360 [right]; \
[background][left]       overlay=shortest=1       [background+left]; \
[background+left][right] overlay=shortest=1:x=640"'

LA_RALLONGE = ['film_0001', 'music_0001',
               'film_0002', 'music_0002',
               'film_0003', 'music_0003',
               'film_0004', 'music_0004',
               'film_0005', 'music_0005',
               'film_0006', 'music_0006',
               'film_0007', 'music_0007',
               'film_0008', 'music_0008',
               'film_0009', 'music_0009',
               'film_0010', 'music_0010',
               'film_0011', 'music_0011',
               'film_0012', 'music_0012',
               'film_0013', 'music_0013',
               'film_0014', 'music_0014',
               'film_0015', 'music_0015',
               'film_0016', 'music_0016',
               'film_0017', 'music_0017',
               'film_0018', 'music_0018',
               'film_0019', 'music_0019',
               'film_0020', 'music_0020',
               'film_0021', 'music_0023',
               'film_0022', 'music_0025',
               'film_0023', 'music_0026',
               'film_0024', 'music_0027',
               'film_0025', 'music_0028',
               'film_0026']

LA_RALLONGE_DANSEE = ['music_0010', 'dance_0001',
                      'music_0021', 'dance_0002',
                      'music_0022', 'dance_0003',
                      'music_0024', 'dance_0004']

class Thread(object):
    todo = {
        'gif': [],
        'preview': [],
        'mp4': [],
        'webm': [],
        'ogg': [],
        'm4a': [],
        'pair_webm': [],
        'pair_mp4': []
    }
    def __init__(self, thread_list):
        previous_vid = None
        for node in thread_list:
            if node.startswith('music'):
                self.todo['ogg'].append('{}.{}'.format(node, 'ogg'))
                self.todo['m4a'].append('{}.{}'.format(node, 'm4a'))
                continue
            self.todo['gif'].append('{}.{}'.format(node, 'gif'))
            self.todo['preview'].append(f'{node}_preview.mp4')
            self.todo['preview'].append(f'{node}_preview.webm')
            self.todo['mp4'].append('{}.{}'.format(node, 'mp4'))
            self.todo['webm'].append('{}.{}'.format(node, 'webm'))
            if previous_vid:
                self.todo['pair_webm'].append('{}-{}.{}'.format(previous_vid, node, 'webm'))
                self.todo['pair_mp4'].append('{}-{}.{}'.format(previous_vid, node, 'mp4'))
            previous_vid = node
        present = { fname for fname in os.listdir(COMPUTED) }        
        for filetype in self.todo:
            newlist = []
            for filename in self.todo[filetype]:
                if filename not in present:
                    newlist.append(filename)
            self.todo[filetype]  = newlist
        self.orig = {}
        for filename in os.listdir(ORIG):
            self.orig[filename.split('.')[0]] = filename
    def generate_gifs(self):
        print('Generating gifs')
        for node in self.todo['gif']:
            node = node.split('.')[0]
            outfile = 'computed/{}.gif'.format(node)
            subprocess.check_call(['ffmpeg', '-i', 'computed/{}.webm'.format(node),
                                   '-r', '1/25', 'computed/{}-%03d.png'.format(node)])
            subprocess.check_call('mogrify -resize 256x256 -gravity Center -crop 256x144+0+0 +repage computed/{}-*.png'.format(node),
                                  shell=True)
            subprocess.check_call(
                'convert -delay {} -loop 0 computed/{}-*.png computed/{}.gif'.format(random.randint(60, 100), node, node), 
                shell=True)
            print("{} generated".format(outfile))
        self.todo['gif'] = []
    def generate_previews(self):
        print('Generating previews')
        for node in self.todo['preview']:
            node, ext = node.split('_preview.')
            outfile = f'computed/{node}_preview.{ext}'
            subprocess.check_call(['ffmpeg', '-i', f'computed/{node}.gif', outfile])
            print("{} generated".format(outfile))
        self.todo['gif'] = []
    def generate_mp4s(self):
        print('Generating mp4s')
        for node in self.todo['mp4']:
            node = node.split('.')[0]
            infile = os.path.join(ORIG, self.orig[node])
            outfile = os.path.join(COMPUTED, '{}.mp4'.format(node))
            ff = ffmpy3.FFmpeg(inputs=od([(infile, None)]),
                               outputs={outfile: "-an -map 0:v -vf scale=640:360:force_original_aspect_ratio=decrease -b:v 900k -movflags faststart"})
            ff.run()
            print('    {} generated'.format(outfile))
        self.todo['mp4'] = []
    def generate_webms(self):
        print('Generating webms')
        for node in self.todo['webm']:
            node = node.split('.')[0]
            infile = os.path.join(ORIG, self.orig[node])
            outfile = os.path.join(COMPUTED, '{}.webm'.format(node))
            ff = ffmpy3.FFmpeg(inputs=od([(infile, None)]),
                               outputs={outfile: "-an -map 0:v -vf scale=640:360:force_original_aspect_ratio=decrease -b:v 900k -codec:v libvpx -auto-alt-ref 0"})
            ff.run()
        self.todo['webm'] = []
    def generate_oggs(self):
        print('Generating oggs')
        for node in self.todo['ogg']:
            node = node.split('.')[0]
            infile = os.path.join(ORIG, self.orig[node])
            outfile = os.path.join(COMPUTED, '{}.ogg'.format(node))
            ff = ffmpy3.FFmpeg(inputs={infile: None},
                               outputs={outfile: "-ar 44100"})
            ff.run()
        self.todo['ogg'] = []
    def generate_m4as(self):
        print('Generating m4as')
        for node in self.todo['m4a']:
            node = node.split('.')[0]
            infile = os.path.join(ORIG, self.orig[node])
            outfile = os.path.join(COMPUTED, '{}.m4a'.format(node))
            ff = ffmpy3.FFmpeg(inputs={infile: None},
                               outputs={outfile: "-ar 44100"})
            ff.run()
        self.todo['m4a'] = []
    def generate_pair_webms(self):
        print('Generating pair_webms')
        for leftright in self.todo['pair_webm']:
            left, right = leftright.split('.')[0].split('-')
            lfilm = os.path.join(ORIG, self.orig[left])
            rfilm = os.path.join(ORIG, self.orig[right])
            outfile = os.path.join(COMPUTED, leftright)
            ff = ffmpy3.FFmpeg(inputs=od([(lfilm, None), (rfilm, None)]),
                               outputs={outfile: "-an -s 1280x360 -filter_complex {} -b:v 900k -codec:v libvpx -auto-alt-ref 0".format(FILTER)})
            ff.run()
        self.todo['pair_webm'] = []
    def generate_pair_mp4s(self):
        print('Generating pair_mp4s')
        for leftright in self.todo['pair_mp4']:
            left, right = leftright.split('.')[0].split('-')
            lfilm = os.path.join(ORIG, self.orig[left])
            rfilm = os.path.join(ORIG, self.orig[right])
            outfile = os.path.join(COMPUTED, leftright)
            ff = ffmpy3.FFmpeg(inputs=od([(lfilm, None), (rfilm, None)]),
                               outputs={outfile: "-an -s 1280x360 -filter_complex {} -b:v 900k -movflags faststart".format(FILTER)})
            ff.run()
        self.todo['pair_mp4'] = []
    def generate_all(self):
        self.generate_oggs()
        self.generate_m4as()
        self.generate_mp4s()
        #self.generate_pair_mp4s()
        self.generate_webms()
        #self.generate_pair_webms()
        self.generate_gifs()
        self.generate_previews()
        



for l in (LA_RALLONGE, LA_RALLONGE_DANSEE):
    thread = Thread(l)
    print(thread.todo)
    thread.generate_all()
    print(thread.todo)

print("Resizing profile pics...")
origpath = os.path.join(ORIG, 'pics')
destpath = os.path.join(COMPUTED, 'pics')
for img in os.listdir(origpath):
    if not os.path.isfile(os.path.join(destpath, img)):
        subprocess.check_call(['convert', os.path.join(origpath, img), '-resize', '300', os.path.join(destpath, img)])
        subprocess.check_call(['convert', os.path.join(origpath, img), '-resize', '150', os.path.join(destpath, '150-' + img)])

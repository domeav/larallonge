#!/usr/bin/env python

import os
import subprocess

CDR_QUALITY = '23'

montage1 = [('film', 1), 
            ('film', 4), 
            ('film', 2), 
            ('film', 6), 
            ('film', 5), 
            ('film', 9),
            ('film', 8),
            ('film', 12),
            ('film', 10),
            ('film', 13),
            ('film', 16),
            ('dance', 2),
            ('film', 14),
            ('film', 17),
            ('film', 19),
            ('film', 18),  
            ('film', 21), 
            ('film', 20)]

montage2 = [('film', 14),
            ('film', 17),
            ('film', 19),
            ('film', 21), 
            ('film', 18),  
            ('film', 20), 
            ('film', 5),
            ('film', 16),
            ('film', 8),
            ('film', 13),
            ('film', 9),
            ('film', 1), 
            ('film', 12),
            ('film', 4), 
            ('film', 10),
            ('film', 2), 
            ('film', 6), 
            ('dance', 2)]

assert(len(montage1) == len(montage2))


# intro/outtro films
FILTER = '''[0:v]trim=duration=10,fade=t=in:st=2:d=2,fade=t=out:st=8:d=1[v0]; [v0]format=yuv422p[v]'''
for part in ['intro-1', 'intro-2', 'outtro-1', 'outtro-2']:
    outfile = 'computed/{}.ts'.format(part)
    if os.path.exists(outfile):
        print '{} exists'.format(outfile)
        continue
    subprocess.check_call(
        ['ffmpeg', '-loop', '1', '-i', 'screens/{}.png'.format(part), 
         '-filter_complex', FILTER, '-map', "[v]",
         '-pix_fmt', 'yuv422p', '-movflags', '+faststart', '-r', '25', '-vbsf', 'h264_mp4toannexb', '-tune', 'stillimage',
         '-c:v',  'libx264', '-crf', CDR_QUALITY, outfile])


# announcements films
FILTER = '''[0:v]trim=duration=13,fade=t=in:st=3:d=0.5,fade=t=out:st=12:d=1[v0]; [v0]format=yuv422p[v]'''
for part in montage1:
    outfile = 'computed/{}-{}-announcement.ts'.format(*part)
    if os.path.exists(outfile):
        print '{} exists'.format(outfile)
        continue
    subprocess.check_call(
        ['ffmpeg', '-loop', '1', '-i', 'screens/{}-{}.png'.format(*part), 
         '-filter_complex', FILTER, '-map', "[v]",
         '-pix_fmt', 'yuv422p', '-movflags', '+faststart', '-r', '25', '-vbsf', 'h264_mp4toannexb', '-tune', 'stillimage',
         '-c:v',  'libx264', '-crf', CDR_QUALITY, outfile])


# videos
FILTER = '''"trim=duration=180, setpts=PTS-STARTPTS"'''

print "Converting to mp4..."
def tomp4(part, outfile):
    if os.path.exists(outfile):
        print '{} exists'.format(outfile)
        return
    command = ' '.join(['ffmpeg', '-i', '../orig/{}_{:04}.*'.format(*part)] + \
              ['-filter_complex', FILTER,
               '-codec:v', 'libx264', '-r', '25',
               '-crf', CDR_QUALITY, '-pix_fmt', 'yuv422p', '-movflags', '+faststart', '-tune', 'film',
               '-an', '-s', '1920x1080', '-vbsf', 'h264_mp4toannexb',
               '-y', outfile])
    subprocess.check_call(command, shell=True)
    print "{} generated".format(outfile)

for part in montage1:
    outfile = 'computed/{}-{}.ts'.format(*part)
    tomp4(part, outfile)



# see https://gist.github.com/abeluck/3757344

def files_to_concat(montage):
    out = []
    for film in montage:
        out.append('computed/{}-{}-announcement.ts'.format(*film))
        out.append('computed/{}-{}.ts'.format(*film))
    return out

for i in [1, 2]:
    montage = eval('montage{}'.format(i))
    outfile = 'computed/all{}.ts'.format(i)
    if os.path.exists(outfile):
        print '{} exists'.format(outfile)
    else:
        os.system('cat computed/intro-1.ts computed/intro-2.ts ' + ' '.join(files_to_concat(montage)) + ' computed/outtro-1.ts computed/outtro-2.ts > {}'.format(outfile))
    outfile = 'computed/montage{}.mp4'.format(i)
    if os.path.exists(outfile):
        print '{} exists'.format(outfile)
    else:
        subprocess.check_call(['ffmpeg', '-y', '-i', 'computed/all{}.ts'.format(i), 
                               '-vcodec', 'copy', 
                               '-pix_fmt', 'yuv422p', '-movflags', '+faststart',
                               '-absf', 'aac_adtstoasc', outfile])

print "done!\n"

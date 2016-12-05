__author__ = 'thiagocastroferreira'

from sys import path
path.append('/home/tcastrof/amr/Grammar')
import os
import main.utils as utils

def run():
    dirs = ['../data/LDC2015E86/data/amrs/split/training',
            '../data/LDC2015E86/data/amrs/split/dev',
            '../data/LDC2016E25/data/amrs/split/training',
            '../data/LDC2016E25/data/amrs/split/dev',
            '../data/LDC2016E33/data/amrs']

    texts = []
    for dir in dirs:
        for fname in os.listdir(dir):
            print fname, '\r',
            amrs = utils.parse_corpus(os.path.join(dir, fname))

            for amr in amrs:
                texts.append(amr['sentence'])

    f = open('text_for_lm')
    f.write('\n'.join(texts))
    f.close()

if __name__ == '__main__':
    run()
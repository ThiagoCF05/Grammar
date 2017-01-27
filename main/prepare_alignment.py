from sys import path
path.append('../')

from main.grammars.ERG import AMR
import os

import utils

def prepare():
    dirs = ['data/LDC2016E25/data/amrs/unsplit',
            'data/LDC2016E33/data/amrs',
            'data/prince/train']

    amrs = []
    for dir in dirs:
        for file in os.listdir(dir):
            if 'prince' in dir:
                amrs.extend(utils.parse_corpus(os.path.join(dir, file), True))
            else:
                amrs.extend(utils.parse_corpus(os.path.join(dir, file), False))

    feng = open('ENG.txt', 'w')
    famr = open('AMR.txt', 'w')
    for amr in amrs:
        _amr = amr['amr'].replace('\t', '').replace('\n', '').replace('\r', '')
        famr.write(_amr)
        famr.write('\n')

        feng.write(amr['sentence'])
        feng.write('\n')
    feng.close()
    famr.close()

def write(fnread, fnwrite):
    f = open(fnread)
    doc = f.read()
    doc = doc.split('\n\n')[:-1]
    f.close()

    fwrite = open(fnwrite, 'w')
    fwrite.write('# AMR release; corpus: lpp; section: training; number of AMRs: 1274 \n\n')
    for row in doc:
        snt, amr = row.split('\n')
        snt = map(lambda w: w.split('_')[0], snt.split())
        snt.insert(1, '::snt')
        snt = ' '.join(snt)

        graph = AMR(nodes={}, edges={}, root=1)
        graph.parse(amr)
        amr = graph.prettify(print_constants=True)

        fwrite.write('#')
        fwrite.write('\n')
        fwrite.write(snt)
        fwrite.write('\n')
        fwrite.write('#')
        fwrite.write('\n')
        fwrite.write('#')
        fwrite.write('\n')
        fwrite.write(amr)
        fwrite.write('\n')
        fwrite.write('\n')
    fwrite.close()

if __name__ == '__main__':
    fnread = '/home/tcastrof/amr/Aligner/AMR_Aligned.keep'
    fwrite = 'data/TEST/train/training.txt'

    write(fnread=fnread, fnwrite=fwrite)
__author__ = 'thiagocastroferreira'

from Aligner import Aligner
from stanford_corenlp_pywrapper import CoreNLP

import os
import utils

def run(fname, aligner):
    def get_alignments(dir):
        alignments = []

        files = os.listdir(dir)
        files = filter(lambda x: x != '.DS_Store', files)
        for file in files[:1]:
            amrs = utils.parse_aligned_corpus(os.path.join(dir, file))
            for amr in amrs:
                text_alignments = aligner.train(amr['amr'], amr['sentence'])
                prepared_alignment = {'subgraphs':[], 'tokens':[], 'text':amr['sentence']}
                for alignment in text_alignments:
                    string = map(lambda x: '/'.join(x), alignment['edges'])
                    subgraph = '~'.join(string)
                    tokens = ','.join(map(lambda x: str(x), alignment['tokens']))

                    prepared_alignment['subgraphs'].append(subgraph)
                    prepared_alignment['tokens'].append(tokens)

                alignments.append(prepared_alignment)
        return alignments

    training_dir = os.path.join(fname, 'training')
    train_set = get_alignments(training_dir)

    dev_dir = os.path.join(fname, 'dev')
    dev_set = get_alignments(dev_dir)

    test_dir = os.path.join(fname, 'test')
    test_set = get_alignments(test_dir)

    return train_set, dev_set, test_set

def write(fname, _set):
    f_sub = open(fname+'_sub', 'w')
    f_text = open(fname+'_text', 'w')
    f_gold = open(fname+'_gold', 'w')

    for row in _set:
        f_sub.write(' '.join(row['subgraphs']))
        f_sub.write('\n')

        f_text.write(row['text'])
        f_text.write('\n')

        for i, token in enumerate(row['tokens']):
            if token == '':
                row['tokens'][i] = '-'
        
        f_gold.write(' '.join(row['tokens']))
        f_gold.write('\n')

    f_sub.close()
    f_text.close()
    f_gold.close()

if __name__ == '__main__':
    proc = CoreNLP("coref")
    verb2noun, noun2verb, verb2actor, actor2verb = utils.noun_verb('data/morph-verbalization-v1.01.txt')
    sub2word = utils.subgraph_word('data/verbalization-list-v1.06.txt')
    aligner = Aligner(verb2noun, noun2verb, verb2actor, actor2verb, sub2word, proc)

    corpora = ['LDC2015E86', 'LDC2016E25']
    dir = 'data/CORPORA/data/alignments/split'

    train_set, dev_set, test_set = [], [], []
    for corpus in corpora:
        train, dev, test = run(dir.replace('CORPORA', corpus), aligner)

        train_set.extend(train)
        dev_set.extend(dev)
        test_set.extend(test)

    write('training', train_set)
    write('dev', dev_set)
    write('test', test_set)
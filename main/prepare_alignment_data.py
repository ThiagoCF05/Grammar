__author__ = 'thiagocastroferreira'

from Aligner import Aligner

from sys import path
path.append('/home/tcastrof/amr/scp_repo')
from stanford_corenlp_pywrapper import CoreNLP

import json
import os
import utils

# table with the frequency of the alignments
def create_table(fname, aligner):
    table = {}

    training = os.path.join(fname, 'training')

    files = filter(lambda x: x != '.DS_Store', os.listdir(training))
    for file in files:
        amrs = utils.parse_aligned_corpus(os.path.join(training, file))
        for amr in amrs:
            info = aligner.proc.parse_doc(amr['sentence'])
            info = info['sentences'][0]

            nodes, edges = aligner.parse(amr['amr'])
            for id, node in nodes.iteritems():
                concept = node['name']
                if concept not in table:
                    table[concept] = {}

                lemmas = map(lambda x: info['lemmas'][x].lower(), node['tokens'])
                if len(lemmas) == 0:
                    if 'NULL' not in table[concept]:
                        table[concept]['NULL'] = 1
                    else:
                        table[concept]['NULL'] = table[concept]['NULL']+ 1
                else:
                    for lemma in lemmas:
                        if lemma not in table[concept]:
                            table[concept][lemma] = 1
                        else:
                            table[concept][lemma] = table[concept][lemma] + 1

    json.dump(table, open('data/alignments/table.json', 'w'), sort_keys=True, indent=4, separators=(',', ': '))

def run(fname, aligner):
    def get_alignments(dir):
        alignments = []

        files = os.listdir(dir)
        files = filter(lambda x: x != '.DS_Store', files)
        for file in files:
            amrs = utils.parse_aligned_corpus(os.path.join(dir, file))
            for amr in amrs:
                print amr['id'], '\r',
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

def main():
    print 'Initializing...'
    proc = CoreNLP("coref")
    verb2noun, noun2verb, verb2actor, actor2verb = utils.noun_verb('data/morph-verbalization-v1.01.txt')
    sub2word = utils.subgraph_word('data/verbalization-list-v1.06.txt')
    aligner = Aligner(verb2noun, noun2verb, verb2actor, actor2verb, sub2word, proc)

    corpora = ['LDC2015E86', 'LDC2016E25']
    dir = 'data/LDC2016E25/data/alignments/split'

    print 'Processing...'
    train_set, dev_set, test_set = [], [], []

    train, dev, test = run(dir, aligner)

    train_set.extend(train)
    dev_set.extend(dev)
    test_set.extend(test)

    print 'Writing...'
    write('data/alignments/training', train_set)
    write('data/alignments/dev', dev_set)
    write('data/alignments/test', test_set)

if __name__ == '__main__':
    proc = CoreNLP("coref")
    verb2noun, noun2verb, verb2actor, actor2verb = utils.noun_verb('data/morph-verbalization-v1.01.txt')
    sub2word = utils.subgraph_word('data/verbalization-list-v1.06.txt')
    aligner = Aligner(verb2noun, noun2verb, verb2actor, actor2verb, sub2word, proc)

    dir = 'data/LDC2016E25/data/alignments/split'
    create_table(dir, aligner)
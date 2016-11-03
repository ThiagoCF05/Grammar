__author__ = 'thiagocastroferreira'

import operator
import os
import nltk
import utils

from Aligner import Aligner
from RuleInducer import RuleInducer

from sys import path
path.append('/home/tcastrof/amr/scp_repo')
from stanford_corenlp_pywrapper import CoreNLP

def write(fname, tag):
    rule_freq = sorted(map(lambda x: (x, len(tag[x])), tag.keys()), key=operator.itemgetter(1))
    rule_freq.reverse()

    f = open(fname, 'w')

    for item in rule_freq:
        rule, freq = item
        f.write(str(rule))
        f.write('\t')
        f.write(str(freq))
        f.write('\n')

        tree_freq = sorted(nltk.FreqDist(tag[rule]).items(), key=operator.itemgetter(1))
        tree_freq.reverse()

        for item2 in tree_freq:
            tree, freq = item2
            f.write(str(tree))
            f.write('\t')
            f.write(str(freq))
            f.write('\n')
        f.write('\n\n')
    f.close()

def evaluate(aligner):
    aligned_dir = 'data/LDC2016E25/data/alignments/unsplit'
    _dir = 'data/LDC2016E25/data/amrs/unsplit'

    tag, ltag = {}, {}

    for fname in filter(lambda  f: f != '.DS_Store', os.listdir(aligned_dir)):
        print fname, '\r',
        aligned_amrs = utils.parse_aligned_corpus(os.path.join(aligned_dir, fname))

        fname = fname.split('-')
        fname[4] = 'amrs'
        fname = '-'.join(fname)
        amrs = utils.parse_corpus(os.path.join(_dir, fname))

        for i, amr in enumerate(amrs):
            try:
                gold_alignments = aligner.train(aligned_amrs[i]['amr'], aligned_amrs[i]['sentence'])
                alignments, info = aligner.run(amr['amr'], amr['sentence'])

                print amr['sentence']
                for alignment in gold_alignments:
                    print alignment
                print '\n'
                for alignment in alignments:
                    print alignment
                print '\n'
                break
                # inducer = RuleInducer(amr['sentence'], amr['amr'], info['parse'], alignments)
                # id2subtrees, id2rule = inducer.run()
                # tag, ltag = inducer.prettify(id2subtrees, id2rule, tag, ltag)
            except:
                print 'ERROR', amr['file'], amr['id']
            break
    return tag, ltag

def main(aligner):
    dir = 'data/LDC2016E25/data/amrs/unsplit'

    tag, ltag = {}, {}

    for fname in os.listdir(dir):
        print fname, '\r',
        amrs = utils.parse_corpus(os.path.join(dir, fname))

        for amr in amrs:
            try:
                alignments, info = aligner.run(amr['amr'], amr['sentence'])
            except:
                print 'ALIGNER ERROR', amr['file'], amr['id']
                alignments, info = None, None

            if alignments != None:
                try:
                    inducer = RuleInducer(amr['sentence'], amr['amr'], info['parse'], alignments)
                    id2subtrees, id2rule = inducer.run()
                    tag, ltag = inducer.prettify(id2subtrees, id2rule, tag, ltag)
                except:
                    print 'INDUCER ERROR', amr['file'], amr['id']
    return tag, ltag


if __name__ == '__main__':
    proc = CoreNLP("coref")
    verb2noun, noun2verb, verb2actor, actor2verb = utils.noun_verb('data/morph-verbalization-v1.01.txt')
    sub2word = utils.subgraph_word('data/verbalization-list-v1.06.txt')

    aligner = Aligner(verb2noun, noun2verb, verb2actor, actor2verb, sub2word, proc)
    tag, ltag = main(aligner)

    write('tag.txt', tag)
    write('ltag.txt', ltag)

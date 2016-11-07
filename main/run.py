__author__ = 'thiagocastroferreira'

import json
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
        if freq > 1:
            f.write(str(rule).encode('utf-8'))
            f.write('\t')
            f.write(str(freq).encode('utf-8'))
            f.write('\n')

        tree_freq = sorted(nltk.FreqDist(tag[rule]).items(), key=operator.itemgetter(1))
        tree_freq.reverse()

        for item2 in tree_freq:
            tree, freq = item2
            if freq > 1:
                f.write(tree.encode('utf-8'))
                f.write('\t')
                f.write(str(freq).encode('utf-8'))
                f.write('\n')
        f.write('\n\n')
    f.close()

def accuracy(gold_align, pred_alig):
    ids = map(lambda x: x['ids'][0], gold_align)

    for _id in ids:
        gold = filter(lambda x: x['ids'][0] == _id, gold_align)[0]
        pred = filter(lambda x: x['ids'][0] == _id, pred_alig)[0]

        dem,num = 0, 0
        for token in gold['tokens']:
            dem += 1
            if token in pred['tokens']:
                num += 1
    return num, dem

def evaluate(aligner):
    aligned_dir = 'data/LDC2016E25/data/alignments/unsplit'
    _dir = 'data/LDC2016E25/data/amrs/unsplit'

    num, dem = 0, 0

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

                _num, _dem = accuracy(gold_alignments, alignments)
                num += _num
                dem += _dem
            except:
                print 'ERROR', amr['file'], amr['id']

    print 'ACCURACY: ', float(num)/dem

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
    freq_table = json.load(open('data/alignments/table.json'))
    verb2noun, noun2verb, verb2actor, actor2verb = utils.noun_verb('data/morph-verbalization-v1.01.txt')
    sub2word = utils.subgraph_word('data/verbalization-list-v1.06.txt')

    aligner = Aligner(verb2noun, noun2verb, verb2actor, actor2verb, sub2word, freq_table, proc)
    evaluate(aligner)
    # tag, ltag = main(aligner)
    #
    # write('tag.txt', tag)
    # write('ltag.txt', ltag)

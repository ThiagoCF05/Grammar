__author__ = 'thiagocastroferreira'

import json
import utils

from stanford_corenlp_pywrapper import CoreNLP
from Aligner import Aligner
from RuleInducer import RuleInducer

if __name__ == '__main__':
    proc = CoreNLP("coref")

    freq_table = json.load(open('data/alignments/table.json'))
    verb2noun, noun2verb, verb2actor, actor2verb = utils.noun_verb('data/morph-verbalization-v1.01.txt')
    sub2word = utils.subgraph_word('data/verbalization-list-v1.06.txt')

    aligner = Aligner(verb2noun, noun2verb, verb2actor, actor2verb, sub2word, freq_table, proc)
    text = 'The machine was adjusted by the girl .'

    amr = """(a / adjust-01
                      :ARG0 (g / girl)
                      :ARG1 (m / machine))"""

    alignments, info = aligner.run(amr, text)

    print info['parse']
    print '\n'

    for alignment in alignments:
        print alignment

    inducer = RuleInducer(text, amr, info, alignments)
    id2subtrees, id2rule, adjtrees = inducer.run()
    tag, ltag = inducer.prettify(id2subtrees, id2rule, adjtrees)

    print '\n'
    print {'tag':tag, 'ltag':ltag}

    for _id in id2subtrees:
        print id2subtrees[_id]
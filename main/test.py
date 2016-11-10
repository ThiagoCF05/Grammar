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
    text = 'I headed straight for the center of activities, but in actual fact traffic was being controlled as early as 4 o\'clock, and they had already started limiting the crowds entering the sports center.'
    amr = """(c / contrast-01
                      :ARG1 (h / head-02
                            :ARG0 (i / i)
                            :ARG1 (c6 / center
                                  :mod (a2 / activity-06))
                            :ARG1-of (s2 / straight-04))
                      :ARG2 (a / and
                            :op1 (c2 / control-01
                                  :ARG1 (t / traffic)
                                  :prep-in (f / fact
                                        :ARG1-of (a3 / actual-02))
                                  :time (d / date-entity :time "4:00"
                                        :mod (e / early)))
                            :op2 (s / start-01
                                  :ARG0 (t2 / they)
                                  :ARG1 (l2 / limit-01
                                        :ARG1 (c4 / crowd
                                              :ARG0-of (e2 / enter-01
                                                    :ARG1 (c5 / center
                                                          :mod (s3 / sport)))))
                                  :time (a4 / already))))"""

    alignments, info = aligner.run(amr, text)

    print info['parse']
    print '\n'

    for alignment in alignments:
        print alignment

    inducer = RuleInducer(text, amr, info['parse'], alignments)
    id2subtrees, id2rule, adjtrees = inducer.run()
    tag, ltag = inducer.prettify(id2subtrees, id2rule, adjtrees)

    print '\n'
    print {'tag':tag, 'ltag':ltag}
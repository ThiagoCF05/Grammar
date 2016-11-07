__author__ = 'thiagocastroferreira'

import json
import utils

from stanford_corenlp_pywrapper import CoreNLP
from Aligner import Aligner

if __name__ == '__main__':
    proc = CoreNLP("coref")

    freq_table = json.load(open('data/alignments/table.json'))
    verb2noun, noun2verb, verb2actor, actor2verb = utils.noun_verb('data/morph-verbalization-v1.01.txt')
    sub2word = utils.subgraph_word('data/verbalization-list-v1.06.txt')

    aligner = Aligner(verb2noun, noun2verb, verb2actor, actor2verb, sub2word, freq_table, proc)
    text = 'In addition , the breakdown in communication also brought a serious problem to the surface . In the past , Red Army regiments were able to maintain contact with central headquarters by relying on just one battered radio . On this occasion though , people had no way to deal with the communication failure .'
    amr = """(m / multi-sentence
                  :snt2 (p2 / possible-01~e.24
                        :ARG1 (m2 / maintain-01~e.26
                              :ARG0 (r / regiment~e.22
                                    :part-of (m3 / military :wiki "People's_Liberation_Army"
                                          :name (n / name :op1 "Red"~e.20 :op2 "Army"~e.21)))
                              :ARG1 (c3 / contact-01~e.27
                                    :ARG0 r
                                    :ARG1~e.28 (h / headquarters~e.30
                                          :mod (c4 / central~e.29)
                                          :part-of m3))
                              :manner~e.31 (r2 / rely-01~e.32
                                    :ARG0 r
                                    :ARG1~e.33 (r3 / radio~e.37
                                          :ARG1-of (b3 / batter-01~e.36)
                                          :quant (j / just~e.34 :op1 1~e.35))))
                        :time (p3 / past~e.18))
                  :snt1 (a2 / and~e.0,1
                        :op2 (b / bring-01~e.8
                              :ARG0 (b2 / break-down-12
                                    :ARG1 (c2 / communicate-01~e.6))
                              :ARG1 (p / problem~e.11
                                    :mod (s2 / serious~e.10))
                              :ARG2~e.12 (s / surface~e.14)
                              :mod (a / also~e.7)))
                  :snt3 (h3 / have-concession-91~e.42
                        :ARG1 (h2 / have-03~e.45 :polarity~e.46 -~e.46
                              :ARG0 (p4 / person~e.44)
                              :ARG1 (w / way~e.47
                                    :manner-of~e.47 (d / deal-01~e.49
                                          :ARG2~e.50 (f / fail-01~e.53
                                                :ARG0 (c5 / communicate-01~e.52))))
                              :time (t2 / thing~e.41
                                    :ARG1-of~e.41 (o / occasion-02~e.41)
                                    :mod (t / this~e.40)))))"""
    alignments, info = aligner.run(amr, text)

    for alignment in alignments:
        print alignment
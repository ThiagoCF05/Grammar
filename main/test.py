__author__ = 'thiagocastroferreira'

import json
import utils

from main.aligners.AMRAligner import AMRAligner
from main.aligners.TAGSynchAligner import TAGSynchAligner
from stanford_corenlp_pywrapper import CoreNLP
# from Aligner import Aligner
# from RuleInducer import RuleInducer

if __name__ == '__main__':
    proc = CoreNLP("coref")

    freq_table = json.load(open('data/alignments/table.json'))
    verb2noun, noun2verb, verb2actor, actor2verb = utils.noun_verb('data/morph-verbalization-v1.01.txt')
    sub2word = utils.subgraph_word('data/verbalization-list-v1.06.txt')

    # aligner = Aligner(verb2noun, noun2verb, verb2actor, actor2verb, sub2word, freq_table, proc)
    aligner = AMRAligner(verb2noun, noun2verb, verb2actor, actor2verb, sub2word, freq_table, proc)
    text = 'According to the international reports on January 11 , eBay announced that it will acquire online ticket website StubHub for 310 million US dollars in cash to further expand its influence on electronic commerce .'

    amr = """(s / say-01
              :ARG0 (r / report-01
                    :mod (i2 / international))
              :ARG1 (a / announce-01
                    :ARG0 (c / company :wiki "EBay"
                          :name (n / name :op1 "eBay"))
                    :ARG1 (a2 / acquire-01
                          :ARG0 c
                          :ARG1 (c2 / company :wiki "StubHub"
                                :name (n2 / name :op1 "StubHub")
                                :mod (w / website
                                      :purpose (t / ticket)
                                      :mod (o / online)))
                          :ARG3 (m / monetary-quantity :quant 310000000
                                :unit (d / dollar)
                                :mod (c3 / country :wiki "United_States"
                                      :name (n3 / name :op1 "US"))
                                :consist-of (c4 / cash))
                          :purpose (e / expand-01
                                :ARG0 c
                                :ARG1 (i / influence-01
                                      :ARG0 c
                                      :ARG1 (c5 / commerce
                                            :mod (e2 / electronic)))
                                :degree (f / further))))
              :time (d2 / date-entity :month 1 :day 11))"""

    text = 'The machine was adjusted by the girl .'

    amr = """(a / adjust-01
                      :ARG0 (g / girl)
                      :ARG1 (m / machine))"""

    alignments, info = aligner.run(amr, text)
    print info['parse']
    print '\n'

    # inducer = RuleInducer(text, amr, info, alignments)
    inducer = TAGSynchAligner(text=text, amr=amr, info=info, alignments=alignments)
    alignments = inducer.run()
    # id2subtrees, id2rule, adjtrees = inducer.run()

    for rule_id in alignments.erg_rules:
        graph = alignments.erg_rules[rule_id].graph
        print alignments.erg_rules[rule_id].name
        print alignments.erg_rules[rule_id].head
        print graph.prettify(root=graph.root, head=alignments.erg_rules[rule_id].head, print_constants=False)
        print '\n'

    print 'Tree\n' + (10 * '-')
    for rule_id in alignments.tag_rules:
        tree = alignments.tag_rules[rule_id].tree
        print alignments.tag_rules[rule_id].name
        print alignments.tag_rules[rule_id].head
        if '/E' in alignments.tag_rules[rule_id].name:
            print 'empty'
        else:
            print tree.prettify(tree.root)
        print '\n'

    print '\n'
    for rule_id in alignments.features:
        print alignments.features[rule_id].pos
        print alignments.features[rule_id].type
        print alignments.features[rule_id].voice
        print alignments.features[rule_id].tense
        print '\n'





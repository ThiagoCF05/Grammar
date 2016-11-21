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
    text = 'The boy wants to ride the red bicycle .'

    amr = """(w / want-01
                      :ARG0 (b2 / boy)
                      :ARG1 (r2 / ride-01
                            :ARG0 b2
                            :ARG1 (b / bicycle
                                  :mod (r / red))))"""

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





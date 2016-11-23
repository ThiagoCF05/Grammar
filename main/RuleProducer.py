__author__ = 'thiagocastroferreira'

from sys import path
path.append('/home/tcastrof/amr/scp_repo')
path.append('/home/tcastrof/amr/Grammar')
from main.aligners.AMRAligner import AMRAligner
from main.grammars.SynchG import SynchG, SynchRule
from main.aligners.TAGSynchAligner import TAGSynchAligner

import copy
import json
import os
import utils

from stanford_corenlp_pywrapper import CoreNLP

def write(grammar, fname):
    rules = []
    for rule in grammar:
        if '/E' in rule.name:
            tree = 'empty'
        else:
            tree = rule.tree.prettify(rule.tree.root)
        graph = rule.graph.prettify(rule.head, rule.graph.root, print_constants=False)

        aux = {
            'name':rule.name,
            'head':rule.head,
            'parent_rule':rule.parent_rule,
            'parent_head':rule.parent_head,
            'graph':graph,
            'graph_rules':rule.graph_rules,
            'tree':tree,
            'tree_rules':rule.tree_rules,
            'features':{
                'type': rule.features.type,
                'voice': rule.features.voice,
                'tense': rule.features.tense
            }
        }
        rules.append(aux)

    json.dump(rules, open(fname, 'w'), sort_keys=True, indent=4, separators=(',', ': '))

def main(aligner):
    dir = 'data/LDC2016E25/data/amrs/unsplit'

    grammar = SynchG(initial_rules=[], substitution_rules=[], adjoining_rules=[])

    processed, errors = 0, 0
    for fname in os.listdir(dir):
        print fname, '\r',
        amrs = utils.parse_corpus(os.path.join(dir, fname))

        for amr in amrs[:30]:
            processed = processed + 1
            try:
                alignments, info = aligner.run(amr['amr'], amr['sentence'])
            except:
                errors = errors + 1
                print 'ALIGNER ERROR', amr['file'], amr['id'], errors
                alignments, info = None, None
            try:
                if alignments != None:
                    # print amr['sentence']
                    # print amr['amr'], '\n\n'
                    inducer = TAGSynchAligner(text=amr['sentence'], amr=amr['amr'], info=info, alignments=alignments)
                    alignments = inducer.run()

                    for rule_id in alignments.erg_rules:
                        name = alignments.erg_rules[rule_id].name
                        head = alignments.erg_rules[rule_id].head

                        parent = alignments.erg_rules[rule_id].parent
                        if parent != '':
                            parent_rule = alignments.id2rule[parent]
                            parent_head = alignments.erg_rules[parent].head
                        else:
                            parent_rule, parent_head = '', ''

                        graph = alignments.erg_rules[rule_id].graph
                        _graph_rules = alignments.erg_rules[rule_id].rules
                        # fix rule names
                        graph_rules = {}
                        for node in _graph_rules:
                            graph_rules[graph.nodes[node].name] = copy.copy(_graph_rules[node])

                        tree = alignments.tag_rules[rule_id].tree
                        tree_rules = alignments.tag_rules[rule_id].rules
                        # TO DO fix rule names

                        features = alignments.features[rule_id]

                        # TO DO: check if the tree is well formed (leafs are terminals or rule nodes)
                        rule = SynchRule(name=name,
                                  head=head,
                                  parent_rule=parent_rule,
                                  parent_head=parent_head,
                                  graph=graph,
                                  graph_rules=graph_rules,
                                  tree=tree,
                                  tree_rules=tree_rules,
                                  features=features)

                        if rule.name == ':root/ROOT':
                            grammar.initial_rules.append(rule)
                        else:
                            grammar.substitution_rules.append(rule)

                        if rule_id in alignments.adjoining_rules:
                            for adjoining in alignments.adjoining_rules[rule_id]:
                                tree = adjoining.tree
                                tree_rules = adjoining.rules
                                rule = SynchRule(name=name,
                                                 head=head,
                                                 parent_rule=parent_rule,
                                                 parent_head=parent_head,
                                                 graph=graph,
                                                 graph_rules=graph_rules,
                                                 tree=tree,
                                                 tree_rules=tree_rules,
                                                 features=features)
                                grammar.adjoining_rules.append(rule)
            except:
                errors = errors +1
                print 'INDUCER ERROR', amr['file'], amr['id']
                print 'AMRs processed: ', processed
                print 'Errors: ', errors
                print 'Rate: ', str(round(float(errors)/processed, 4))
                print 20 * '-' + '\n\n'

    return grammar


if __name__ == '__main__':
    proc = CoreNLP("coref")
    freq_table = json.load(open('data/alignments/table.json'))
    verb2noun, noun2verb, verb2actor, actor2verb = utils.noun_verb('data/morph-verbalization-v1.01.txt')
    sub2word = utils.subgraph_word('data/verbalization-list-v1.06.txt')

    aligner = AMRAligner(verb2noun, noun2verb, verb2actor, actor2verb, sub2word, freq_table, proc)
    # evaluate(aligner)
    grammar = main(aligner)

    write(grammar.initial_rules, 'initial.txt')

    write(grammar.substitution_rules, 'substitution.txt')

    write(grammar.adjoining_rules, 'adjoining.txt')

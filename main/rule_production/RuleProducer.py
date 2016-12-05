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
import main.utils as utils

from stanford_corenlp_pywrapper import CoreNLP

def write(grammar, fname):
    rules = []
    errors = 0
    for rule in grammar:
        try:
            if '/E' in rule.name:
                tree = 'empty'
            else:
                tree = rule.tree.prettify(rule.tree.root)
            graph = rule.graph.prettify(rule.head, rule.graph.root, print_constants=False)

            verb, noun = {}, {}
            if rule.features != None:
                if rule.features.type == 'verb':
                    verb = {'tense': rule.features.tense, 'voice': rule.features.voice}
                elif rule.features.type == 'noun':
                    noun = {'form': rule.features.form, 'number': rule.features.number, 'inPP': rule.features.inPP}

            aux = {
                'name':rule.name,
                'head':rule.head,
                'parent_rule':rule.parent_rule,
                'parent_head':rule.parent_head,
                'graph':graph,
                'graph_rules':rule.graph_rules,
                'tree':tree,
                'tree_rules':rule.tree_rules,
                'noun_info': noun,
                'verb_info': verb,
                'tokens':rule.tokens
            }
            rules.append(aux)
        except:
            errors = errors + 1
            print 'Error: ', errors

    json.dump(rules, open(fname, 'w'), sort_keys=True, indent=4, separators=(',', ': '))

def check_validity(tree):
    isValid = True

    for node in tree.edges:
        if len(tree.edges[node]) == 0:
            if tree.nodes[node].type == 'nonterminal':
                isValid = False
                break

    return isValid

def main(aligner):
    dirs = ['../data/LDC2015E86/data/amrs/split/training',
            '../data/LDC2015E86/data/amrs/split/dev',
            '../data/LDC2016E25/data/amrs/split/training',
            '../data/LDC2016E25/data/amrs/split/dev',
            '../data/LDC2016E33/data/amrs']
    # dir = '../data/LDC2016E25/data/amrs/unsplit'

    grammar = SynchG(initial_rules=[], substitution_rules=[], adjoining_rules=[])

    processed, errors, rules_processed, invalid_rules = 0, 0, 0, 0
    for dir in dirs:
        for fname in os.listdir(dir):
            print fname, '\r',
            amrs = utils.parse_corpus(os.path.join(dir, fname))

            for amr in amrs:
                processed = processed + 1
                # try:
                alignments, info = aligner.run(amr['amr'], amr['sentence'])
                # except:
                #     errors = errors + 1
                #     print 'ALIGNER ERROR', amr['file'], amr['id'], errors
                #     alignments, info = None, None
                try:
                    if alignments != None:
                        # print amr['sentence']
                        # print amr['amr'], '\n\n'
                        inducer = TAGSynchAligner(text=amr['sentence'], amr=amr['amr'], info=info, alignments=alignments)
                        alignments = inducer.run()

                        for rule_id in alignments.erg_rules:
                            rules_processed = rules_processed + 1

                            name = alignments.erg_rules[rule_id].name
                            head = alignments.erg_rules[rule_id].head
                            tokens = alignments.erg_rules[rule_id].tokens

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

                            if check_validity(tree):
                                rule = SynchRule(name=name,
                                          head=head,
                                          parent=parent,
                                          parent_rule=parent_rule,
                                          parent_head=parent_head,
                                          graph=graph,
                                          graph_rules=graph_rules,
                                          tree=tree,
                                          tree_rules=tree_rules,
                                          features=features,
                                          tokens=tokens)

                                if ':root' in rule.name:
                                    grammar.initial_rules.append(rule)
                                else:
                                    grammar.substitution_rules.append(rule)

                                if rule_id in alignments.adjoining_rules:
                                    for adjoining in alignments.adjoining_rules[rule_id]:
                                        tree = adjoining.tree
                                        tree_rules = adjoining.rules
                                        rule = SynchRule(name=name,
                                                         head=head,
                                                         parent=parent,
                                                         parent_rule=parent_rule,
                                                         parent_head=parent_head,
                                                         graph=graph,
                                                         graph_rules=graph_rules,
                                                         tree=tree,
                                                         tree_rules=tree_rules,
                                                         features=features,
                                                         tokens=tokens)
                                        grammar.adjoining_rules.append(rule)
                            else:
                                invalid_rules = invalid_rules + 1

                    if (processed % 1000) == 0:
                        print 'AMRs processed: ', processed
                        print 'Errors: ', errors
                        print 'Rate: ', str(round(float(errors)/processed, 4))
                        print 10 * '-'
                        print 'Rules processed', rules_processed
                        print 'Invalid rules: ', invalid_rules
                        print 'Rate: ', str(round(float(invalid_rules)/rules_processed, 4))
                        print 20 * '-' + '\n\n'
                except:
                    errors = errors +1
                    print 'INDUCER ERROR', amr['file'], amr['id']
                    print 'AMRs processed: ', processed
                    print 'Errors: ', errors
                    print 'Rate: ', str(round(float(errors)/processed, 4))
                    print 10 * '-'
                    print 'Rules processed', rules_processed
                    print 'Invalid rules: ', invalid_rules
                    print 'Rate: ', str(round(float(invalid_rules)/rules_processed, 4))
                    print 20 * '-' + '\n\n'

    return grammar


if __name__ == '__main__':
    proc = CoreNLP("coref")
    freq_table = json.load(open('../data/alignments/table.json'))
    verb2noun, noun2verb, verb2actor, actor2verb = utils.noun_verb('../data/morph-verbalization-v1.01.txt')
    sub2word = utils.subgraph_word('../data/verbalization-list-v1.06.txt')

    aligner = AMRAligner(verb2noun, noun2verb, verb2actor, actor2verb, sub2word, freq_table, proc)
    # evaluate(aligner)
    grammar = main(aligner)

    write(grammar.initial_rules, '/home/tcastrof/amr/data/grammars/initial.json')

    write(grammar.substitution_rules, '/home/tcastrof/amr/data/grammars/substitution.json')

    write(grammar.adjoining_rules, '/home/tcastrof/amr/data/grammars/adjoining.json')

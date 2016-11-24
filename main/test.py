__author__ = 'thiagocastroferreira'

import copy
import json
import utils

from main.grammars.SynchG import SynchG, SynchRule
from main.aligners.AMRAligner import AMRAligner
from main.aligners.TAGSynchAligner import TAGSynchAligner
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
        except:
            errors = errors + 1
            print 'Error: ', errors

    json.dump(rules, open(fname, 'w'), sort_keys=True, indent=4, separators=(',', ': '))

def create_rule(alignments, rule_id):
    def check_validity(tree):
        isValid = True

        for node in tree.edges:
            if len(tree.edges[node]) == 0:
                if tree.nodes[node].type == 'nonterminal':
                    isValid = False
                    break

        return isValid

    initial_rules, substitution_rules, adjoining_rules = [], [], []

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

    features = alignments.features[rule_id]

    if check_validity(tree):
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
            initial_rules.append(rule)
        else:
            substitution_rules.append(rule)

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
                adjoining_rules.append(rule)
    return initial_rules, substitution_rules, adjoining_rules

if __name__ == '__main__':
    proc = CoreNLP("coref")

    freq_table = json.load(open('data/alignments/table.json'))
    verb2noun, noun2verb, verb2actor, actor2verb = utils.noun_verb('data/morph-verbalization-v1.01.txt')
    sub2word = utils.subgraph_word('data/verbalization-list-v1.06.txt')

    aligner = AMRAligner(verb2noun, noun2verb, verb2actor, actor2verb, sub2word, freq_table, proc)

    text = 'The London emergency services said that altogether eleven people had been sent to hospital for treatment due to minor wounds.'
    amr = """(s / say-01
                      :ARG0 (s2 / service
                            :mod (e / emergency)
                            :location (c / city :wiki 'London'
                                  :name (n / name :op1 'London')))
                      :ARG1 (s3 / send-01
                            :ARG1 (p / person :quant 11)
                            :ARG2 (h / hospital)
                            :mod (a / altogether)
                            :purpose (t / treat-03
                                  :ARG1 p
                                  :ARG2 (w / wound-01
                                        :ARG1 p
                                        :mod (m / minor)))))"""

    alignments, info = aligner.run(amr, text)
    print info['parse']
    print '\n'

    inducer = TAGSynchAligner(text=text, amr=amr, info=info, alignments=alignments)
    alignments = inducer.run()

    initial, substitution, adjoining = [], [], []
    for rule_id in alignments.erg_rules:
        _initial, _substitution, _adjoining = create_rule(alignments, rule_id)

        initial.extend(_initial)
        substitution.extend(_substitution)
        adjoining.extend(_adjoining)

    write(initial, 'initial.txt')

    write(substitution, 'substitution.txt')

    write(adjoining, 'adjoining.txt')

    # for rule_id in alignments.erg_rules:
    #     graph = alignments.erg_rules[rule_id].graph
    #     print alignments.erg_rules[rule_id].name
    #     print alignments.erg_rules[rule_id].head
    #     print graph.prettify(root=graph.root, head=alignments.erg_rules[rule_id].head, print_constants=False)
    #     print '\n'
    #
    # print 'Tree\n' + (10 * '-')
    # for rule_id in alignments.tag_rules:
    #     tree = alignments.tag_rules[rule_id].tree
    #     print alignments.tag_rules[rule_id].name
    #     print alignments.tag_rules[rule_id].head
    #     if '/E' in alignments.tag_rules[rule_id].name:
    #         print 'empty'
    #     else:
    #         print tree.prettify(tree.root)
    #     print '\n'
    #
    # print '\n'
    # for rule_id in alignments.features:
    #     print alignments.features[rule_id].pos
    #     print alignments.features[rule_id].type
    #     print alignments.features[rule_id].voice
    #     print alignments.features[rule_id].tense
    #     print '\n'





__author__ = 'thiagocastroferreira'

import cPickle as p
import json
import nltk
import os

class RuleProb(object):
    def __init__(self, initial='', substitution='', adjoining='', fwrite=''):
        self.initial = json.load(open(initial))
        self.run(self.initial, os.path.join(fwrite, 'initial'))

        self.substitution = json.load(open(substitution))
        self.run(self.substitution, os.path.join(fwrite, 'substitution'))

        self.adjoining = json.load(open(adjoining))
        self.run(self.adjoining, os.path.join(fwrite, 'adjoining'))

    def run(self, rules, fname):
        group_2, group_3, group_4, group_5 = [], [], [], []

        print fname
        for i, rule in enumerate(rules):
            print 'Rule: ', str(i+1), '\r',
            if len(rule['tree_rules']) == 0:
                g2 = (rule['tree'], rule['name'], 'empty')
                group_2.append(g2)

                g3 = (rule['tree'], rule['name'], 'empty', rule['head'])
                group_3.append(g3)

                g4 = (rule['tree'], rule['name'], 'empty', rule['head'], rule['parent_rule'])
                group_4.append(g4)

                g5 = (rule['tree'], rule['name'], 'empty', rule['head'], rule['parent_rule'], rule['parent_head'])
                group_5.append(g5)
            else:
                edges = rule['tree_rules']
                edges.sort()
                edges = tuple(edges)

                g2 = (rule['tree'], rule['name'], edges)
                group_2.append(g2)

                g3 = (rule['tree'], rule['name'], edges, rule['head'])
                group_3.append(g3)

                g4 = (rule['tree'], rule['name'], edges, rule['head'], rule['parent_rule'])
                group_4.append(g4)

                g5 = (rule['tree'], rule['name'], edges, rule['head'], rule['parent_rule'], rule['parent_head'])
                group_5.append(g5)
        print '\n'

        # 2 conditions
        freq_2 = dict(nltk.FreqDist(group_2))
        _fname = fname + '_rule_edges.pickle'
        p.dump(freq_2, open(_fname, 'w'))

        # 3 conditions
        freq_3 = dict(nltk.FreqDist(group_3))
        _fname = fname + '_rule_edges_head.pickle'
        p.dump(freq_3, open(_fname, 'w'))

        # 4 conditions
        freq_4 = dict(nltk.FreqDist(group_4))
        _fname = fname + '_rule_edges_head_prule.pickle'
        p.dump(freq_4, open(_fname, 'w'))

        # 5 conditions
        freq_5 = dict(nltk.FreqDist(group_5))
        _fname = fname + '_rule_edges_head_prule_phead.pickle'
        p.dump(freq_5, open(_fname, 'w'))

if __name__ == '__main__':
    RuleProb(initial='/home/tcastrof/amr/data/grammars/initial.json',
             substitution='/home/tcastrof/amr/data/grammars/substitution.json',
             adjoining='/home/tcastrof/amr/data/grammars/adjoining.json',
             fwrite='/home/tcastrof/amr/data/grammars')
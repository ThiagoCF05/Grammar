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
        num_2, num_3, num_4, num_5 = [], [], [], []
        dem_2, dem_3, dem_4, dem_5 = [], [], [], []

        print fname
        for i, rule in enumerate(rules):
            print 'Rule: ', str(i+1), '\r',
            if len(rule['tree_rules']) == 0:
                g2 = (rule['name'], 'empty', rule['tree'])
                num_2.append(g2)
                g2 = (rule['name'], 'empty')
                dem_2.append(g2)

                g3 = (rule['name'], 'empty', rule['head'], rule['tree'])
                num_3.append(g3)
                g3 = (rule['name'], 'empty', rule['head'])
                dem_3.append(g3)

                g4 = (rule['name'], 'empty', rule['head'], rule['parent_rule'], rule['tree'])
                num_4.append(g4)
                g4 = (rule['name'], 'empty', rule['head'], rule['parent_rule'])
                dem_4.append(g4)

                g5 = (rule['name'], 'empty', rule['head'], rule['parent_rule'], rule['parent_head'], rule['tree'])
                num_5.append(g5)
                g5 = (rule['name'], 'empty', rule['head'], rule['parent_rule'], rule['parent_head'])
                dem_5.append(g5)
            else:
                edges = rule['tree_rules']
                edges.sort()
                edges = tuple(edges)

                g2 = (rule['name'], edges, rule['tree'])
                num_2.append(g2)
                g2 = (rule['name'], edges)
                dem_2.append(g2)

                g3 = (rule['name'], edges, rule['head'], rule['tree'])
                num_3.append(g3)
                g3 = (rule['name'], edges, rule['head'])
                dem_3.append(g3)

                g4 = (rule['name'], edges, rule['head'], rule['parent_rule'], rule['tree'])
                num_4.append(g4)
                g4 = (rule['name'], edges, rule['head'], rule['parent_rule'])
                dem_4.append(g4)

                g5 = (rule['name'], edges, rule['head'], rule['parent_rule'], rule['parent_head'], rule['tree'])
                num_5.append(g5)
                g5 = (rule['name'], edges, rule['head'], rule['parent_rule'], rule['parent_head'])
                dem_5.append(g5)
        print '\n'

        # 2 conditions
        freq_num_2 = dict(nltk.FreqDist(num_2))
        _fname = fname + '_rule_edges_num.pickle'
        p.dump(freq_num_2, open(_fname, 'w'))

        freq_dem_2 = dict(nltk.FreqDist(dem_2))
        _fname = fname + '_rule_edges_dem.pickle'
        p.dump(freq_dem_2, open(_fname, 'w'))

        # 3 conditions
        freq_num_3 = dict(nltk.FreqDist(num_3))
        _fname = fname + '_rule_edges_head_num.pickle'
        p.dump(freq_num_3, open(_fname, 'w'))

        freq_dem_3 = dict(nltk.FreqDist(dem_3))
        _fname = fname + '_rule_edges_head_dem.pickle'
        p.dump(freq_dem_3, open(_fname, 'w'))

        # 4 conditions
        freq_num_4 = dict(nltk.FreqDist(num_4))
        _fname = fname + '_rule_edges_head_prule_num.pickle'
        p.dump(freq_num_4, open(_fname, 'w'))

        freq_dem_4 = dict(nltk.FreqDist(dem_4))
        _fname = fname + '_rule_edges_head_prule_dem.pickle'
        p.dump(freq_dem_4, open(_fname, 'w'))

        # 5 conditions
        freq_num_5 = dict(nltk.FreqDist(num_5))
        _fname = fname + '_rule_edges_head_prule_phead_num.pickle'
        p.dump(freq_num_5, open(_fname, 'w'))

        freq_dem_5 = dict(nltk.FreqDist(dem_5))
        _fname = fname + '_rule_edges_head_prule_phead_dem.pickle'
        p.dump(freq_dem_5, open(_fname, 'w'))

if __name__ == '__main__':
    RuleProb(initial='/home/tcastrof/amr/data/grammars/initial.json',
             substitution='/home/tcastrof/amr/data/grammars/substitution.json',
             adjoining='/home/tcastrof/amr/data/grammars/adjoining.json',
             fwrite='/home/tcastrof/amr/data/grammars')
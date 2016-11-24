__author__ = 'thiagocastroferreira'

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

        # 2 conditions
        freq_num_2 = dict(nltk.FreqDist(num_2))
        fname = fname + '_rule_edges_num.json'
        json.dump(freq_num_2, open(fname, 'w'), sort_keys=True, indent=4, separators=(',', ': '))

        freq_dem_2 = dict(nltk.FreqDist(dem_2))
        fname = fname + '_rule_edges_dem.json'
        json.dump(freq_dem_2, open(fname, 'w'), sort_keys=True, indent=4, separators=(',', ': '))

        # 3 conditions
        freq_num_3 = dict(nltk.FreqDist(num_3))
        fname = fname + '_rule_edges_head_num.json'
        json.dump(freq_num_3, open(fname, 'w'), sort_keys=True, indent=4, separators=(',', ': '))

        freq_dem_3 = dict(nltk.FreqDist(dem_3))
        fname = fname + '_rule_edges_head_dem.json'
        json.dump(freq_dem_3, open(fname, 'w'), sort_keys=True, indent=4, separators=(',', ': '))

        # 4 conditions
        freq_num_4 = dict(nltk.FreqDist(num_4))
        fname = fname + '_rule_edges_head_prule_num.json'
        json.dump(freq_num_4, open(fname, 'w'), sort_keys=True, indent=4, separators=(',', ': '))

        freq_dem_4 = dict(nltk.FreqDist(dem_4))
        fname = fname + '_rule_edges_head_prule_dem.json'
        json.dump(freq_dem_4, open(fname, 'w'), sort_keys=True, indent=4, separators=(',', ': '))

        # 5 conditions
        freq_num_5 = dict(nltk.FreqDist(num_5))
        fname = fname + '_rule_edges_head_prule_phead_num.json'
        json.dump(freq_num_5, open(fname, 'w'), sort_keys=True, indent=4, separators=(',', ': '))

        freq_dem_5 = dict(nltk.FreqDist(dem_5))
        fname = fname + '_rule_edges_head_prule_phead_dem.json'
        json.dump(freq_dem_5, open(fname, 'w'), sort_keys=True, indent=4, separators=(',', ': '))

if __name__ == '__main__':
    RuleProb(initial='../data/grammars/initial.json',
             substitution='../data/grammars/substitution.json',
             adjoining='../data/grammars/adjoining.json',
             fwrite='..data/grammars')
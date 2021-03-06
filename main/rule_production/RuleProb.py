__author__ = 'thiagocastroferreira'

from sys import path
path.append('../../')

import main.generator.properties as prop
import cPickle as p
import json
import nltk
import os

class RuleProb(object):
    def __init__(self, initial='', substitution='', adjoining='', lexicons='', rule_write='', lexicon_write=''):
        self.initial = json.load(open(initial))
        self.freq_rules(self.initial, os.path.join(rule_write, 'initial'))

        self.substitution = json.load(open(substitution))
        self.freq_rules(self.substitution, os.path.join(rule_write, 'substitution'))

        self.adjoining = json.load(open(adjoining))
        self.freq_rules(self.adjoining, os.path.join(rule_write, 'adjoining'))

        self.lexicons = json.load(open(lexicons))
        self.freq_lexicon(lexicon_write)

    def freq_lexicon(self, fdir):
        sw, shead, spos, sedge = [], [], [], []
        w, w_wtm1, w_head, w_pos, w_edge = {}, {}, {}, {}, {}

        # Group coutings by part-of-speech
        for lexicon in self.lexicons:
            sw.append(lexicon['w_t'])
            sw.append(lexicon['w_tm1'])
            shead.append(lexicon['head'])
            spos.append(lexicon['pos'])
            sedge.append(lexicon['edge'])

            pos = lexicon['pos']
            if pos not in w:
                w[pos] = []
            if pos not in w_wtm1:
                w_wtm1[pos] = []
            if pos not in w_head:
                w_head[pos] = []
            if pos not in w_pos:
                w_pos[pos] = []
            if pos not in w_edge:
                w_edge[pos] = []

            w[pos].append(lexicon['w_t'])
            w_wtm1[pos].append((lexicon['w_t'], lexicon['w_tm1']))
            w_head[pos].append((lexicon['w_t'], lexicon['head']))
            w_pos[pos].append((lexicon['w_t'], lexicon['pos']))
            w_edge[pos].append((lexicon['w_t'], lexicon['edge']))

        laplace = {
            'w': len(set(sw)),
            'head': len(set(shead)),
            'pos': len(set(spos)),
            'edge': len(set(sedge))
        }

        for pos in w:
            w[pos] = dict(nltk.FreqDist(w[pos]))
            w_wtm1[pos] = dict(nltk.FreqDist(w_wtm1[pos]))
            w_head[pos] = dict(nltk.FreqDist(w_head[pos]))
            w_pos[pos] = dict(nltk.FreqDist(w_pos[pos]))
            w_edge[pos] = dict(nltk.FreqDist(w_edge[pos]))

        p.dump(laplace, open(os.path.join(fdir, 'laplace.pickle'), 'w'))
        p.dump(w, open(os.path.join(fdir, 'w.pickle'), 'w'))
        p.dump(w_wtm1, open(os.path.join(fdir, 'w_wtm1.pickle'), 'w'))
        p.dump(w_head, open(os.path.join(fdir, 'w_head.pickle'), 'w'))
        p.dump(w_pos, open(os.path.join(fdir, 'w_pos.pickle'), 'w'))
        p.dump(w_edge, open(os.path.join(fdir, 'w_edge.pickle'), 'w'))

    def freq_rules(self, rules, fname):
        group_2, group_3, group_4, group_5 = [], [], [], []

        print fname
        for i, rule in enumerate(rules):
            if 'voice' in rule['verb_info']:
                template = (rule['tree'], rule['verb_info']['voice'])
            else:
                template = (rule['tree'], 'active')

            if len(rule['tree_rules']) == 0:
                g2 = (template, rule['name'], 'empty')
                group_2.append(g2)

                g3 = (template, rule['name'], 'empty', rule['head'])
                group_3.append(g3)
            else:
                edges = rule['tree_rules']
                edges.sort()
                edges = tuple(edges)

                g2 = (template, rule['name'], edges)
                group_2.append(g2)

                g3 = (template, rule['name'], edges, rule['head'])
                group_3.append(g3)

        # 2 conditions
        freq_2 = dict(nltk.FreqDist(group_2))
        _fname = fname + '_rule_edges.pickle'
        p.dump(freq_2, open(_fname, 'w'))

        # 3 conditions
        freq_3 = dict(nltk.FreqDist(group_3))
        _fname = fname + '_rule_edges_head.pickle'
        p.dump(freq_3, open(_fname, 'w'))

if __name__ == '__main__':
    # RuleProb(initial='/home/tcastrof/amr/data/grammars/initial.json',
    #          substitution='/home/tcastrof/amr/data/grammars/substitution.json',
    #          adjoining='/home/tcastrof/amr/data/grammars/adjoining.json',
    #          fwrite='/home/tcastrof/amr/data/grammars')
    initial = prop.initial_rules
    sub = prop.substitution_rules
    adj = prop.adjoining_rules
    lexicons = prop.lexicons
    rule_write = '../data/prince/rules'
    lexicon_write = '../data/prince/lexicon'


    RuleProb(initial=initial,
             substitution=sub,
             adjoining=adj,
             lexicons=lexicons,
             rule_write=rule_write,
             lexicon_write=lexicon_write)
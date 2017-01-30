__author__ = 'thiagocastroferreira'

import cPickle as p
import operator
import properties as prop

from main.grammars.TAG import Tree

import REG as reg

class Lexicalizer(object):
    def __init__(self):
        self.grammar = {'initial':{}, 'substitution':{}}
        self.grammar['initial']['rule_edges'] = p.load(open(prop.initial_rule_edges))
        self.grammar['initial']['rule_edges_head'] = p.load(open(prop.initial_rule_edges_head))
        self.grammar['substitution']['rule_edges'] = p.load(open(prop.substitution_rule_edges))
        self.grammar['substitution']['rule_edges_head'] = p.load(open(prop.substitution_rule_edges_head))

        # self.w = p.load(open(prop.lexicon_w))
        # self.w_edge = p.load(open(prop.lexicon_w_edge))
        # self.w_pos = p.load(open(prop.lexicon_w_pos))
        # self.w_head = p.load(open(prop.lexicon_w_head))
        # self.w_wtm1 = p.load(open(prop.lexicon_w_tm1))
        # self.laplace = p.load(open(prop.lexicon_laplace))

        self.w_head_pos = p.load(open(prop.lexicon_w_head_pos))

    def choose_words(self, subtree, rule):
        if '/name' in rule.head:
            name = reg.proper_name(rule)

            isInserted = False
            subtree = subtree.split()
            for i, token in enumerate(subtree):
                aux = token.split('-')
                if aux[0] == 'XXX' and len(aux) > 1:
                    if not isInserted:
                        subtree[i] = name
                        isInserted = True
                    else:
                        subtree[i] = ''
            subtree = ' '.join(subtree)
        elif 'date-entity' in rule.head:
            subtree = 'on ' + reg.date_entity(rule)
        else:
            subtree = subtree.split()

            for i, token in enumerate(subtree):
                aux = token.split('-')
                if aux[0] == 'XXX' and len(aux) > 1:
                    subtree[i] = self.select_lexicon(rule, aux[1])
            subtree = ' '.join(subtree)

        return subtree

    # TO DO: implement the function
    def select_lexicon(self, rule, pos):
        head = rule.head
        edge = rule.name.split('/')[0]

        w_head_pos = self.w_head_pos

        f = filter(lambda x: x[1] == head and x[2] == pos, self.w_head_pos)
        if len(f) > 0:
            candidates = set(map(lambda w: w[0], f))
            candidates = dict(map(lambda w: (w, 0.0), candidates))

            dem = sum(map(lambda x: w_head_pos[x], f))
            for candidate in candidates:
                g = filter(lambda w: w[0] == candidate[0], f)
                num = sum(map(lambda x: w_head_pos[x], g))

                candidates[candidate] = float(num) / dem
            P = sorted(candidates.items(), key=operator.itemgetter(1), reverse=True)
            result = P[0][0]
        else:
            head = rule.head.split('-')
            if len(head) == 1:
                result = head[0]
            else:
                result = ' '.join(head[:-1])

        return result
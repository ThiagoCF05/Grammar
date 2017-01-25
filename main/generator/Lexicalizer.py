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

        self.w = p.load(open(prop.lexicon_w))
        self.w_edge = p.load(open(prop.lexicon_w_edge))
        self.w_pos = p.load(open(prop.lexicon_w_pos))
        self.w_head = p.load(open(prop.lexicon_w_head))
        self.w_wtm1 = p.load(open(prop.lexicon_w_tm1))
        self.laplace = p.load(open(prop.lexicon_laplace))

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

        # w = self.w
        w_head = self.w_head
        w_pos = self.w_pos
        # w_edge = self.w_edge

        if ('-' in head or '/' in head) and pos != 'NN':
            # filter candidates
            candidates = dict(map(lambda w: (w[0], 0.0), filter(lambda x: x[1] == head, w_head)))

            if len(candidates) > 0:
                candidates = dict(map(lambda w: (w, 0.0), candidates))
                for candidate in candidates:
                    # P(w)
                    # dem = sum(w.values())
                    #
                    # f = filter(lambda x: x == candidate, w)
                    # num = sum(map(lambda x: w[x], f))
                    # prob = (num+1.0) / (dem+len(w.keys()))
                    ################################################
                    # P(w | pos)
                    f = filter(lambda x: x[0] == candidate, w_pos)
                    dem = sum(map(lambda x: w_pos[x], f))

                    f = filter(lambda x: x[1] == pos, w_pos)
                    num = sum(map(lambda x: w_pos[x], f))
                    posteriori = (num+1.0) / (dem+len(w_pos.keys()))
                    prob = posteriori
                    ################################################
                    # P(head | w, pos)
                    f = filter(lambda x: x[0] == candidate, w_head)
                    dem = sum(map(lambda x: w_head[x], f))

                    f = filter(lambda x: x[1] == head, f)
                    num = sum(map(lambda x: w_head[x], f))
                    posteriori = (num+1.0) / (dem+len(w_head.keys()))
                    prob = prob * posteriori
                    ################################################
                    # P(edge | w, pos)
                    # f = filter(lambda x: x[0] == candidate, w_edge)
                    # dem = sum(map(lambda x: w_edge[x], f))
                    #
                    # f = filter(lambda x: x[1] == edge, f)
                    # num = sum(map(lambda x: w_edge[x], f))
                    # posteriori = (num+1.0) / (dem+len(w_edge.keys()))
                    # prob = prob * posteriori
                    ################################################
                    candidates[candidate] = prob

                P = sorted(candidates.items(), key=operator.itemgetter(1), reverse=True)
                result = P[0][0]
            else:
                head = rule.head.split('-')
                if len(head) == 1:
                    result = head[0]
                else:
                    result = ' '.join(head[:-1])
        else:
            head = rule.head.split('-')
            if len(head) == 1:
                result = head[0]
            else:
                result = ' '.join(head[:-1])

        return result
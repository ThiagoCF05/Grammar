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

    def choose_words(self, subtree, rule_id, rule):
        if '/name' in rule.head:
            name = reg.proper_name(rule)
            size, pos = len(name.split()), 0

            remove_edges = []
            root = subtree.root
            if subtree.nodes[subtree.root].name != 'NP':
                for node in subtree.edges[subtree.root]:
                    if 'NP' in subtree.nodes[node].name:
                        root = node
                        break
                    else:
                        if subtree.nodes[node].type == 'terminal':
                            subtree.nodes[node].lexicon = self.select_functional_lexicon(rule, subtree.nodes[node].name)
                            # subtree.nodes[node].lexicon = subtree.nodes[node].name

            for i, node in enumerate(subtree.edges[root]):
                if pos == size:
                    break
                if subtree.nodes[node].type == 'terminal':
                    if subtree.nodes[node].name == 'NN':
                        if pos == 0:
                            subtree.nodes[node].lexicon = name
                        else:
                            remove_edges.append(i)
                        pos += 1
                    else:
                        remove_edges.append(i)

            for edge in remove_edges:
                node = subtree.edges[root][edge]
                del subtree.nodes[node]
                del subtree.edges[node]
                del subtree.edges[root][edge]
        elif 'date-entity' in rule.head:
            date = reg.date_entity(rule)
            tree = '(PP (IN on) (NP (NN ' + date + ')))'
            subtree = Tree(nodes={}, edges={}, root=1)
            subtree.parse(tree)
            for node in subtree.nodes:
                subtree.nodes[node].rule_id = rule_id
                if subtree.nodes[node].lexicon == date:
                    subtree.nodes[node].label = rule_id
        else:
            for node in subtree.nodes:
                if subtree.nodes[node].type == 'terminal':
                    if subtree.nodes[node].label == -1:
                        subtree.nodes[node].lexicon = self.select_functional_lexicon(rule, subtree.nodes[node].name)
                        # subtree.nodes[node].lexicon = subtree.nodes[node].name
                    else:
                        if rule.head == '-':
                            head = 'not'
                        else:
                            head = rule.head.split('-')
                            if len(head) == 1:
                                head = head[0]
                            else:
                                head = ' '.join(head[:-1])
                        subtree.nodes[node].lexicon = head
        return subtree

    # TO DO: implement the function
    def select_functional_lexicon(self, rule, pos):
        head = rule.head
        edge = rule.name.split('/')[0]

        w_head = self.w_head[pos]
        w_pos = self.w_pos[pos]
        w_edge = self.w_edge[pos]

        candidates = dict(map(lambda w: (w, 0.0), self.w[pos].keys()))
        for candidate in candidates:
            # P(w | pos)
            dem = sum(w_pos.values())

            f = filter(lambda x: x[1] == candidate, w_pos)
            num = sum(map(lambda x: w_pos[x], f))
            prob = (num+1.0) / (dem+len(w_pos.keys()))

            # P(head | w, pos)
            f = filter(lambda x: x[0] == candidate, w_head)
            dem = sum(map(lambda x: w_head[x], f))

            f = filter(lambda x: x[1] == head, f)
            num = sum(map(lambda x: w_head[x], f))
            posteriori = (num+1.0) / (dem+len(w_head.keys()))
            prob = prob * posteriori

            # P(edge | w, pos)
            f = filter(lambda x: x[0] == candidate, w_edge)
            dem = sum(map(lambda x: w_edge[x], f))

            f = filter(lambda x: x[1] == edge, f)
            num = sum(map(lambda x: w_edge[x], f))
            posteriori = (num+1.0) / (dem+len(w_edge.keys()))
            prob = prob * posteriori

            candidates[candidate] = prob

        P = sorted(candidates.items(), key=operator.itemgetter(1), reverse=True)
        return P[0][0]
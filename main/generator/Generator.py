__author__ = 'thiagocastroferreira'

from sys import path
path.append('/home/tcastrof/amr/scp_repo')
path.append('/home/tcastrof/amr/Grammar')

import copy
import cPickle as p
import operator
import re
import main.utils as utils

from main.grammars.ERG import AMR, AMRNode, AMREdge, ERG, ERGRule
from main.grammars.TAG import Tree

class Generator(object):
    def __init__(self, amr='', verb2noun={}, noun2verb={}, verb2actor={}, actor2verb={}, sub2word={}, models=[]):
        self.verb2noun = verb2noun
        self.noun2verb = noun2verb
        self.verb2actor = verb2actor
        self.actor2verb = actor2verb
        self.sub2word = sub2word

        self.amr = AMR(nodes={}, edges={}, root='')
        self.amr.parse(amr)

        self.grammar = {'initial':{}, 'substitution':{}, 'adjoining':{}}
        for fname in models:
            aux = fname.split('/')[-1].split('_')
            if aux[0] == 'initial':
                self.grammar['initial'][len(aux)-1] = p.load(open(fname))
            elif aux[0] == 'substitution':
                self.grammar['substitution'][len(aux)-1] = p.load(open(fname))
            else:
                self.grammar['adjoining'][len(aux)-1] = p.load(open(fname))

        # self.grammar = {'initial':{}, 'substitution':{}, 'adjoining':{}}
        # self.grammar['initial'] = p.load(open('../data/grammars/initial_rule_edges_head.pickle'))
        # self.grammar['substitution'] = p.load(open('../data/grammars/substitution_rule_edges_head.pickle'))
        # self.grammar['adjoining'] = p.load(open('../data/grammars/adjoining_rule_edges_head.pickle'))

        # Break the amr into subgraphs and create ERG
        self.create_erg()

        # Generation process from the root rule
        root_rule = filter(lambda rule_id: ':root' in self.erg.rules[rule_id].name, self.erg.rules)[0]
        self.generate(rule_id=root_rule,
                      graph_edge_parent={'node':0, 'edge':0},
                      graph=AMR(nodes={}, edges={}, root=1),
                      tree_node_parents=None,
                      trees=[],
                      tree_pos=[])

    # AMR operations
    def match_subgraph_patterns(self, root):
        # filter subgraphs with the root given as a parameter which the related word is in the sentence
        subgraphs = filter(lambda iter: iter[0] == self.amr.nodes[root].name, self.sub2word)

        if len(subgraphs) > 0:
            subgraphs = sorted(subgraphs, key=len)
            subgraphs.reverse()

            matched = True
            filtered_subgraph = [self.amr.nodes[root].name]
            tokens = []
            for sub in subgraphs:
                matched = True
                tokens = self.sub2word[sub]
                for edge in sub[1:]:
                    f = filter(lambda match_edge: match_edge.name == edge[0] and self.amr.nodes[match_edge.node_id].name == edge[1], self.amr.edges[root])
                    if len(f) > 0:
                        filtered_subgraph.append(f[0])
                    else:
                        matched = False
                        filtered_subgraph = [self.amr.nodes[root].name]
                        break
                if matched:
                    break

            if matched:
                return filtered_subgraph, tokens
        return None, []

    def create_rule(self, root, rule=None):
        self.amr.nodes[root].status = 'labeled'

        if rule == None:
            rule = ERGRule(name=self.amr.nodes[root].parent['edge'],
                           head=self.amr.nodes[root].name,
                           graph=AMR(nodes={}, edges={}, root=root),
                           tokens=[],
                           lemmas=[],
                           parent='',
                           rules={})

        node = self.amr.nodes[root]
        rule.graph.nodes[root] = AMRNode(id=node.id, name=node.name, parent=node.parent, status=node.status, tokens=node.tokens)

        rule.graph.edges[root] = []
        for edge in self.amr.edges[root]:
            rule.graph.edges[root].append(AMREdge(name=edge.name, node_id=edge.node_id, isRule=True))

            if root not in rule.rules:
                rule.rules[root] = []
            rule.rules[root].append(edge.name)

        return rule

    def create_subgraph_rule(self, root, edges, tokens):
        rule = self.create_rule(root)
        rule.tokens = tokens

        for edge in edges:
            if self.amr.nodes[edge.node_id].status == 'unlabeled':
                rule = self.create_rule(edge.node_id, rule)

                for _edge in rule.graph.edges[root]:
                    if _edge.name == edge.name:
                        rule.rules[root].remove(_edge.name)
                        _edge.isRule = False
                        break

        if root in rule.rules and len(rule.rules[root]) == 0:
            del rule.rules[root]

        return rule

    def create_father(self, root, edge):
        self.amr.nodes[root].status = 'labeled'

        for rule_id in self.erg.rules:
            rule = self.erg.rules[rule_id]

            if rule.graph.root == edge.node_id:
                rule.name = self.amr.nodes[root].parent['edge']
                rule.head = self.amr.nodes[root].name
                rule.graph.root = root

                rule.graph.nodes[root] = copy.copy(self.amr.nodes[root])

                rule.graph.edges[root] = []
                for _edge in self.amr.edges[root]:
                    if _edge.name == edge.name:
                        rule.graph.edges[root].append(AMREdge(name=_edge.name, node_id=_edge.node_id, isRule=False))
                    else:
                        rule.graph.edges[root].append(AMREdge(name=_edge.name, node_id=_edge.node_id, isRule=True))
                        if root not in rule.rules:
                            rule.rules[root] = []
                        rule.rules[root].append(_edge.name)
                break

    def find_subgraphs(self, root, visited):
        visited.append(root)

        # Find entity and quantity nodes
        regex = re.compile("""(.+-entity)$|(.+-quantity)$""")

        if self.amr.nodes[root].status != 'labeled':
            # Find subgraph defined at verbalization-list, and have-org/rel
            subgraph, tokens = self.match_subgraph_patterns(root)
            if subgraph != None:
                # When there is no edges
                if len(subgraph) > 1:
                    rule = self.create_subgraph_rule(root, subgraph[1:], tokens)
                    self.erg.rules[self.erg.count] = rule
                    self.erg.count = self.erg.count + 1

        for i, edge in enumerate(self.amr.edges[root]):
            if edge.node_id not in visited:
                self.find_subgraphs(edge.node_id, visited)

            # MATCH parent of :degree non-matched
            if edge.name == ':degree' and len(self.amr.nodes[edge.node_id].tokens) == 0:
                rule = self.create_subgraph_rule(root, [edge])
                self.erg.rules[self.erg.count] = rule
                self.erg.count = self.erg.count + 1

            # MATCH parent of :name
            if edge.name == ':name':
                self.create_father(root, edge)

            # MATCH reification
            elif self.amr.nodes[edge.node_id].name in ['have-rel-role-91', 'have-org-role-91'] and self.amr.nodes[root].status != 'labeled' and len(self.amr.nodes[root].tokens) == 0:
                self.create_father(root, edge)

        # MATCH NAME NODES
        if self.amr.nodes[root].name == 'name':
            rule = self.create_subgraph_rule(root, self.amr.edges[root])
            self.erg.rules[self.erg.count] = rule
            self.erg.count = self.erg.count + 1
        # MATCH entity and quantity nodes
        elif regex.match(self.amr.nodes[root].name) != None:
            rule = self.create_subgraph_rule(root, self.amr.edges[root])
            self.erg.rules[self.erg.count] = rule
            self.erg.count = self.erg.count + 1
        # MATCH org and rel roles
        elif self.amr.nodes[root].name in ['have-rel-role-91', 'have-org-role-91']:
            edges = filter(lambda edge: edge.name == ':ARG2', self.amr.edges[root])
            rule = self.create_subgraph_rule(root, edges)
            self.erg.rules[self.erg.count] = rule
            self.erg.count = self.erg.count + 1

    def create_erg(self):
        self.erg = ERG(rules={}, start='')
        self.find_subgraphs(self.amr.root, [])

        # Create rule for the unlabeled nodes
        for node in self.amr.nodes:
            if self.amr.nodes[node].status != 'labeled':
                rule = self.create_rule(node)
                self.erg.rules[self.erg.count] = rule
                self.erg.count = self.erg.count + 1

        # Set parent rule names
        for rule_id in self.erg.rules:
            graph = self.erg.rules[rule_id].graph
            root = graph.root
            parent = graph.nodes[root].parent

            for _id in self.erg.rules:
                if parent['node'] in self.erg.rules[_id].graph.nodes:
                    self.erg.rules[rule_id].parent = _id
                    break

    def find_subtree(self, rule_id, tree_type, trees, beam_n):
        rule = self.erg.rules[rule_id]

        # Get rules with the same income edge and head
        grammar = filter(lambda g: rule.name == g[1].split('/')[0] and rule.head == g[3], self.grammar[tree_type][3])

        # Test outcome edges condition
        if len(rule.rules.keys()) == 0:
            grammar = filter(lambda g: g[2] == 'empty', grammar)
        else:
            for node in rule.rules:
                for edge_rule in rule.rules[node]:
                    _grammar = []
                    for g in grammar:
                        for edge in g[2]:
                            if edge_rule == edge.split('/')[0]:
                                _grammar.append(g)
                    grammar = _grammar

        dem = sum(map(lambda rule: self.grammar[tree_type][3][rule], grammar))
        candidates = map(lambda rule: (rule[0], float(self.grammar[tree_type][3][rule])/dem), grammar)

        new_trees = []
        if len(trees) == 0:
            new_trees = map(lambda candidate: (None, candidate[0], candidate[1]), candidates)
        else:
            for tree in trees:
                for candidate in candidates:
                    new_tree = (tree[0], candidate[0], tree[1] * candidate[1])
                    new_trees.append(new_tree)

        new_trees = sorted(new_trees, key=operator.itemgetter(2))
        new_trees.reverse()
        return new_trees[:beam_n]

    def generate(self, rule_id, graph_edge_parent, graph, tree_node_parents, trees, tree_pos):
        def find_leaf(root, rule, leaf):
            if rule in tree.nodes[root].name:
                leaf = root
            else:
                for edge in tree.edges[root]:
                    if leaf == '':
                        leaf = find_leaf(edge, rule, leaf)
                    else:
                        break
            return leaf

        def find_rule(node, edge):
            for _rule_id in self.erg.rules:
                _graph = self.erg.rules[_rule_id].graph
                root = _graph.root
                if _graph.nodes[root].parent['node'] == node and _graph.nodes[root].parent['edge'] == edge:
                    return _rule_id
            return -1

        root_trees = []

        # Choose initial graph
        if tree_node_parents == None:
            graph = copy.copy(self.erg.rules[rule_id].graph)

            # Choose initial tree and parse it
            candidates = self.find_subtree(rule_id, 'initial', [], 20)
            tree_pos = []
            for candidate in candidates:
                tree = Tree(nodes={}, edges={}, root=1)
                tree.parse(candidate[1])

                trees.append((tree, candidate[2]))
                root_trees.append(1)
                tree_node_parents.append(0)
                tree_pos.append(0)
        else:
            # Insert subgraph into the graph
            subgraph = copy.copy(self.erg.rules[rule_id].graph)
            subgraph.nodes[subgraph.root].parent = {'node':graph_edge_parent['node'], 'edge':graph_edge_parent['edge']}

            for node_id in subgraph.nodes:
                graph.nodes[node_id] = copy.copy(subgraph.nodes[node_id])
                graph.edges[node_id] = copy.copy(subgraph.edges[node_id])

            root = graph_edge_parent['node']
            for edge in graph.edges[root]:
                if edge.name == graph_edge_parent['edge']:
                    edge.isRule = False
                    edge.node_id = subgraph.root
                    break

            candidates = self.find_subtree(rule_id, 'substitution', trees, 20)
            trees = []
            for i, candidate in enumerate(candidates):
                # Insert subtree into the tree
                tree = candidate[0]
                tree_parent = tree_node_parents[i]
                pos = tree_pos[i]

                subtree = Tree(nodes={}, edges={}, root=1)
                subtree.parse(candidate[1])

                for node_id in subtree.nodes:
                    tree.nodes[pos+node_id] = copy.copy(subtree.nodes[node_id])
                    tree.edges[pos+node_id] = map(lambda x: x+pos, subtree.edges[node_id])

                root_tree = pos + 1
                root = tree.nodes[tree_parent].parent
                tree.nodes[root_tree].parent = root
                index = tree.edges[root].index(tree_parent)
                tree.edges[root][index] = root_tree

                del tree.nodes[tree_parent]
                del tree.edges[tree_parent]

                trees.append((tree, candidate[2]))
                root_trees.append(root_tree)
                tree_pos[i] = max(tree.nodes)

        for node_parent in self.erg.rules[rule_id].rules:
            for rule_edge in self.erg.rules[rule_id].rules[node_parent]:
                child_rule_id = find_rule(node_parent, rule_edge)

                graph_edge_parent = {'node':node_parent, 'edge':rule_edge}

                for i, tree in trees:
                    tree_node_parents[i] = find_leaf(root_trees[i], rule_edge, '')

                graph, trees = self.generate(child_rule_id, graph_edge_parent, graph, tree_node_parents, trees, tree_pos)

        return graph, trees

if __name__ == '__main__':
    models = ['../data/grammars/initial_rule_edges.pickle',
              '../data/grammars/initial_rule_edges_head.pickle',
              '../data/grammars/initial_rule_edges_head_prule.pickle',
              '../data/grammars/initial_rule_edges_head_prule_phead.pickle',
              '../data/grammars/substitution_rule_edges.pickle',
              '../data/grammars/substitution_rule_edges_head.pickle',
              '../data/grammars/substitution_rule_edges_head_prule.pickle',
              '../data/grammars/substitution_rule_edges_head_prule_phead.pickle',
              '../data/grammars/adjoining_rule_edges.pickle',
              '../data/grammars/adjoining_rule_edges_head.pickle',
              '../data/grammars/adjoining_rule_edges_head_prule.pickle',
              '../data/grammars/adjoining_rule_edges_head_prule_phead.pickle']
    verb2noun, noun2verb, verb2actor, actor2verb = utils.noun_verb('../data/morph-verbalization-v1.01.txt')
    sub2word = utils.subgraph_word('../data/verbalization-list-v1.06.txt')

    amr = """(p / love-01
                :ARG0 (b / boy)
                :ARG1 (g / girl))"""

    gen = Generator(amr=amr,
                    verb2noun=verb2noun,
                    noun2verb=noun2verb,
                    verb2actor=verb2actor,
                    actor2verb=actor2verb,
                    sub2word=sub2word,
                    models=models)
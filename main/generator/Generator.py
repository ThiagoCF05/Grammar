__author__ = 'thiagocastroferreira'

from sys import path
path.append('/home/tcastrof/amr/scp_repo')
path.append('/home/tcastrof/amr/Grammar')

import copy
import cPickle as p
import main.utils as utils
import operator

from main.grammars.ERG import ERGFactory
from main.grammars.TAG import Tree
from main.grammars.SynchG import SynchG, SynchRule

class Candidate(object):
    def __init__(self, graph=None, tree=None, prob=0.0, synchg=None, isComplete=False):
        self.tree = Tree(nodes={}, edges={}, root=1)
        self.tree.parse(tree)
        self.graph = graph

        self.isComplete = isComplete
        self.synchg = synchg
        self.prob = prob

    # Insert subtree into the tree and return the subtree with updated ids
    def update_tree(self, root, subtree, prob):
        pos = max(self.tree.nodes)

        aux = Tree(nodes={}, edges={}, root=pos+1)
        aux.parse(subtree)
        subtree = aux

        new_root = pos + 1
        updated_subtree = Tree(nodes={}, edges={}, root=new_root)
        if len(subtree.nodes) > 0:
            for node_id in subtree.nodes:
                self.tree.nodes[pos+node_id] = copy.copy(subtree.nodes[node_id])
                self.tree.nodes[pos+node_id].parent = self.tree.nodes[pos+node_id].parent + pos
                self.tree.edges[pos+node_id] = map(lambda x: x+pos, subtree.edges[node_id])

                updated_subtree.nodes[pos+node_id] = copy.copy(subtree.nodes[node_id])
                updated_subtree.nodes[pos+node_id].parent = updated_subtree.nodes[pos+node_id].parent + pos
                updated_subtree.edges[pos+node_id] = map(lambda x: x+pos, subtree.edges[node_id])

            parent = self.tree.nodes[root].parent
            self.tree.nodes[new_root].parent = parent
            index = self.tree.edges[parent].index(root)
            self.tree.edges[parent][index] = new_root
        else:
            parent = self.tree.nodes[root].parent
            index = self.tree.edges[parent].index(root)
            del self.tree.edges[parent][index]

        del self.tree.nodes[root]
        del self.tree.edges[root]

        self.prob = self.prob * prob
        return updated_subtree

    def update_graph(self, subgraph, parent):
        subgraph.nodes[subgraph.root].parent = parent

        for node_id in subgraph.nodes:
            self.graph.nodes[node_id] = copy.copy(subgraph.nodes[node_id])
            self.graph.edges[node_id] = copy.copy(subgraph.edges[node_id])

        root = parent['node']
        for edge in self.graph.edges[root]:
            if edge.name == parent['edge']:
                edge.isRule = False
                edge.node_id = subgraph.root
                break

class Generator(object):
    def __init__(self, amr='', verb2noun={}, noun2verb={}, verb2actor={}, actor2verb={}, sub2word={}, models=[], beam_n=20):
        self.verb2noun = verb2noun
        self.noun2verb = noun2verb
        self.verb2actor = verb2actor
        self.actor2verb = actor2verb
        self.sub2word = sub2word

        self.grammar = {'initial':{}, 'substitution':{}, 'adjoining':{}}
        for fname in models:
            aux = fname.split('/')[-1].split('_')
            if aux[0] == 'initial':
                self.grammar['initial'][len(aux)-1] = p.load(open(fname))
            elif aux[0] == 'substitution':
                self.grammar['substitution'][len(aux)-1] = p.load(open(fname))
            else:
                self.grammar['adjoining'][len(aux)-1] = p.load(open(fname))

        # Break the amr into subgraphs and create ERG
        erg = ERGFactory(amr=amr,
                              verb2noun=verb2noun,
                              noun2verb=noun2verb,
                              verb2actor=verb2actor,
                              actor2verb=actor2verb,
                              sub2word=sub2word).create_erg()
        self.init_synchg(erg)
        self.beam_n = beam_n

    def init_synchg(self, erg):
        self.synchg = SynchG(rules={}, start='', initial_rules=[], substitution_rules=[], adjoining_rules=[])
        self.synchg.count = erg.count

        for rule_id in erg.rules:
            synch_rule = SynchRule(name=erg.rules[rule_id].name,
                                   head=erg.rules[rule_id].head,
                                   parent=erg.rules[rule_id].parent,
                                   graph=erg.rules[rule_id].graph,
                                   graph_rules=erg.rules[rule_id].rules,
                                   tree=None,
                                   tree_rules=[],
                                   features=None)
            self.synchg.rules[rule_id] = synch_rule

    def find_subtree(self, rule_id, synchg, tree_type):
        def filter_grammar(condition_level):
            rule = synchg.rules[rule_id]
            if rule.parent == '':
                parent_rule = ''
                parent_head = ''
            else:
                parent = synchg.rules[rule.parent]
                parent_rule = parent.name
                parent_head = parent.head

            result = []

            if condition_level == 5:
                if tree_type == 'initial':
                    result = filter(lambda g: rule.name == g[1].split('/')[0]
                                              and rule.head == g[3]
                                              and parent_rule == g[4]
                                              and parent_head == g[5], self.grammar[tree_type][condition_level])
                else:
                    result = filter(lambda g: rule.name == g[1]
                                              and rule.head == g[3]
                                              and parent_rule == g[4]
                                              and parent_head == g[5], self.grammar[tree_type][condition_level])
            elif condition_level == 4:
                if tree_type == 'initial':
                    result = filter(lambda g: rule.name == g[1].split('/')[0]
                                              and rule.head == g[3]
                                              and parent_rule == g[4], self.grammar[tree_type][condition_level])
                else:
                    result = filter(lambda g: rule.name == g[1]
                                              and rule.head == g[3]
                                              and parent_rule == g[4], self.grammar[tree_type][condition_level])
            elif condition_level == 3:
                if tree_type == 'initial':
                    result = filter(lambda g: rule.name == g[1].split('/')[0]
                                              and rule.head == g[3], self.grammar[tree_type][condition_level])
                else:
                    result = filter(lambda g: rule.name == g[1]
                                              and rule.head == g[3], self.grammar[tree_type][condition_level])
            elif condition_level == 2:
                if tree_type == 'initial':
                    result = filter(lambda g: rule.name == g[1].split('/')[0], self.grammar[tree_type][condition_level])
                else:
                    result = filter(lambda g: rule.name == g[1], self.grammar[tree_type][condition_level])

            return result

        rule = synchg.rules[rule_id]
        condition_level = 3
        grammar = []
        while condition_level > 1 and len(grammar) == 0:
            # Get rules with the same income edge and head
            grammar = filter_grammar(condition_level)

            # Test outcome edges condition
            if len(rule.graph_rules.keys()) == 0:
                grammar = filter(lambda g: g[2] == 'empty', grammar)
            else:
                for node in rule.graph_rules:
                    for edge_rule in rule.graph_rules[node]:
                        fgramar = []
                        for g in grammar:
                            for edge in g[2]:
                                if edge_rule.name == edge.split('/')[0]:
                                    fgramar.append(g)
                        grammar = copy.copy(fgramar)
            if len(grammar) == 0:
                condition_level = condition_level - 1

        dem = sum(map(lambda x: self.grammar[tree_type][condition_level][x], grammar))
        candidates = map(lambda x: (x[0], float(self.grammar[tree_type][condition_level][x])/dem), grammar)
        return candidates

    def choose_initial(self, rule_id):
        graph = copy.copy(self.synchg.rules[rule_id].graph)

        # Choose initial trees
        candidates = self.find_subtree(rule_id, self.synchg, 'initial')
        candidates = sorted(candidates, key=operator.itemgetter(1), reverse=True)[:self.beam_n]

        initials = []
        for candidate in candidates:
            initial = Candidate(graph=graph, tree=candidate[0], prob=candidate[1], synchg=copy.deepcopy(self.synchg), isComplete=False)
            initial.synchg.rules[rule_id].name = initial.synchg.rules[rule_id].name + '/' + initial.tree.nodes[initial.tree.root].name

            initial.synchg.rules[rule_id].tree = Tree(nodes={}, edges={}, root=1)
            initial.synchg.rules[rule_id].tree.parse(candidate[0])

            initials.append(initial)

        return initials

    def choose_substitution(self, rule_id, candidates):
        def find_leaf(tree, root, rule_name, leaf):
            if rule_name in tree.nodes[root].name:
                leaf = root
            else:
                for edge in tree.edges[root]:
                    if leaf == -1:
                        leaf = find_leaf(tree, edge, rule_name, leaf)
                    else:
                        break
            return leaf

        substitutions = []
        for candidate in candidates:
            subgraph = copy.copy(candidate.synchg.rules[rule_id].graph)

            graph_root = candidate.synchg.rules[rule_id].graph.root
            graph_parent = candidate.synchg.rules[rule_id].graph.nodes[graph_root].parent
            candidate.update_graph(subgraph=subgraph, parent=graph_parent)

            parent_rule = candidate.synchg.rules[rule_id].parent
            tree_parent = candidate.synchg.rules[parent_rule].tree.root
            tree_root = find_leaf(candidate.tree, tree_parent, candidate.synchg.rules[rule_id].name, -1)
            if tree_root == -1:
                candidate.prob = candidate.prob * -1
            else:
                # Change the name of the rule, inserting TAG node
                candidate.synchg.rules[rule_id].name = candidate.tree.nodes[tree_root].name
                subtrees = self.find_subtree(rule_id, candidate.synchg, 'substitution')
                subtrees = sorted(subtrees, key=operator.itemgetter(1), reverse=True)[:self.beam_n]

                for subtree in subtrees:
                    substitution = copy.deepcopy(candidate)
                    updated_subtree = substitution.update_tree(root=tree_root,subtree=subtree[0], prob=subtree[1])
                    substitution.synchg.rules[rule_id].tree = updated_subtree
                    substitutions.append(substitution)

        return sorted(substitutions, key=lambda x: x.prob, reverse=True)[:self.beam_n]

    def generate(self, rule_id, candidates):
        if len(candidates) == 0:
            candidates = self.choose_initial(rule_id)
        else:
            candidates = self.choose_substitution(rule_id, candidates)

        for graph_node in self.synchg.rules[rule_id].graph_rules:
            for graph_edge in self.synchg.rules[rule_id].graph_rules[graph_node]:
                child_rule_id = graph_edge.node_id
                candidates = self.generate(child_rule_id, candidates)

        return candidates

    def run(self):
        # Generation process from the root rule
        start_rule = filter(lambda rule_id: ':root' in self.synchg.rules[rule_id].name, self.synchg.rules)[0]
        candidates = self.generate(start_rule, [])

        for candidate in candidates:
            print candidate.tree.prettify(candidate.tree.root)

if __name__ == '__main__':
    models = ['/Users/thiagocastroferreira/Documents/Doutorado/Third_Chapter/AMR/induced_grammars/initial_rule_edges.pickle',
              '/Users/thiagocastroferreira/Documents/Doutorado/Third_Chapter/AMR/induced_grammars/initial_rule_edges_head.pickle',
              '/Users/thiagocastroferreira/Documents/Doutorado/Third_Chapter/AMR/induced_grammars/initial_rule_edges_head_prule.pickle',
              '/Users/thiagocastroferreira/Documents/Doutorado/Third_Chapter/AMR/induced_grammars/initial_rule_edges_head_prule_phead.pickle',
              '/Users/thiagocastroferreira/Documents/Doutorado/Third_Chapter/AMR/induced_grammars/substitution_rule_edges.pickle',
              '/Users/thiagocastroferreira/Documents/Doutorado/Third_Chapter/AMR/induced_grammars/substitution_rule_edges_head.pickle',
              '/Users/thiagocastroferreira/Documents/Doutorado/Third_Chapter/AMR/induced_grammars/substitution_rule_edges_head_prule.pickle',
              '/Users/thiagocastroferreira/Documents/Doutorado/Third_Chapter/AMR/induced_grammars/substitution_rule_edges_head_prule_phead.pickle',
              '/Users/thiagocastroferreira/Documents/Doutorado/Third_Chapter/AMR/induced_grammars/adjoining_rule_edges.pickle',
              '/Users/thiagocastroferreira/Documents/Doutorado/Third_Chapter/AMR/induced_grammars/adjoining_rule_edges_head.pickle',
              '/Users/thiagocastroferreira/Documents/Doutorado/Third_Chapter/AMR/induced_grammars/adjoining_rule_edges_head_prule.pickle',
              '/Users/thiagocastroferreira/Documents/Doutorado/Third_Chapter/AMR/induced_grammars/adjoining_rule_edges_head_prule_phead.pickle']
    verb2noun, noun2verb, verb2actor, actor2verb = utils.noun_verb('../data/morph-verbalization-v1.01.txt')
    sub2word = utils.subgraph_word('../data/verbalization-list-v1.06.txt')

    amr = """(l / love-01
                :ARG0 (b / boy
                    :mod (s / smart))
                :ARG1 (p / country))"""

    amr = """(p / person
                      :name (n / name
                            :op1 \"Barack\"
                            :op2 \"Obama\"))"""

    gen = Generator(amr=amr,
                    verb2noun=verb2noun,
                    noun2verb=noun2verb,
                    verb2actor=verb2actor,
                    actor2verb=actor2verb,
                    sub2word=sub2word,
                    models=models, beam_n=20)

    candidates = gen.run()
__author__ = 'thiagocastroferreira'

from main.grammars.TAG import Tree

class SynchRule(object):
    def __init__(self, name='', head='', parent=-1, parent_rule='', parent_head='', graph=None, graph_rules={}, tree=None, tree_rules=[], tokens=[], features=None):
        self.name = name
        self.head = head

        self.parent = parent
        self.parent_rule = parent_rule
        self.parent_head = parent_head

        self.graph_rules = graph_rules
        self.tree_rules = tree_rules

        self.graph = graph
        self.tree = tree

        self.tokens = tokens
        self.features = features

    def update_tree(self, tree):
        self.tree = Tree(nodes={}, edges={}, root=1)
        self.tree.parse(tree)

        self.tree_rules = self.tree.get_nodes_by(type='rule', root=self.tree.root, nodes=[])

class SynchG(object):
    def __init__(self, rules={}, start='', initial_rules=[], substitution_rules=[], adjoining_rules=[], lexicons=[]):
        self.rules = rules
        self.start = start
        self.count = 0
        self.initial_rules = initial_rules
        self.substitution_rules = substitution_rules
        self.adjoining_rules = adjoining_rules
        self.lexicons = lexicons

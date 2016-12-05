__author__ = 'thiagocastroferreira'

class SynchRule(object):
    def __init__(self, name='', head='', parent=-1, graph=None, graph_rules={}, tree=None, tree_rules=[], tokens=[], features=None):
        self.name = name
        self.head = head

        self.parent = parent

        self.graph_rules = graph_rules
        self.tree_rules = tree_rules

        self.graph = graph
        self.tree = tree

        self.tokens = tokens
        self.features = features

class SynchG(object):
    def __init__(self, rules={}, start='', initial_rules=[], substitution_rules=[], adjoining_rules=[]):
        self.rules = rules
        self.start = start
        self.count = 0
        self.initial_rules = initial_rules
        self.substitution_rules = substitution_rules
        self.adjoining_rules = adjoining_rules

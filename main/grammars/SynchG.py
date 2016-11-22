__author__ = 'thiagocastroferreira'

class SynchRule(object):
    def __init__(self, name='', head='', parent_rule='', parent_head='', graph=None, graph_rules=[], tree=None, tree_rules=[], features=None):
        self.name = name
        self.head = head

        self.parent_rule = parent_rule
        self.parent_head = parent_head

        self.graph_rules = graph_rules
        self.tree_rules = tree_rules

        self.graph = graph
        self.tree = tree

        self.features = features

class SynchG(object):
    def __init__(self, initial_rules=[], substitution_rules=[], adjoining_rules=[]):
        self.initial_rules = initial_rules
        self.substitution_rules = substitution_rules
        self.adjoining_rules = adjoining_rules

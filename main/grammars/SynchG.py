__author__ = 'thiagocastroferreira'

from main.grammars.ERG import ERGRule
from main.grammars.TAG import TAGRule

class SynchRule(object):
    def __init__(self, name='', head='', erg_rule=None, tag_rule=None, features=None):
        self.name = name
        self.head = head
        self.erg_rule = erg_rule
        self.tag_rule = tag_rule
        self.features = features

class SynchG(object):
    def __init__(self, initial_rules={}, substitution_rules={}, adjoining_rules={}):
        self.initial_rules = initial_rules
        self.substitution_rules = substitution_rules
        self.adjoining_rules = adjoining_rules

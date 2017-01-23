__author__ = 'thiagocastroferreira'

class Alignments(object):
    def __init__(self, erg_rules={}, tag_rules={}, adjoining_rules={}, features={}, id2rule={}, lexicons={}):
        self.erg_rules = erg_rules
        self.tag_rules = tag_rules
        self.adjoining_rules = adjoining_rules
        self.features = features
        self.lexicons = lexicons
        self.id2rule = id2rule
        self.count = 0
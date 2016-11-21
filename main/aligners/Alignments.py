__author__ = 'thiagocastroferreira'

class Features(object):
    def __init__(self, type='', pos=[], tokens=[], lemmas=[], voice='', tense=''):
        self.type = type
        self.pos = pos
        self.tokens = tokens
        self.lemmas = lemmas
        self.voice = voice
        self.tense = tense

class Alignments(object):
    def __init__(self, erg_rules={}, tag_rules={}, adjoining_rules={}, features={}, id2rule={}):
        self.erg_rules = erg_rules
        self.tag_rules = tag_rules
        self.adjoining_rules = adjoining_rules
        self.features = features
        self.id2rule = id2rule
        self.count = 0
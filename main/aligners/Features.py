__author__ = 'thiagocastroferreira'

class Features(object):
    def __init__(self, type='', pos=[], tokens=[], lemmas=[]):
        self.type = type
        self.pos = pos
        self.tokens = tokens
        self.lemmas = lemmas

class VerbPhrase(Features):
    def __init__(self, type='', pos=[], tokens=[], lemmas=[], voice='', tense=''):
        Features.__init__(self, type=type, pos=pos, tokens=tokens, lemmas=lemmas)
        self.voice = voice
        self.tense = tense

class NounPhrase(Features):
    def __init__(self, type='', pos=[], tokens=[], lemmas=[], form='', number='', inPP=False):
        Features.__init__(self, type=type, pos=pos, tokens=tokens, lemmas=lemmas)
        self.form = form
        self.number = number
        # in prepositional phrase
        self.inPP = inPP

class Lexicon(object):
    def __init__(self, w_t, w_tm1, head, pos, edge, rule_id, index):
        self.rule_id = rule_id
        self.w_t = w_t
        self.w_tm1 = w_tm1
        self.head = head
        self.pos = pos
        self.edge = edge
        self.index= index
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
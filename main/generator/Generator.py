__author__ = 'thiagocastroferreira'

import cPickle as p

from main.grammars.ERG import AMR

class Generator(object):
    def __init__(self, fread='', files=[], amr=''):
        self.amr = AMR(nodes={}, edges={}, root='')
        self.amr.parse(amr)

        self.fread = fread
        self.grammar = {'initial':{}, 'substitution':{}, 'adjoining':{}}

        for fname in files:
            if 'initial' in fname:
                if 'num' in fname:
                    pass
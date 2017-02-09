__author__ = 'thiagocastroferreira'

from sys import path
path.append('/home/tcastrof/amr/scp_repo')
path.append('/home/tcastrof/amr/Grammar')
path.append('../../')

from main.grammars.ERG import ERGFactory

import json
import kenlm
import main.utils as utils
import itertools

class Linearizer(object):
    def __init__(self, lm_path, erg_factory):
        self.model = kenlm.Model(lm_path)
        self.erg_factory = erg_factory

    def process(self, amr):
        erg = self.erg_factory.create_erg(amr)
        start_rule = filter(lambda rule_id: ':root' in erg.rules[rule_id].name, erg.rules)[0]

        linear = self.linearize(start_rule, erg)
        return linear

    def ranking(self, base):
        candidates = []
        for candidate in itertools.permutations(base):
            snt = []
            for e in candidate:
                for span in e.split():
                    snt.extend(span.split('~'))

            snt = ' '.join(snt)
            score = self.model.score(snt)
            candidates.append((' '.join(candidate), score))

        return sorted(candidates, key=lambda x: x[1], reverse=True)

    def linearize(self, rule_id, erg):
        head = erg.rules[rule_id].name + '~' + erg.rules[rule_id].head
        linear = [head]

        if len(erg.rules[rule_id].rules) > 0:
            edges = reduce(lambda x, y: x+y, erg.rules[rule_id].rules.values())

            for edge in edges:
                _rule_id = edge.node_id

                linear.append(self.linearize(_rule_id, erg))

        rank = self.ranking(linear)
        return rank[0][0]

    def write(self, fname, linearizations):
        f = open(fname, 'w')
        for linear in linearizations:
            f.write(linear)
            f.write('\n')
        f.close()

if __name__ == '__main__':
    freq_table = json.load(open('../data/alignments/table.json'))
    verb2noun, noun2verb, verb2actor, actor2verb = utils.noun_verb('../data/morph-verbalization-v1.01.txt')
    sub2word = utils.subgraph_word('../data/verbalization-list-v1.06.txt')

    factory = ERGFactory(verb2noun=verb2noun,
                         noun2verb=noun2verb,
                         verb2actor=verb2actor,
                         actor2verb=actor2verb,
                         sub2word=sub2word)

    lm2 = Linearizer(erg_factory=factory, lm_path='/home/tcastrof/amr/data/prince/linearization/lm2.arpa')
    lm3 = Linearizer(erg_factory=factory, lm_path='/home/tcastrof/amr/data/prince/linearization/lm3.arpa')
    lm4 = Linearizer(erg_factory=factory, lm_path='/home/tcastrof/amr/data/prince/linearization/lm4.arpa')
    lm5 = Linearizer(erg_factory=factory, lm_path='/home/tcastrof/amr/data/prince/linearization/lm5.arpa')

    fdev = '../data/prince/dev.txt'

    amrs = utils.parse_corpus(fdev, True)

    linear2, linear3, linear4, linear5 = [], [], [], []
    for amr in amrs:
        try:
            l = reduce(lambda x,y: x+y, map(lambda x: x.split('~'), lm2.process(amr['amr'].lower()).split()))
            linear2.append(' '.join(l))

            l = reduce(lambda x,y: x+y, map(lambda x: x.split('~'), lm3.process(amr['amr'].lower()).split()))
            linear3.append(' '.join(l))

            l = reduce(lambda x,y: x+y, map(lambda x: x.split('~'), lm4.process(amr['amr'].lower()).split()))
            linear4.append(' '.join(l))

            l = reduce(lambda x,y: x+y, map(lambda x: x.split('~'), lm5.process(amr['amr'].lower()).split()))
            linear5.append(' '.join(l))
        except:
            linear2.append('-')
            linear3.append('-')
            linear4.append('-')
            linear5.append('-')

    lm2.write('/home/tcastrof/amr/data/prince/linearization/dev2.eval', linear2)
    lm3.write('/home/tcastrof/amr/data/prince/linearization/dev3.eval', linear3)
    lm4.write('/home/tcastrof/amr/data/prince/linearization/dev4.eval', linear4)
    lm5.write('/home/tcastrof/amr/data/prince/linearization/dev5.eval', linear5)

    ################################################################################################################
    ftest = '../data/prince/test.txt'

    amrs = utils.parse_corpus(ftest, True)

    linear2, linear3, linear4, linear5 = [], [], [], []
    for amr in amrs:
        try:
            l = reduce(lambda x,y: x+y, map(lambda x: x.split('~'), lm2.process(amr['amr'].lower()).split()))
            linear2.append(' '.join(l))

            l = reduce(lambda x,y: x+y, map(lambda x: x.split('~'), lm3.process(amr['amr'].lower()).split()))
            linear3.append(' '.join(l))

            l = reduce(lambda x,y: x+y, map(lambda x: x.split('~'), lm4.process(amr['amr'].lower()).split()))
            linear4.append(' '.join(l))

            l = reduce(lambda x,y: x+y, map(lambda x: x.split('~'), lm5.process(amr['amr'].lower()).split()))
            linear5.append(' '.join(l))
        except:
            linear2.append('-')
            linear3.append('-')
            linear4.append('-')
            linear5.append('-')

    lm2.write('/home/tcastrof/amr/data/prince/linearization/test2.eval', linear2)
    lm3.write('/home/tcastrof/amr/data/prince/linearization/test3.eval', linear3)
    lm4.write('/home/tcastrof/amr/data/prince/linearization/test4.eval', linear4)
    lm5.write('/home/tcastrof/amr/data/prince/linearization/test5.eval', linear5)
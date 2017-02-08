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

if __name__ == '__main__':
    freq_table = json.load(open('../data/alignments/table.json'))
    verb2noun, noun2verb, verb2actor, actor2verb = utils.noun_verb('../data/morph-verbalization-v1.01.txt')
    sub2word = utils.subgraph_word('../data/verbalization-list-v1.06.txt')

    factory = ERGFactory(verb2noun=verb2noun,
                         noun2verb=noun2verb,
                         verb2actor=verb2actor,
                         actor2verb=actor2verb,
                         sub2word=sub2word)

    linear = Linearizer(erg_factory=factory, lm_path='../data/prince/linearization/lm.arpa')

    fdev = '../data/prince/test.txt'

    amrs = utils.parse_corpus(fdev, True)

    linearizations = []
    for amr in amrs:
        try:
            l = reduce(lambda x,y: x+y, map(lambda x: x.split('~'), linear.process(amr['amr'].lower()).split()))
            linearizations.append(' '.join(l))
        except:
            linearizations.append('-')

    f = open('../data/prince/linearization/test.eval', 'w')
    for linear in linearizations:
        f.write(linear)
        f.write('\n')
    f.close()
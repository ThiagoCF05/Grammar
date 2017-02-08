__author__ = 'thiagocastroferreira'

from main.grammars.ERG import ERGFactory

import itertools
import json
import main.utils as utils

class BaseLinear(object):
    def __init__(self, freq, erg_factory):
        self.freq = freq
        self.erg_factory = erg_factory

    def process(self, amr):
        erg = self.erg_factory.create_erg(amr)
        start_rule = filter(lambda rule_id: ':root' in erg.rules[rule_id].name, erg.rules)[0]

        linear = self.linearize(start_rule, erg, [])
        return linear

    def ranking(self, base, root, plain=False):
        candidates = []
        for candidate in itertools.permutations(base):
            snt = []
            for elem in candidate:
                if elem == root:
                    if plain:
                        snt.append(':root')
                    else:
                        snt.append(elem.split('~')[1])
                else:
                    snt.append(elem.split('~')[0])

            snt = ' '.join(snt)
            if snt.strip() in self.freq:
                score = self.freq[snt.strip()]
            else:
                score = 0
            candidates.append((candidate, score))

        return sorted(candidates, key=lambda x: x[1], reverse=True)

    def linearize(self, rule_id, erg, linear):
        rule_name = erg.rules[rule_id].name + '~' + erg.rules[rule_id].head
        base = [rule_name]

        if len(erg.rules[rule_id].rules) > 0:
            edges = reduce(lambda x, y: x+y, erg.rules[rule_id].rules.values())

            for edge in edges:
                _rule_id = edge.node_id

                name = erg.rules[_rule_id].name + '~' + erg.rules[_rule_id].head
                base.append(name)
            rank = self.ranking(base, rule_name, False)
            if len(filter(lambda x: x[1] > 0, rank)) == 0:
                rank = self.ranking(base, rule_name, True)
            candidate = rank[0][0]

            for name_head in candidate:
                if rule_name == name_head:
                    linear.extend(rule_name.split('~'))
                else:
                    name, head = name_head.split('~')
                    rule_id = filter(lambda rule_id: erg.rules[rule_id].name == name and erg.rules[rule_id].head == head, erg.rules)[0]
                    linear = self.linearize(rule_id, erg, linear)
        else:
            linear.extend(rule_name.split('~'))
        return linear

if __name__ == '__main__':
    freq_table = json.load(open('../data/alignments/table.json'))
    verb2noun, noun2verb, verb2actor, actor2verb = utils.noun_verb('../data/morph-verbalization-v1.01.txt')
    sub2word = utils.subgraph_word('../data/verbalization-list-v1.06.txt')

    factory = ERGFactory(verb2noun=verb2noun,
                         noun2verb=noun2verb,
                         verb2actor=verb2actor,
                         actor2verb=actor2verb,
                         sub2word=sub2word)

    freq = json.load(open('../data/prince/linearization/freq.txt'))
    linear = BaseLinear(erg_factory=factory, freq=freq)

    fdev = '../data/prince/dev.txt'

    amrs = utils.parse_corpus(fdev, True)

    linearizations = []
    for amr in amrs:
        try:
            # l = reduce(lambda x,y: x+y, map(lambda x: x.split('~'), linear.process(amr['amr'].lower()).split()))
            l = linear.process(amr['amr'].lower())
            linearizations.append(' '.join(l))
        except:
            linearizations.append('-')

    f = open('../data/prince/linearization/dev.baseline', 'w')
    for linear in linearizations:
        f.write(linear)
        f.write('\n')
    f.close()
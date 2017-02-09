__author__ = 'thiagocastroferreira'

from sys import path
path.append('/home/tcastrof/amr/scp_repo')
path.append('/home/tcastrof/amr/Grammar')
path.append('../../')

from main.grammars.ERG import ERGFactory

import json
import main.utils as utils
import nltk

class TrainLinear(object):
    def __init__(self, training_set, erg_factory):
        self.training = utils.parse_corpus(training_set, True)
        self.erg_factory = erg_factory

    def run(self):
        linearizations = []

        for amr in self.training:
            try:
                print amr['sentence']
                alignments = self.erg_factory.create_erg(amr['amr'])
                linearizations.extend(self.process(alignments))
            except:
                print 'error'
            print 10 * '-'
        return linearizations

    def write(self, linearizations, fwrite):
        f = open(fwrite, 'w')
        for linear in linearizations:
            f.write(' '.join(linear))
            f.write('\n')
        f.close()

    def process(self, alignments):
        sets = []

        for rule_id in alignments.rules:
            if len(alignments.rules[rule_id].rules) > 0:
                linear, linear_plain = [], []

                tokens = alignments.rules[rule_id].tokens
                head = alignments.rules[rule_id].head
                if len(tokens) > 0:
                    rule = (head, tokens[0])
                    linear.append(rule)

                    rule = (':root', tokens[0])
                    linear_plain.append(rule)

                graph_rules = reduce(lambda x, y: x+y, alignments.rules[rule_id].rules.values())
                for _rule in graph_rules:
                    _rule_id = _rule.node_id
                    if type(_rule_id) == str:
                        break
                    tokens = alignments.rules[_rule_id].tokens
                    head = alignments.rules[_rule_id].name #+ '~' + alignments.rules[_rule_id].head
                    if len(tokens) > 0:
                        rule = (head, tokens[0])
                        linear.append(rule)
                        linear_plain.append(rule)

                linear.sort(key=lambda x: x[1])
                linear_plain.sort(key=lambda x: x[1])

                flinear, fplain = [], []
                for i, rule in enumerate(linear):
                    flinear.append(linear[i][0])
                    fplain.append(linear_plain[i][0])
                sets.append(flinear)
                sets.append(fplain)
        return sets

if __name__ == '__main__':
    freq_table = json.load(open('../data/alignments/table.json'))
    verb2noun, noun2verb, verb2actor, actor2verb = utils.noun_verb('../data/morph-verbalization-v1.01.txt')
    sub2word = utils.subgraph_word('../data/verbalization-list-v1.06.txt')

    factory = ERGFactory(verb2noun=verb2noun,
                         noun2verb=noun2verb,
                         verb2actor=verb2actor,
                         actor2verb=actor2verb,
                         sub2word=sub2word)

    training = '/home/tcastrof/amr/data/prince/train/training.txt'

    linear = TrainLinear(training_set=training, erg_factory=factory)
    l = linear.run()

    # write = '../data/prince/linearization/linear_rules.txt'
    # linear.write(l, write)

    json_write = '/home/tcastrof/amr/data/prince/linearization/freq.json'
    l = map(lambda x: ' '.join(x), l)
    freq = nltk.FreqDist(l)
    json.dump(dict(freq), open(json_write,  'w'), sort_keys=True, indent=4, separators=(',', ': ') )
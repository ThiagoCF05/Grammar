import sys
sys.path.append('../../')

import main.utils as utils
import properties as prop
import os

from main.grammars.ERG import ERGFactory
from Generator import Generator
# from Realizer import Realizer

def write(l, fname):
    f = open(fname, 'w')
    for row in l:
        f.write(row)
        f.write('\n')
    f.close()

def write_lexical(l, fname):
    for key in l:
        f = open(fname+str(key), 'w')
        for row in l[key]:
            f.write(row)
            f.write('\n')
        f.close()

def run(fread, fwrite, models, factory):
    gold, lexicalized, realized = [], {}, {}
    for amr in utils.parse_corpus(fread, True):
        print amr['sentence']
        try:
            gen = Generator(amr=amr['amr'],
                            erg_factory=factory,
                            models=models,
                            beam_n=10)

            candidates = gen.run()
            for i in range(10):
                if i not in lexicalized:
                    lexicalized[i] = []

                if i < len(candidates):
                    tree = candidates[i].tree
                    lexicalized[i].append(tree.realize(root=tree.root, text=''))
                    # print tree.realize(root=tree.root, text=''), ' \t', tree.prettify(root=tree.root, isRule=False)
                else:
                    lexicalized[i].append('-')
        except:
            print 'Error'
            for i in range(10):
                if i not in lexicalized:
                    lexicalized[i] = []
                lexicalized[i].append('-')
        gold.append(amr['sentence'])

    write(gold, os.path.join(fwrite, 'gold'))
    write(lexicalized, os.path.join(fwrite, 'lexicalized'))
    # write(realized, 'realized')

if __name__ == '__main__':
    models = [prop.initial_rule_edges,
              prop.substitution_rule_edges,
              prop.initial_rule_edges_head,
              prop.substitution_rule_edges_head]
    verb2noun, noun2verb, verb2actor, actor2verb = utils.noun_verb(prop.morph_verb)
    sub2word = utils.subgraph_word(prop.verbalization)

    factory = ERGFactory(verb2noun=verb2noun,
                         noun2verb=noun2verb,
                         verb2actor=verb2actor,
                         actor2verb=actor2verb,
                         sub2word=sub2word)
    # realizer = Realizer()

    print 'Developing Set'
    fread = '../data/prince/dev.txt'
    fwrite = '/home/tcastrof/amr/data/prince/results/dev'
    run(fread=fread, fwrite=fwrite, models=models, factory=factory)

    print 'Test Set'
    fread = '../data/prince/test.txt'
    fwrite = '/home/tcastrof/amr/data/prince/results/test'
    run(fread=fread, fwrite=fwrite, models=models, factory=factory)
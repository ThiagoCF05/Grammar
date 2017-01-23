import sys
sys.path.append('../../')

import main.utils as utils
import properties as prop

from main.grammars.ERG import ERGFactory
from Generator import Generator
# from Realizer import Realizer

def write(l, fname):
    f = open(fname, 'w')
    for row in l:
        f.write(row)
        f.write('\n')
    f.close()

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

    dev_file = '../data/prince/dev.txt'

    gold, lexicalized, realized = [], [], []
    for amr in utils.parse_corpus(dev_file, True):
        print amr['sentence']
        try:
            gen = Generator(amr=amr['amr'],
                            erg_factory=factory,
                            models=models,
                            beam_n=20)

            candidates = gen.run()
            for candidate in candidates[:10]:
                tree = candidate.tree
                print tree.realize(root=tree.root, text=''), ' \t', tree.prettify(root=tree.root, isRule=False)
        except:
            print 'Error'
            # lexicalized.append('-')
            # realized.append('-')
        # gold.append(amr['sentence'])
        print 10 * '-'
            

    write(gold, 'gold')
    write(lexicalized, 'lexicalized')
    write(realized, 'realized')
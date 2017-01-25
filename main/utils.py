__author__ = 'thiagocastroferreira'

import re

def parse_aligned_corpus(fname):
    with open(fname) as f:
        doc = f.read()

    instances = doc.split('\n\n')[1:]

    amrs = []
    for instance in instances:
        try:
            instance = instance.split('\n')
            sentence_id = instance[0].split()[2]
            sentence = ' '.join(instance[1].split()[2:])
            alignments = instance[2].split()[2:]
            amr = '\n'.join(instance[3:])

            amrs.append({'id':sentence_id, 'file':fname, 'sentence': sentence, 'alignments': alignments, 'amr': amr})
        except:
            pass
    return amrs

def parse_corpus(fname, prince=False):
    with open(fname) as f:
        doc = f.read()

    instances = doc.split('\n\n')[1:]

    amrs = []
    for instance in instances:
        try:
            instance = instance.split('\n')
            # sentence_id = instance[0].split()[2]
            sentence = ' '.join(instance[1].split()[2:])
            if prince:
                amr = '\n'.join(instance[4:])
            else:
                amr = '\n'.join(instance[3:])

            amrs.append({'file':fname, 'sentence': sentence, 'amr': amr})
        except:
            pass
    return amrs

def noun_verb(fname):
    verb2noun, noun2verb = {}, {}
    verb2actor, actor2verb = {}, {}
    with open(fname) as f:
        doc = f.read()

    for row in doc.split('\n'):
        regex = re.compile("""::DERIV-VERB \"(.+?)\"""")
        verb = regex.match(row).groups()[0]

        regex = re.compile("""::DERIV-NOUN \"(.+?)\"""")
        m = regex.search(row)
        if m != None:
            noun = m.groups()[0]
            verb2noun[verb] = noun
            noun2verb[noun] = verb

        regex = re.compile("""::DERIV-NOUN-ACTOR \"(.+?)\"""")
        m = regex.search(row)
        if m != None:
            actor = m.groups()[0]
            verb2actor[verb] = actor
            actor2verb[actor] = verb

    return verb2noun, noun2verb, verb2actor, actor2verb

def subgraph_word(fname):
    sub2word = {}

    with open(fname) as f:
        doc = f.read()

    regex1 = re.compile("""VERBALIZE (.+) TO (.+)""")
    regex2 = re.compile("""MAYBE-VERBALIZE (.+) TO (.+)""")

    for row in doc.split('\n'):
        m = regex1.match(row)
        if m == None:
            m = regex2.match(row)

        if m != None:
            aux = m.groups()
            word = aux[0]

            _subgraph = aux[1].split()
            root = _subgraph[0]
            subgraph = [root]

            node, edge = '', ''
            for instance in _subgraph[1:]:
                if instance[0] == ':':
                    edge = instance
                else:
                    node = instance
                    subgraph.append((edge, node))
            subgraph = tuple(subgraph)
            if subgraph not in sub2word:
                sub2word[subgraph] = [word]
            else:
                sub2word[subgraph].append(word)

    return sub2word

from main.grammars.ERG import AMR

# if __name__ == '__main__':
#     f = open('data/prince/train/AMR_Aligned.keep')
#     doc = f.read()
#     doc = doc.split('\n\n')[:-1]
#     f.close()
#
#     fwrite = open('data/prince/train/training_aligned.txt', 'w')
#     fwrite.write('# AMR release; corpus: lpp; section: training; number of AMRs: 1274 (generated on Fri Mar 4, 2016 at 21:03:52)\n\n')
#     for row in doc:
#         snt, amr = row.split('\n')
#         snt = map(lambda w: w.split('_')[0], snt.split())
#         snt.insert(1, '::snt')
#         snt = ' '.join(snt)
#
#         graph = AMR(nodes={}, edges={}, root=1)
#         graph.parse(amr)
#         amr = graph.prettify(print_constants=True)
#
#         fwrite.write('#')
#         fwrite.write('\n')
#         fwrite.write(snt)
#         fwrite.write('\n')
#         fwrite.write('#')
#         fwrite.write('\n')
#         fwrite.write('#')
#         fwrite.write('\n')
#         fwrite.write(amr)
#         fwrite.write('\n')
#         fwrite.write('\n')
#     fwrite.close()

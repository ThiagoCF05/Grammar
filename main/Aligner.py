__author__ = 'thiagocastroferreira'

import copy

# from sys import path
# path.append('/home/tcastrof/amr/scp_repo')
# from stanford_corenlp_pywrapper import CoreNLP
from nltk.stem.porter import *

class Aligner(object):
    def __init__(self, verb2noun, noun2verb, verb2actor, actor2verb, sub2word, freq_table, proc):
        self.verb2noun = verb2noun
        self.noun2verb = noun2verb
        self.verb2actor = verb2actor
        self.actor2verb = actor2verb
        self.sub2word = sub2word
        self.freq_table = freq_table
        self.proc = proc

    # display the result not splitted by sentence
    def get_corenlp_result(self, text):
        info = self.proc.parse_doc(text)
        coref = info['entities']

        all_lemmas, all_pos, entitymentions, parse = [], [], [], ''
        sent2size = [0]
        for i, sent in enumerate(info['sentences']):
            all_lemmas.extend(sent['lemmas'])
            all_pos.extend(sent['pos'])

            for j, entity in enumerate(sent['entitymentions']):
                sent['entitymentions'][j]['tokspan'][0] += sent2size[-1]
                sent['entitymentions'][j]['tokspan'][1] += sent2size[-1]
            entitymentions.extend(sent['entitymentions'])

            parse += sent['parse'] + ' '

            sent2size.append(sent2size[-1]+len(sent['lemmas']))

        for entity in coref:
            for mention in entity['mentions']:
                mention['tokspan_in_sentence'][0] += sent2size[mention['sentence']]
                mention['tokspan_in_sentence'][1] += sent2size[mention['sentence']]

        parse = parse.strip()
        info = {'lemmas':all_lemmas, 'entitymentions':entitymentions, 'pos':all_pos, 'parse':parse}
        return info, coref

    def parse(self, amr):
        nodes, edges = {}, {'root':[]}

        node, edge, tokens = '', ':root', []
        parent = 'root'
        for instance in amr.replace('/', '').split():
            # closing = filter(lambda x: x == ')', instance)
            closing = 0
            for i in range(len(instance)):
                if instance[-(i+1)] == ')':
                    closing = closing + 1
                else:
                    break
            if closing > 0:
                instance = instance[:-closing]

            if instance[0] == ':':
                instance = instance.split('~e.')
                edge = instance[0]
                if len(instance) > 1:
                    tokens.extend(map(lambda x: int(x), instance[1].split(',')))
            elif instance[0] == '(':
                node = instance[1:]
            else:
                instance = instance.replace('\'', '').replace('\"', '').split('~e.')
                name = instance[0]
                if len(instance) > 1:
                    tokens.extend(map(lambda x: int(x), instance[1].split(',')))
                if node != '':
                    nodes[node] = {'name':name, 'parent':{'node':parent, 'edge':edge}, 'status':'unlabeled', 'tokens':list(set(tokens))}

                    edges[node] = []
                    edges[parent].append((edge, node))

                    parent = node
                else:
                    if edge not in [':wiki', ':mode']:
                        _node = copy.copy(name)
                        i = 1
                        while _node in nodes.keys():
                            _node = name + '-coref' + str(i)
                            i = i + 1
                        nodes[_node] = {'name':name, 'parent':{'node':parent, 'edge':edge}, 'status':'unlabeled', 'tokens':list(set(tokens))}

                        edges[_node] = []
                        edges[parent].append((edge, _node))
                node, tokens = '', []

            for i in xrange(closing):
                parent = nodes[parent]['parent']['node']
        return nodes, edges

    def match_node_patterns(self, root, lemmas):
        def set_label(string):
            indexes = filter(lambda x: lemmas[x][1] == 'unlabeled' and lemmas[x][0].lower() == string.lower(), xrange(len(lemmas)))
            if len(indexes) > 0:
                index = min(indexes)
                self.nodes[root]['tokens'].append(index)
                return index
            return -1
        def set_label_given(index):
            self.nodes[root]['tokens'].append(index)
            return index

        regex_propbank = re.compile('(.*)-[0-9]+')

        concept = self.nodes[root]['name']
        indexes = []

        # MATCH CONCEPT TO NODE
        isSet = set_label(concept)
        # MATCH PROPBANK
        if isSet < 0:
            m = regex_propbank.match(concept)
            if m != None:
                concept = m.groups()[0]
                # Split for the case of phrasal verbs
                for _concept in concept.split('-'):
                    isSet = set_label(_concept)
                    if isSet > -1:
                        indexes.append(isSet)
        # MATCH VERB2NOUN
        if isSet < 0:
            if concept in self.verb2noun:
                _concept = self.verb2noun[concept]
                isSet = set_label(_concept)
        # MATCH VERB2ACTOR
        if isSet < 0:
            if concept in self.verb2actor:
                _concept = self.verb2actor[concept]
                isSet = set_label(_concept)
        # MATCH contrast
        if isSet < 0 and concept == 'contrast':
            _indexes = filter(lambda x: lemmas[x][1] == 'unlabeled' and lemmas[x][0].lower() in ['but', 'however'], xrange(len(lemmas)))
            for index in _indexes:
                isSet = set_label_given(index)
                break
        # MATCH COMPARATIVE AND SUPERLATIVE
        if isSet < 0:
            _indexes = filter(lambda x: lemmas[x][1] == 'unlabeled' and self.info['pos'][x] in ['JJR', 'JJS'], xrange(len(lemmas)))
            for index in _indexes:
                if lemmas[index][0][:-2] == concept or (lemmas[index] == 'better' and concept == 'good') or (lemmas[index] == 'worse' and concept == 'bad'):
                    isSet = set_label_given(index)
                    break
                elif lemmas[index][0][:-3] == concept or (lemmas[index] == 'best' and concept == 'good') or (lemmas[index] == 'worst' and concept == 'bad'):
                    isSet = set_label_given(index)
                    break
        # QUESTIONS
        if isSet < 0 and concept == 'amr-unknown':
            _indexes = filter(lambda x: lemmas[x][1] == 'unlabeled' and self.info['pos'][x] in ['WDT', 'WP', 'WP$', 'WRB'], xrange(len(lemmas)))
            for index in _indexes:
                isSet = set_label_given(index)
                break
        # MATCH STEMMER
        if isSet < 0:
            stemmer = PorterStemmer()
            _indexes = filter(lambda x: lemmas[x][1] == 'unlabeled', xrange(len(lemmas)))
            for index in _indexes:
                if stemmer.stem(lemmas[index][0]) == stemmer.stem(concept):
                    isSet = set_label_given(index)
                    break
        # POLARITY
        if isSet < 0 and self.nodes[root]['parent']['edge'] == ':polarity':
            for concept in ['no', 'not', 'non', 'n\'t']:
                isSet = set_label(concept)
                if isSet > -1:
                    break
        # MODALS
        if isSet < 0 and self.nodes[root]['name'] in ['possible-01', 'obligate-01', 'permit-01', 'recommend-01', 'likely-01', 'prefer-01']:
            _indexes = filter(lambda x: lemmas[x][1] == 'unlabeled' and self.info['pos'][x] == 'MD', xrange(len(lemmas)))
            for index in _indexes:
                isSet = set_label_given(index)
                break
        # MATCH QUANTIFIERS
        if isSet < 0 and self.nodes[root]['parent']['edge'] in [':quant', ':value', ':op1', ':op2', ':op3', ':op4']:
            try:
                float_concept = float(concept)
                for entity in self.info['entitymentions']:
                    if entity['type'] in ['NUMBER', 'ORDINAL'] and float(entity['normalized']) == float_concept:
                        s, e = entity['tokspan']
                        indexes = range(s, e)
                        isSet = set_label_given(indexes[0])
                        break
                    elif entity['type'] == 'PERCENT' and float(entity['normalized'].replace('%', '')) == float_concept:
                        s, e = entity['tokspan']
                        indexes = range(s, e)
                        isSet = set_label_given(indexes[0])
                        break
            except:
                pass
        # DATE QUANTIFIERS
        if isSet < 0 and self.nodes[root]['parent']['edge'] in [':day', ':month', ':year']:
            try:
                float_concept = float(concept)
                for entity in self.info['entitymentions']:
                    if entity['type'] in ['ORDINAL'] and float(entity['normalized']) == float_concept:
                        s, e = entity['tokspan']
                        indexes = range(s, e)
                        isSet = set_label_given(indexes[0])
                        break
                    elif entity['type'] == 'DATE':
                        year, month, day = map(lambda x: float(x.replace('X', '0')), entity['normalized'].split('T')[0].split('-'))

                        s, e = entity['tokspan']
                        if self.nodes[root]['parent']['edge'] == ':day' and float_concept == day:
                            indexes = range(s, e)
                            isSet = indexes[0]
                        elif self.nodes[root]['parent']['edge'] == ':month' and float_concept == month:
                            indexes = range(s, e)
                            isSet = indexes[0]
                        elif self.nodes[root]['parent']['edge'] == ':year' and float_concept == year:
                            indexes = range(s, e)
                            isSet = indexes[0]
                        if isSet > -1:
                            set_label_given(isSet)
                            break
            except:
                pass
        # TIME QUANTIFIERS
        if isSet < 0 and self.nodes[root]['parent']['edge'] in [':time']:
            try:
                for entity in self.info['entitymentions']:
                    if entity['type'] == 'TIME':
                        time = entity['normalized'].split('T')[-1]
                        if time[0] == '0':
                            time = time[1:]
                        if str(concept) == str(time):
                            s, e = entity['tokspan']
                            indexes = range(s, e)
                            isSet = indexes[0]
                            set_label_given(isSet)
                            break
            except:
                pass
        if isSet > -1 and len(indexes) == 0:
            indexes = [isSet]
        return indexes

    def match_frequency_patterns(self, root, lemmas):
        try:
            concept2freq = self.freq_table[root]
            max_freq = ('NULL', concept2freq['NULL'])

            for lemma in filter(lambda x: x[1] == 'unlabeled', lemmas):
                try:
                    freq = concept2freq[lemma[0]]
                except:
                    freq = 0

                if freq > max_freq[1]:
                    max_freq = (lemma[0], freq)

            if max_freq[0] != 'NULL':
                for i, lemma in enumerate(lemmas):
                    if lemma[1] == 'unlabeled' and lemma[0] == max_freq[0]:
                        self.nodes[root]['tokens'].append(i)
                        lemmas[i][1] = 'labeled'
                        break
        except:
            pass
        return self._create_alignment(root), lemmas

    def match_subgraph_patterns(self, root, lemmas):
        # filter subgraphs with the root given as a parameter which the word related is in the sentence
        f = filter(lambda iter: iter[0][0] == self.nodes[root]['name'], self.sub2word.iteritems())

        subgraphs, lemma = [], ''
        for candidate in f:
            for _lemma in filter(lambda x: x[1] == 'unlabeled', lemmas):
                if _lemma[0] in candidate[1]:
                    subgraphs.append(candidate[0])
                    lemma = _lemma[0]
                    break

        if len(subgraphs) > 0:
            subgraphs = sorted(subgraphs, key=len)
            subgraphs.reverse()

            matched = True
            filtered_subgraph = [self.nodes[root]['name']]
            for sub in subgraphs:
                matched = True
                for edge in sub[1:]:
                    f = filter(lambda match_edge: match_edge[0] == edge[0] and self.nodes[match_edge[1]]['name'] == edge[1], self.edges[root])
                    if len(f) > 0:
                        filtered_subgraph.append(f[0])
                    else:
                        matched = False
                        filtered_subgraph = [self.nodes[root]['name']]
                        break
                if matched:
                    break

            if matched:
                return self.info['lemmas'].index(lemma), filtered_subgraph
        return -1, -1

    def match_coreferences_patterns(self, root, tokens, lemmas):
        alignments = []

        for entity in self.coref:
            if len(entity['mentions']) > 1:
                first_mention =  entity['mentions'][0]
                s, e = first_mention['tokspan_in_sentence']
                interval = range(s, e)
                if len(filter(lambda x: x in interval, tokens)) > 0:
                    match = root + '-coref'
                    for i in range(len(filter(lambda node: match in node, self.nodes))):
                        try:
                            node = match + str(i+1)
                            s,e = entity['mentions'][i+1]['tokspan_in_sentence']
                            indexes = range(s, e)
                            self.nodes[node]['tokens'] = indexes

                            for index in indexes:
                                lemmas[index] = (lemmas[index][0], 'labeled')

                            alignment = self._create_alignment(node)
                            alignments.append(alignment)
                        except:
                            pass
                    break
        return alignments, lemmas

    def _create_alignment(self, root):
        self.nodes[root]['status'] = 'labeled'

        edge = (self.nodes[root]['parent']['edge'], root)
        indexes = self.nodes[root]['tokens']
        lemmas = map(lambda x: self.info['lemmas'][x], indexes)
        alignment = {'edges':[edge], 'tokens':indexes, 'ids':[], 'lemmas':lemmas}
        return alignment

    def align(self, root, visited, lemmas, alignments, id, isAligned = False):
        def create_subgraph_alignment(edges):
            self.nodes[root]['status'] = 'labeled'
            alignment = {'edges':[], 'tokens':[], 'ids':[]}

            edge = (self.nodes[root]['parent']['edge'], root)
            alignment['edges'].append(edge)
            alignment['tokens'].extend(self.nodes[root]['tokens'])

            for edge in edges:
                self.nodes[edge[1]]['status'] = 'labeled'
                alignment['edges'].append(edge)

                indexes = self.nodes[edge[1]]['tokens']
                alignment['tokens'].extend(indexes)
            alignment['tokens'] = list(set(alignment['tokens']))
            return alignment

        visited.append(root)
        self.nodes[root]['id'] = id

        # Find entity and quantity nodes
        regex = re.compile("""(.+-entity)$|(.+-quantity)$""")

        if self.nodes[root]['status'] != 'labeled':
            # Find subgraph defined at verbalization-list, and have-org/rel
            index, subgraph = self.match_subgraph_patterns(root, lemmas)
            if index > -1:
                lemmas[index] = (lemmas[index][0], 'labeled')

                # When there is no edges
                if len(subgraph) == 1:
                    self.nodes[root]['tokens'].append(index)
                    alignment = self._create_alignment(root)
                    alignments.append(alignment)
                else:
                    self.nodes[subgraph[1][1]]['tokens'].append(index)
                    alignments.append(create_subgraph_alignment(subgraph[1:]))
            elif not isAligned:
                indexes = self.match_node_patterns(root, lemmas)
                for index in indexes:
                    lemmas[index] = (lemmas[index][0], 'labeled')

        for i, edge in enumerate(self.edges[root]):
            if edge[1] not in visited:
                lemmas, alignments = self.align(edge[1], visited, lemmas, alignments, id+'.'+str(i), isAligned)

            # MATCH parent of :degree non-matched
            if edge[0] == ':degree' and len(self.nodes[edge[1]]['tokens']) == 0:
                alignments.append(create_subgraph_alignment([edge]))

            # MATCH parent of :name
            if edge[0] == ':name':
                self.nodes[root]['status'] = 'labeled'

                for alignment in alignments:
                    if edge in alignment['edges']:
                        n_e = (self.nodes[root]['parent']['edge'], root)
                        alignment['tokens'].extend(self.nodes[root]['tokens'])
                        alignment['edges'].insert(0, n_e)
                        break

            # MATCH reification
            elif self.nodes[edge[1]]['name'] in ['have-rel-role-91', 'have-org-role-91'] and self.nodes[root]['status'] != 'labeled' and len(self.nodes[root]['tokens']) == 0:
                self.nodes[root]['status'] = 'labeled'

                for alignment in alignments:
                    if edge in alignment['edges']:
                        n_e = (self.nodes[root]['parent']['edge'], root)
                        alignment['tokens'].extend(self.nodes[root]['tokens'])
                        alignment['edges'].insert(0, n_e)
                        break

        # MATCH NAME NODES
        if self.nodes[root]['name'] == 'name':
            alignments.append(create_subgraph_alignment(self.edges[root]))
        # MATCH entity and quantity nodes
        elif regex.match(self.nodes[root]['name']) != None:
            alignments.append(create_subgraph_alignment(self.edges[root]))
        # MATCH org and rel roles
        elif self.nodes[root]['name'] in ['have-rel-role-91', 'have-org-role-91']:
            edges = filter(lambda x: x[0] == ':ARG2', self.edges[root])
            alignments.append(create_subgraph_alignment(edges))

        return lemmas, alignments

    def train(self, amr, text):
        self.info, self.coref = self.get_corenlp_result(text)

        self.nodes, self.edges = self.parse(amr)

        lemmas = map(lambda x: (x, 'unlabeled'), self.info['lemmas'])

        root = self.edges['root'][0][1]
        lemmas, alignments = self.align(root, [], lemmas, [], '0', True)

        for node in self.nodes:
            if self.nodes[node]['status'] != 'labeled':
                alignment = self._create_alignment(node)
                alignments.append(alignment)

        for alignment in alignments:
            alignment['ids'] = map(lambda edge: self.nodes[edge[1]]['id'], alignment['edges'])
            alignment['edges'] = map(lambda edge: (edge[0], self.nodes[edge[1].split('-coref')[0]]['name']), alignment['edges'])
        return alignments

    def run(self, amr, text):
        self.info, self.coref = self.get_corenlp_result(text)

        self.nodes, self.edges = self.parse(amr)

        # replace people for person
        count = len(filter(lambda x: x == 'people', self.info['lemmas']))
        while count != 0:
            self.info['lemmas'][self.info['lemmas'].index('people')] = 'person'
            count = count - 1
        lemmas = map(lambda x: (x, 'unlabeled'), self.info['lemmas'])

        root = self.edges['root'][0][1]
        lemmas, alignments = self.align(root, [], lemmas, [], '0')

        for node in self.nodes:
            if self.nodes[node]['status'] != 'labeled':
                if len(self.nodes[node]['tokens']) > 0:
                    alignment = self._create_alignment(node)
                    alignments.append(alignment)

        # Label coreferences
        coreferences = filter(lambda node: '-coref' in node and self.nodes[node] != 'labeled', self.nodes)
        entities = set(map(lambda ref: ref.split('-')[0], coreferences))
        for entity in entities:
            tokens = []
            for alignment in alignments:
                if len(filter(lambda edge: edge[1] == entity, alignment['edges'])) > 0:
                    tokens = alignment['tokens']
                    break
            if len(tokens) == 0:
                tokens = self.nodes[entity]['tokens']
            _alignments, lemmas = self.match_coreferences_patterns(entity, tokens, lemmas)
            alignments.extend(_alignments)

        for node in self.nodes:
            if self.nodes[node]['status'] != 'labeled':
                alignment, lemmas = self.match_frequency_patterns(node, lemmas)
                alignments.append(alignment)

        for alignment in alignments:
            alignment['ids'] = map(lambda edge: self.nodes[edge[1]]['id'], alignment['edges'])
            alignment['edges'] = map(lambda edge: (edge[0], self.nodes[edge[1]]['name']), alignment['edges'])

        return alignments, self.info
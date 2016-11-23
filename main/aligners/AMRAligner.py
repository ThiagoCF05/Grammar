__author__ = 'thiagocastroferreira'

import copy
import re

from main.aligners.Alignments import Alignments
from main.grammars.ERG import AMR, AMRNode, AMREdge, ERGRule
from nltk.stem.porter import *

class AMRAligner(object):
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

        all_lemmas, all_tokens, all_pos, entitymentions, parse = [], [], [], [], ''
        sent2size = [0]
        for i, sent in enumerate(info['sentences']):
            all_lemmas.extend(sent['lemmas'])
            all_tokens.extend(sent['tokens'])
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
        info = {'lemmas':all_lemmas, 'entitymentions':entitymentions, 'pos':all_pos, 'parse':parse, 'tokens':all_tokens}
        return info, coref

    def create_rule(self, root, rule=None):
        self.amr.nodes[root].status = 'labeled'

        if rule == None:
            rule = ERGRule(name=self.amr.nodes[root].parent['edge'],
                           head=self.amr.nodes[root].name,
                           graph=AMR(nodes={}, edges={}, root=root),
                           tokens=[],
                           lemmas=[],
                           parent='',
                           rules={})

        indexes = copy.copy(self.amr.nodes[root].tokens)
        lemmas = map(lambda x: self.info['lemmas'][x], indexes)
        rule.tokens.extend(indexes)
        rule.lemmas.extend(lemmas)

        node = self.amr.nodes[root]
        rule.graph.nodes[root] = AMRNode(id=node.id, name=node.name, parent=node.parent, status=node.status, tokens=node.tokens)

        rule.graph.edges[root] = []
        for edge in self.amr.edges[root]:
            rule.graph.edges[root].append(AMREdge(name=edge.name, node_id=edge.node_id, isRule=True))

            if root not in rule.rules:
                rule.rules[root] = []
            rule.rules[root].append(edge.name)

        rule.tokens = list(set(rule.tokens))
        return rule

    def create_subgraph_rule(self, root, edges):
        rule = self.create_rule(root)

        for edge in edges:
            if self.amr.nodes[edge.node_id].status == 'unlabeled':
                rule = self.create_rule(edge.node_id, rule)

                for _edge in rule.graph.edges[root]:
                    if _edge.name == edge.name:
                        rule.rules[root].remove(_edge.name)
                        _edge.isRule = False
                        break

        if root in rule.rules and len(rule.rules[root]) == 0:
            del rule.rules[root]

        return rule

    def create_father(self, root, edge):
        self.amr.nodes[root].status = 'labeled'

        for rule_id in self.alignments.erg_rules:
            rule = self.alignments.erg_rules[rule_id]

            if rule.graph.root == edge.node_id:
                rule.name = self.amr.nodes[root].parent['edge']
                rule.head = self.amr.nodes[root].name
                rule.graph.root = root

                indexes = self.amr.nodes[root].tokens
                _lemmas = map(lambda x: self.info['lemmas'][x], indexes)
                rule.tokens.extend(indexes)
                rule.lemmas.extend(_lemmas)
                rule.tokens = list(set(rule.tokens))

                rule.graph.nodes[root] = copy.copy(self.amr.nodes[root])

                rule.graph.edges[root] = []
                for _edge in self.amr.graph.edges[root]:
                    if _edge.name == edge.name:
                        rule.graph.edges[root].append(AMREdge(name=_edge.name, node_id=_edge.node_id, isRule=False))
                    else:
                        rule.graph.edges[root].append(AMREdge(name=_edge.name, node_id=_edge.node_id, isRule=True))
                        if root not in rule.rules:
                            rule.rules[root] = []
                        rule.rules[root].append(_edge.name)
                break

    def match_frequency_patterns(self, root):
        try:
            concept2freq = self.freq_table[root]
            max_freq = ('NULL', concept2freq['NULL'])

            for lemma in filter(lambda x: x[1] == 'unlabeled', self.lemmas):
                try:
                    freq = concept2freq[lemma[0]]
                except:
                    freq = 0

                if freq > max_freq[1]:
                    max_freq = (lemma[0], freq)

            if max_freq[0] != 'NULL':
                for i, lemma in enumerate(self.lemmas):
                    if lemma[1] == 'unlabeled' and lemma[0] == max_freq[0]:
                        self.amr.nodes[root].tokens.append(i)
                        self.lemmas[i][1] = 'labeled'
                        break
        except:
            pass
        return self.create_rule(root)

    def match_subgraph_patterns(self, root):
        # filter subgraphs with the root given as a parameter which the related word is in the sentence
        f = filter(lambda iter: iter[0][0] == self.amr.nodes[root].name, self.sub2word.iteritems())

        subgraphs, lemma = [], ''
        for candidate in f:
            for _lemma in filter(lambda x: x[1] == 'unlabeled', self.lemmas):
                if _lemma[0] in candidate[1]:
                    subgraphs.append(candidate[0])
                    lemma = _lemma[0]
                    break

        if len(subgraphs) > 0:
            subgraphs = sorted(subgraphs, key=len)
            subgraphs.reverse()

            matched = True
            filtered_subgraph = [self.amr.nodes[root].name]
            for sub in subgraphs:
                matched = True
                for edge in sub[1:]:
                    f = filter(lambda match_edge: match_edge.name == edge[0] and self.amr.nodes[match_edge.node_id].name == edge[1], self.amr.edges[root])
                    if len(f) > 0:
                        filtered_subgraph.append(f[0])
                    else:
                        matched = False
                        filtered_subgraph = [self.amr.nodes[root].name]
                        break
                if matched:
                    break

            if matched:
                return self.info['lemmas'].index(lemma), filtered_subgraph
        return -1, -1

    def match_node_patterns(self, root):
        def set_label(string):
            indexes = filter(lambda x: self.lemmas[x][1] == 'unlabeled' and self.lemmas[x][0].lower() == string.lower(), xrange(len(self.lemmas)))
            if len(indexes) > 0:
                index = min(indexes)
                self.amr.nodes[root].tokens.append(index)
                return index
            return -1

        def set_label_given(index):
            self.amr.nodes[root].tokens.append(index)
            return index

        regex_propbank = re.compile('(.*)-[0-9]+')

        concept = self.amr.nodes[root].name
        indexes = []

        # MATCH CONCEPT TO NODE
        isSet = set_label(concept)
        # MATCH PROPBANK
        if isSet < 0:
            m = regex_propbank.match(concept)
            # Avoid reification tags
            if m != None and str(concept.split('-')[-1]) != '91':
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
            _indexes = filter(lambda x: self.lemmas[x][1] == 'unlabeled' and self.lemmas[x][0].lower() in ['but', 'however'], xrange(len(self.lemmas)))
            if len(_indexes) > 0:
                isSet = set_label_given(_indexes[-1])
        # MATCH COMPARATIVE AND SUPERLATIVE
        if isSet < 0:
            _indexes = filter(lambda x: self.lemmas[x][1] == 'unlabeled' and self.info['pos'][x] in ['JJR', 'JJS'], xrange(len(self.lemmas)))
            for index in _indexes:
                if self.lemmas[index][0][:-2] == concept or (self.lemmas[index] == 'better' and concept == 'good') or (self.lemmas[index] == 'worse' and concept == 'bad'):
                    isSet = set_label_given(index)
                    break
                elif self.lemmas[index][0][:-3] == concept or (self.lemmas[index] == 'best' and concept == 'good') or (self.lemmas[index] == 'worst' and concept == 'bad'):
                    isSet = set_label_given(index)
                    break
        # QUESTIONS
        if isSet < 0 and concept == 'amr-unknown':
            _indexes = filter(lambda x: self.lemmas[x][1] == 'unlabeled' and self.info['pos'][x] in ['WDT', 'WP', 'WP$', 'WRB'], xrange(len(self.lemmas)))
            for index in _indexes:
                isSet = set_label_given(index)
                break
        # MATCH STEMMER
        if isSet < 0:
            stemmer = PorterStemmer()
            _indexes = filter(lambda x: self.lemmas[x][1] == 'unlabeled', xrange(len(self.lemmas)))
            for index in _indexes:
                try:
                    if stemmer.stem(self.lemmas[index][0]) == stemmer.stem(concept):
                        isSet = set_label_given(index)
                        break
                except:
                    pass
        # POLARITY
        if isSet < 0 and self.amr.nodes[root].parent['edge'] == ':polarity':
            for concept in ['no', 'not', 'non', 'n\'t']:
                isSet = set_label(concept)
                if isSet > -1:
                    break
        # MODALS
        m = regex_propbank.match(self.amr.nodes[root].name)
        if m != None:
            concept = m.groups()[0]
        else:
            concept = self.amr.nodes[root].name
        if isSet < 0 and concept in ['possible', 'obligate', 'permit', 'recommend', 'likely', 'prefer']:
            _indexes = filter(lambda x: self.lemmas[x][1] == 'unlabeled' and self.lemmas[x][0].lower() not in ['will', 'would'] and self.info['pos'][x] == 'MD', xrange(len(self.lemmas)))
            for index in _indexes:
                isSet = set_label_given(index)
                break
        # MATCH QUANTIFIERS
        if isSet < 0 and self.amr.nodes[root].parent['edge'] in [':quant', ':value', ':op1', ':op2', ':op3', ':op4']:
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
        if isSet < 0 and self.amr.nodes[root].parent['edge'] in [':day', ':month', ':year']:
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
                        if self.amr.nodes[root].parent['edge'] == ':day' and float_concept == day:
                            indexes = range(s, e)
                            isSet = indexes[0]
                        elif self.amr.nodes[root].parent['edge'] == ':month' and float_concept == month:
                            indexes = range(s, e)
                            isSet = indexes[0]
                        elif self.amr.nodes[root].parent['edge'] == ':year' and float_concept == year:
                            indexes = range(s, e)
                            isSet = indexes[0]
                        if isSet > -1:
                            set_label_given(isSet)
                            break
            except:
                pass
        # TIME QUANTIFIERS
        if isSet < 0 and self.amr.nodes[root].parent['edge'] in [':time']:
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

    def match_coreferences_patterns(self):
        def match(root, tokens):
            for entity in self.coref:
                if len(entity['mentions']) > 1:
                    first_mention =  entity['mentions'][0]
                    s, e = first_mention['tokspan_in_sentence']
                    interval = range(s, e)
                    if len(filter(lambda x: x in interval, tokens)) > 0:
                        match = root + '-coref'
                        for i in range(len(filter(lambda node: match in node, self.amr.nodes))):
                            try:
                                node = match + str(i+1)
                                s,e = entity['mentions'][i+1]['tokspan_in_sentence']
                                indexes = range(s, e)
                                self.amr.nodes[node].tokens = indexes

                                for index in indexes:
                                    self.lemmas[index] = (self.lemmas[index][0], 'labeled')

                                rule = self.create_rule(node)
                                self.alignments.erg_rules[self.alignments.count] = rule
                                self.alignments.count = self.alignments.count + 1
                            except:
                                pass
                        break

        coreferences = filter(lambda node: '-coref' in node and self.amr.nodes[node].status != 'labeled', self.amr.nodes)
        entities = set(map(lambda ref: ref.split('-')[0], coreferences))
        for entity in entities:
            tokens = []
            for rule_id in self.alignments.erg_rules:
                if entity in self.alignments.erg_rules[rule_id].graph.nodes:
                    tokens = self.alignments.erg_rules[rule_id].tokens
                    break
            if len(tokens) == 0 and entity in self.amr.nodes:
                tokens = self.amr.nodes[entity].tokens
            match(entity, tokens)

    def align(self, root, visited, isAligned = False):
        visited.append(root)

        # Find entity and quantity nodes
        regex = re.compile("""(.+-entity)$|(.+-quantity)$""")

        if self.amr.nodes[root].status != 'labeled':
            # Find subgraph defined at verbalization-list, and have-org/rel
            index, subgraph = self.match_subgraph_patterns(root)
            if index > -1:
                self.lemmas[index] = (self.lemmas[index][0], 'labeled')

                # When there is no edges
                if len(subgraph) == 1:
                    self.amr.nodes[root].tokens.append(index)
                    rule = self.create_rule(root)
                else:
                    self.amr.nodes[subgraph[1].node_id].tokens.append(index)
                    rule = self.create_subgraph_rule(root, subgraph[1:])
                self.alignments.erg_rules[self.alignments.count] = rule
                self.alignments.count = self.alignments.count + 1
            elif not isAligned:
                indexes = self.match_node_patterns(root)
                for index in indexes:
                    self.lemmas[index] = (self.lemmas[index][0], 'labeled')

        for i, edge in enumerate(self.amr.edges[root]):
            if edge.node_id not in visited:
                self.align(edge.node_id, visited, isAligned)

            # MATCH parent of :degree non-matched
            if edge.name == ':degree' and len(self.amr.nodes[edge.node_id].tokens) == 0:
                rule = self.create_subgraph_rule(root, [edge])
                self.alignments.erg_rules[self.alignments.count] = rule
                self.alignments.count = self.alignments.count + 1

            # MATCH parent of :name
            if edge.name == ':name':
                self.create_father(root, edge)

            # MATCH reification
            elif self.amr.nodes[edge.node_id].name in ['have-rel-role-91', 'have-org-role-91'] and self.amr.nodes[root].status != 'labeled' and len(self.amr.nodes[root].tokens) == 0:
                self.create_father(root, edge)

        # MATCH NAME NODES
        if self.amr.nodes[root].name == 'name':
            rule = self.create_subgraph_rule(root, self.amr.edges[root])
            self.alignments.erg_rules[self.alignments.count] = rule
            self.alignments.count = self.alignments.count + 1
        # MATCH entity and quantity nodes
        elif regex.match(self.amr.nodes[root].name) != None:
            rule = self.create_subgraph_rule(root, self.amr.edges[root])
            self.alignments.erg_rules[self.alignments.count] = rule
            self.alignments.count = self.alignments.count + 1
        # MATCH org and rel roles
        elif self.amr.nodes[root].name in ['have-rel-role-91', 'have-org-role-91']:
            edges = filter(lambda edge: edge.name == ':ARG2', self.amr.edges[root])
            rule = self.create_subgraph_rule(root, edges)
            self.alignments.erg_rules[self.alignments.count] = rule
            self.alignments.count = self.alignments.count + 1

    def run(self, amr, text):
        self.info, self.coref = self.get_corenlp_result(text)

        # Initialize AMR
        self.amr = AMR(nodes={}, edges={}, root='')
        self.amr.parse(amr)

        # replace people for person
        count = len(filter(lambda x: x == 'people', self.info['lemmas']))
        while count != 0:
            self.info['lemmas'][self.info['lemmas'].index('people')] = 'person'
            count = count - 1
        self.lemmas = map(lambda x: (x, 'unlabeled'), self.info['lemmas'])

        # Initialize Aligner
        self.alignments = Alignments(erg_rules={}, tag_rules={}, adjoining_rules={}, features={}, id2rule={})
        root = self.amr.edges['root'][0].node_id
        self.align(root, [], False)

        # Label nodes that have at least one token attached
        for node in self.amr.nodes:
            if self.amr.nodes[node].status != 'labeled':
                if len(self.amr.nodes[node].tokens) > 0:
                    rule = self.create_rule(node)
                    self.alignments.erg_rules[self.alignments.count] = rule
                    self.alignments.count = self.alignments.count + 1

        # Label coreferences
        self.match_coreferences_patterns()

        # Classify unlabeled nodes by frequency in the training alignments
        for node in self.amr.nodes:
            if self.amr.nodes[node].status != 'labeled':
                rule = self.match_frequency_patterns(node)
                self.alignments.erg_rules[self.alignments.count] = rule
                self.alignments.count = self.alignments.count + 1

        # Set parent rule names
        for rule_id in self.alignments.erg_rules:
            graph = self.alignments.erg_rules[rule_id].graph
            root = graph.root
            parent = graph.nodes[root].parent

            for _id in self.alignments.erg_rules:
                if parent['node'] in self.alignments.erg_rules[_id].graph.nodes:
                    self.alignments.erg_rules[rule_id].parent = _id
                    break

        return self.alignments, self.info

    # TO DO: refactor
    def train(self, amr, text):
        self.info, self.coref = self.get_corenlp_result(text)

        # Initialize Aligner
        self.alignments = Alignments(erg_rules={}, tag_rules={}, adjoining_rules={}, features={}, id2rule={})

        # Initialize AMR
        self.amr = AMR(nodes={}, edges={}, root='')
        self.amr.parse(amr)

        self.lemmas = map(lambda x: (x, 'unlabeled'), self.info['lemmas'])
        root = self.amr.edges['root'][0].node_id
        self.align(root, [], True)

        for node in self.amr.nodes:
            rule = self.create_rule(node)
            self.alignments.erg_rules[self.alignments.count] = rule
            self.alignments.count = self.alignments.count + 1

        # Set parent rule names
        for rule_id in self.alignments.erg_rules:
            graph = self.alignments.erg_rules[rule_id].graph
            root = graph.root
            parent = graph.nodes[root].parent

            for _id in self.alignments.erg_rules:
                if parent['node'] in self.alignments.erg_rules[_id].graph.nodes:
                    self.alignments.erg_rules[rule_id].parent = _id
                    break

        return self.alignments, self.info
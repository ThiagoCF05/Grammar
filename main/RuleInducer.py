__author__ = 'thiagocastroferreira'

"""
Author: Thiago Castro Ferreira
Date: 31/10/2016
Description:
    This script aims to extract the rules of our Lexicalized Tree Adjoining Grammar
"""

import copy

class RuleInducer(object):
    def __init__(self, text, amr, info, alignments):
        self.text = text
        self.tokens = text.split()
        self.amr = amr
        self.tree = info['parse']
        self.alignments = alignments
        self.info = info

    def get_rules(self):
        rule_id = 1
        id2alignment, id2subtrees = {}, {}
        for i, align in enumerate(self.alignments):
            id2alignment[rule_id] = align

            # Initializing subtrees with their heads
            id2subtrees[rule_id] = {'tree':{}, 'nodes':{}, 'head':[], 'root':'', 'info':{'type':'', 'pos':[], 'tokens':[], 'lemmas':[]}}
            id2subtrees[rule_id]['head'].append(align['edges'][0][1])
            id2subtrees[rule_id]['head'].extend(map(lambda x: x[0], align['edges'][1:]))

            rule_id = rule_id + 1
        return id2alignment, id2subtrees

    def parse_tree(self):
        nodes = {}
        tree = {}

        _id = 1
        prev_id = 0
        terminal_id = 0

        for child in self.tree.replace('\n', '').split():
            if child[0] == '(':
                nodes[_id] = {'name': child[1:], 'parent': prev_id, 'type':'nonterminal'}
                tree[_id] = []
                if prev_id > 0:
                    tree[prev_id].append(_id)
                prev_id = copy.copy(_id)
                _id = _id + 1
            else:
                closing = filter(lambda x: x == ')', child)
                terminal = child.replace(closing, '')
                nodes[prev_id]['value'] = terminal_id
                nodes[prev_id]['lexicon'] = terminal
                nodes[prev_id]['type'] = 'terminal'

                terminal_id = terminal_id + 1

                for i in xrange(len(closing)):
                    prev_id = nodes[prev_id]['parent']
        return nodes, tree, _id

    # TO DO: treat modals would, should, might to, must, etc.
    def get_verb_tense(self, pos, lemmas):
        voice, tense = 'active', 'simple present'
        if len(pos) == 1:
            if pos[0] == 'VB':
                tense = 'infinitive'
            elif pos[0] in ['VBP', 'VBZ']:
                tense = 'simple present'
            elif pos[0] in ['VBD', 'VBN']:
                tense = 'simple past'
            elif pos[0] == 'VBG':
                tense = 'present continuous'
        elif len(pos) == 2:
            if pos[0] in ['VB', 'VBP', 'VBZ']:
                if lemmas[0] == 'be' and pos[1] == 'VBG':
                    tense = 'present continuous'
                elif lemmas[0] == 'have' and pos[1] == 'VBN':
                    tense = 'present perfect'
                elif lemmas[0] == 'be' and pos[1] == 'VBN':
                    tense = 'simple present'
                    voice = 'passive'
            elif pos[0] == 'VBD':
                if lemmas[0] == 'be' and pos[1] == 'VBG':
                    tense = 'past continuous'
                elif lemmas[0] == 'have' and pos[1] == 'VBN':
                    tense = 'past perfect'
                elif lemmas[0] == 'be' and pos[1] == 'VBN':
                    tense = 'simple past'
                    voice = 'passive'
            elif lemmas[0] == 'will':
                tense = 'simple future'
        elif len(pos) == 3:
            if pos[0] in ['VB', 'VBP', 'VBZ']:
                if lemmas[0] == 'have' and pos[1] == 'VBN' and lemmas[1] == 'be':
                    if pos[2] == 'VBG':
                        tense = 'present perfect continuous'
                    elif pos[2] == 'VBN':
                        tense = 'present perfect'
                        voice = 'passive'
                elif lemmas[0] == 'be' and pos[1] == 'VBN' and lemmas[1] == 'be' and pos[2] == 'VBN':
                    tense = 'simple present continuous'
                    voice = 'passive'
            elif pos[0] == 'VBD':
                if lemmas[0] == 'have' and pos[1] == 'VBN' and lemmas[1] == 'be':
                    if pos[2] == 'VBG':
                        tense = 'past perfect continuous'
                    elif pos[2] == 'VBN':
                        tense = 'past perfect'
                        voice = 'passive'
                elif lemmas[0] == 'be' and pos[1] == 'VBN' and lemmas[1] == 'be' and pos[2] == 'VBN':
                    tense = 'simple past continuous'
                    voice = 'passive'
            elif lemmas[0] == 'will':
                if lemmas[1] == 'be':
                    if pos[2] == 'VBG':
                        tense = 'future continuous'
                    elif pos[2] == 'VBN':
                        tense = 'simple future'
                        voice = 'passive'
                elif lemmas[1] == 'have' and pos[2] == 'VBN':
                    tense = 'future perfect'
        elif len(pos) == 4:
            if pos[1] == 'VBN' and lemmas[1] == 'be' \
                    and pos[2] == 'VBG' and lemmas[2] == 'be' and pos[3] == 'VBN':
                if pos[0] in ['VB', 'VBP', 'VBZ'] and lemmas[0] == 'have':
                    tense = 'present perfect continuous'
                    voice = 'passive'
                elif pos[0] == 'VBD' and lemmas[0] == 'have':
                    tense = 'past perfect continuous'
                    voice = 'passive'
            elif lemmas[0] == 'will':
                if lemmas[1] == 'have' and pos[2] == 'VBN' and lemmas[2] == 'be':
                    if pos[3] == 'VBG':
                        tense = 'future present continuous'
                    elif pos[3] == 'VBN':
                        tense = 'future perfect'
                        voice = 'passive'
                elif lemmas[1] == 'be' and pos[2] == 'VBG' and lemmas[2] == 'be' and lemmas[3] == 'VBN':
                    tense = 'future continuous'
                    voice = 'passive'
        elif len(pos) == 5:
            if lemmas[0] == 'will' and lemmas[1] == 'have' \
                    and pos[2] == 'VBN' and lemmas[2] == 'be' \
                    and pos[3] == 'VBG' and lemmas[3] and pos[4] == 'VBN':
                tense = 'future perfect continuos'
                voice = 'passive'
        return voice, tense

    def induce(self, root, head_label, id2alignment, id2subtree, id2rule, id2adjtree={}):
        def get_children_labels():
            labels = []
            for edge in self.tree[root]:
                if self.nodes[edge]['label'] > -1:
                    labels.append(self.nodes[edge]['label'])
            return labels

        # TO DO: refactor this function
        def update_rule(root, label, should_label=True):
            if should_label:
                self.nodes[root]['label'] = label

                id2subtree[label]['root'] = root
                rule_name = id2alignment[self.nodes[root]['label']]['edges'][0][0]+'/'+self.nodes[root]['name']
                id2rule[self.nodes[root]['label']] = rule_name

            if root not in id2subtree[label]['nodes']:
                id2subtree[label]['nodes'][root] = copy.copy(self.nodes[root])
                id2subtree[label]['tree'][root] = copy.copy(self.tree[root])

            for edge in self.tree[root]:
                update_rule(edge, label, False)
                del self.nodes[edge]
                del self.tree[edge]
            self.tree[root] = []

        def create_adjoining(head, id2adjtree):
            def create(root, adj_edge, adjtree):
                adjtree['nodes'][root] = copy.copy(self.nodes[root])
                adjtree['tree'][root] = []
                for edge in self.tree[root]:
                    adjtree['tree'][root].append(edge)
                    if edge != adj_edge:
                        adjtree = create(edge, adj_edge, adjtree)
                    else:
                        adjtree['nodes'][edge] = copy.copy(self.nodes[edge])
                        adjtree['nodes'][edge]['name'] += '*'
                        adjtree['tree'][edge] = []
                del self.nodes[root]
                del self.tree[root]
                return adjtree

            isAdjoined = False
            for edge in self.tree[root]:
                if self.nodes[root]['name'] == self.nodes[edge]['name']:
                    parent = self.nodes[root]['parent']

                    adjtree = {'nodes':{}, 'tree':{}, 'root':root}
                    adjtree = create(root, edge, adjtree)

                    if head not in id2adjtree:
                        id2adjtree[head] = []
                    id2adjtree[head].append(adjtree)

                    self.tree[parent][self.tree[parent].index(root)] = edge
                    isAdjoined = True
                    break
            return id2adjtree, isAdjoined

        def get_head(root, labels):
            # preference for root_label: always get the head of the sentence
            preference = self.nodes[root]['name'][0]
            if preference == 'S':
                preference = 'V'
            elif preference == 'A':
                preference = 'J'

            head = -1
            if head_label in set(labels):
                head = head_label
            else:
                for edge in self.tree[root]:
                    if self.nodes[edge]['name'][0] == preference:
                        head = self.nodes[edge]['label']
            return head

        def get_verb_info(root, label):
            # Extract verb information
            id2subtree[label]['info']['type'] = 'verb'
            id2subtree[label]['info']['pos'].insert(0, self.nodes[root]['name'])
            id2subtree[label]['info']['tokens'].insert(0, self.nodes[root]['lexicon'])

            if len(self.nodes[root]['name']) == 3:
                self.nodes[root]['name'] = self.nodes[root]['name'][:-1]
            self.nodes[root]['lexicon'] = self.info['lemmas'][self.info['tokens'].index(self.nodes[root]['lexicon'])]
            id2subtree[label]['info']['lemmas'].insert(0, self.nodes[root]['lexicon'])

            return id2subtree[label]['info']

        self.nodes[root]['label'] = -1
        if self.nodes[root]['type'] == 'terminal':
            for label in id2alignment:
                if self.nodes[root]['value'] in id2alignment[label]['tokens']:
                    if 'VB' in self.nodes[root]['name'] or self.nodes[root]['name'] == 'MD':
                        id2subtree[label]['info'] = get_verb_info(root, label)

                    update_rule(root, label)
                    break
        else:
            for edge in self.tree[root]:
                id2subtree, id2rule, id2adjtree = self.induce(edge, head_label, id2alignment, id2subtree, id2rule, id2adjtree)

            # Get children labels (except non-label nodes: -1)
            labels = get_children_labels()

            # If the node is the root of the tree
            if root == 1:
                update_rule(root, head_label)
            elif len(set(labels)) == 1 and labels[0] > -1:
                # Extract tense of the verb in case of a verb phrase
                if self.nodes[root]['name'] == 'VP':
                    for edge in self.tree[root]:
                        if ('VB' in self.nodes[edge]['name'] or self.nodes[edge]['name'] == 'MD') and self.nodes[edge]['type'] == 'terminal' and self.nodes[edge]['label'] == -1:
                            id2subtree[labels[0]]['info'] = get_verb_info(edge, labels[0])
                            break

                # Extract adjoining rules
                id2adjtree, isAdjoined = create_adjoining(labels[0], id2adjtree)

                if not isAdjoined:
                    label = labels[0]
                    update_rule(root, label)
            elif len(set(labels)) > 1:
                # Find the head of the subtree (the most right element from a specific type)
                head = get_head(root, labels)

                for edge in self.tree[root]:
                    if self.nodes[edge]['label'] not in [-1, head]:
                        rule_name = id2alignment[self.nodes[edge]['label']]['edges'][0][0]+'/'+self.nodes[edge]['name']
                        id2rule[self.nodes[edge]['label']] = rule_name

                        self.nodes[self._id] = {'name': rule_name, 'parent': root, 'type':'rule', 'label':-1}
                        self.tree[self._id] = []
                        self.tree[root][self.tree[root].index(edge)] = self._id
                        del self.nodes[edge]
                        del self.tree[edge]
                        self._id = self._id + 1

                if head > -1:
                    # Extract tense of the verb in case of a verb phrase
                    if self.nodes[root]['name'] == 'VP':
                        for edge in self.tree[root]:
                            if ('VB' in self.nodes[edge]['name'] or self.nodes[edge]['name'] == 'MD') and self.nodes[edge]['type'] == 'terminal' and self.nodes[edge]['label'] == -1:
                                id2subtree[head]['info'] = get_verb_info(edge, head)
                                break

                    # Extract adjoining rules
                    id2adjtree, isAdjoined = create_adjoining(head, id2adjtree)

                    if not isAdjoined:
                        update_rule(root, head)

        return id2subtree, id2rule, id2adjtree

    def print_tree(self, root, nodes, tree, printed):
        if nodes[root]['type'] == 'nonterminal':
            printed = printed + ' (' + nodes[root]['name']

            for node in tree[root]:
                printed = self.print_tree(node, nodes, tree, printed)
        elif nodes[root]['type'] == 'terminal':
            if nodes[root]['label'] > -1:
                lexicon = 'XXX'
            else:
                lexicon = nodes[root]['lexicon']
            printed = printed + ' (' + nodes[root]['name'] + ' ' + lexicon
        else:
            printed = printed + ' (' + nodes[root]['name']

        printed = printed + ')'
        return printed.strip()

    def prettify(self, id2subtree, id2rule, id2adjtree, tag={'initial':{}, 'substitution':{}, 'adjoining':{}}, ltag={'initial':{}, 'substitution':{}, 'adjoining':{}}):
        def get_head():
            head = '['
            for h in id2subtree[_id]['head']:
                head = head + h + ', '
            head = head[:-2]
            if head != '':
                head = head + ']'
            return head

        # lexicalized and delexicalized tag
        # Initial and substitution rules
        for _id in id2subtree:
            rule = id2rule[_id]

            _type = 'substitution'
            if rule == ':root/ROOT':
                _type = 'initial'

            head = get_head()
            if id2subtree[_id]['info']['type'] == 'verb':
                voice, tense = id2subtree[_id]['info']['voice'], id2subtree[_id]['info']['tense']
                lexical_id = (rule, head, voice, tense)
            else:
                lexical_id = (rule, head)

            if lexical_id not in ltag[_type]:
                ltag[_type][lexical_id] = []
            if rule not in tag[_type]:
                tag[_type][rule] = []

            if id2subtree[_id]['root'] == '':
                tag[_type][rule].append('empty')
                ltag[_type][lexical_id].append('empty')
            else:
                tree = self.print_tree(id2subtree[_id]['root'], id2subtree[_id]['nodes'], id2subtree[_id]['tree'], '')
                tag[_type][rule].append(tree)
                ltag[_type][lexical_id].append(tree)

        # Adjoining rules
        for _id in id2adjtree:
            head = get_head()

            rule = id2rule[_id]

            if id2subtree[_id]['info']['type'] == 'verb':
                voice, tense = id2subtree[_id]['info']['voice'], id2subtree[_id]['info']['tense']
                lexical_id = (rule, head, voice, tense)
            else:
                lexical_id = (rule, head)

            if lexical_id not in ltag['adjoining']:
                ltag['adjoining'][lexical_id] = []
            if rule not in tag['adjoining']:
                tag['adjoining'][rule] = []

            for tree in id2adjtree[_id]:
                pretty_tree = self.print_tree(tree['root'], tree['nodes'], tree['tree'], '')
                tag['adjoining'][rule].append(pretty_tree)
                ltag['adjoining'][lexical_id].append(pretty_tree)

        return tag, ltag

    def run(self):
        self.nodes, self.tree, self._id = self.parse_tree()

        id2alignment, id2subtrees = self.get_rules()

        root = filter(lambda x: self.nodes[x]['name'] == 'ROOT', self.nodes)[0]
        head_label = ''
        for _id in id2alignment:
            if len(filter(lambda x: x[0] == ':root', id2alignment[_id]['edges'])) > 0:
                head_label = _id
                break

        id2subtrees, id2rule, adjtrees = self.induce(root, head_label, id2alignment, id2subtrees, {}, {})

        for _id in id2subtrees:
            if _id not in id2rule:
                rule_name = id2alignment[_id]['edges'][0][0]+'/'+'E'
                id2rule[_id] = rule_name
            if id2subtrees[_id]['info']['type'] == 'verb':
                voice, tense = self.get_verb_tense(id2subtrees[_id]['info']['pos'], id2subtrees[_id]['info']['lemmas'])
                id2subtrees[_id]['info']['voice'] = voice
                id2subtrees[_id]['info']['tense'] = tense

        return id2subtrees, id2rule, adjtrees
__author__ = 'thiagocastroferreira'

"""
Author: Thiago Castro Ferreira
Date: 31/10/2016
Description:
    This script aims to extract the rules of our Synchronized Grammar
"""

import copy
import re

from main.aligners.Features import NounPhrase, VerbPhrase
from main.grammars.TAG import Tree, TAGNode, TAGRule

class TAGSynchAligner(object):
    def __init__(self, text, amr, info, alignments):
        self.text = text
        self.tokens = text.split()
        self.amr = amr
        self.string_tree = info['parse']
        self.alignments = alignments
        self.info = info

        self.info['tokens'] = map(lambda x: x.lower(), self.info['tokens'])

    def set_tree_rules(self):
        for rule_id in self.alignments.erg_rules:
            # Initializing subtrees with their heads
            self.alignments.tag_rules[rule_id] = TAGRule(tree=Tree(nodes={}, edges={}, root=1),
                                                         head=self.alignments.erg_rules[rule_id].head,
                                                         name=self.alignments.erg_rules[rule_id].name,
                                                         rules=[],
                                                         parent=self.alignments.erg_rules[rule_id].parent,
                                                         type='substitution')
            self.alignments.features[rule_id] = None

    # TO DO: treat modals would, should, might to, must, etc.
    def get_verb_tense(self, features):
        pos, lemmas = features.pos, features.lemmas
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

        features.voice = voice
        features.tense = tense
        return features

    def get_verb_info(self, root, rule_id):
        # Extract verb information
        if self.alignments.features[rule_id] == None:
            self.alignments.features[rule_id] = VerbPhrase(type='verb', pos=[], tokens=[], lemmas=[], voice='', tense='')
        feature = self.alignments.features[rule_id]

        feature.pos.insert(0, self.tree.nodes[root].name)
        feature.tokens.insert(0, self.tree.nodes[root].lexicon)

        if len(self.tree.nodes[root].name) == 3:
            self.tree.nodes[root].name = self.tree.nodes[root].name[:-1]
        index = self.info['tokens'].index(self.tree.nodes[root].lexicon)
        self.tree.nodes[root].lexicon = self.info['lemmas'][index]
        feature.lemmas.insert(0, self.tree.nodes[root].lexicon)

    def get_noun_info(self, root, rule_id):
        def check_terminal(node):
            if self.tree.nodes[node].name == 'NN':
                feature.form = 'description'
                feature.number = 'singular'
            elif self.tree.nodes[node].name == 'NNS':
                feature.form = 'description'
                feature.number = 'plural'
                self.tree.nodes[node].name = self.tree.nodes[node].name[:-1]
            elif self.tree.nodes[node].name == 'NNP':
                feature.form = 'proper'
                feature.number = 'singular'
                self.tree.nodes[node].name = self.tree.nodes[node].name[:-1]
            elif self.tree.nodes[node].name == 'NNPS':
                feature.form = 'proper'
                feature.number = 'plural'
                self.tree.nodes[node].name = self.tree.nodes[node].name[:-2]
            elif self.tree.nodes[node].name == 'PRP':
                feature.form = 'pronoun'

                if self.tree.nodes[node].lexicon in ['i', 'you', 'he', 'she', 'it', 'me', 'him', 'her']:
                    feature.number = 'singular'
                elif self.tree.nodes[node].lexicon in ['we', 'they', 'us', 'them']:
                    feature.number = 'plural'
            elif self.tree.nodes[node].name == 'PRP$':
                feature.form = 'possessive pronoun'

                if self.tree.nodes[node].lexicon in ['my', 'your', 'his', 'her', 'its', 'mine', 'yours', 'hers']:
                    feature.number = 'singular'
                elif self.tree.nodes[node].lexicon in ['our', 'their', 'ours', 'theirs']:
                    feature.number = 'plural'
            elif self.tree.nodes[node].name == 'DT':
                if self.tree.nodes[node].lexicon in ['this', 'that']:
                    feature.form = 'demonstrative'
                    feature.number = 'singular'
                elif self.tree.nodes[node].lexicon in ['these', 'those']:
                    feature.form = 'demonstrative'
                    feature.number = 'plural'
            elif self.tree.nodes[node].name in ['CC', ',']:
                feature.form = 'list'
                feature.number = 'plural'

        if self.alignments.features[rule_id] == None:
            self.alignments.features[rule_id] = NounPhrase(type='noun', pos=[], tokens=[], lemmas=[], form='', number='', inPP=False)
        feature = self.alignments.features[rule_id]

        if self.tree.nodes[root].type == 'terminal':
            check_terminal(root)
        else:
            parent = self.tree.nodes[root].parent
            if self.tree.nodes[parent].name == 'PP':
                feature.inPP = True

    def update_rule_tree(self, root, rule_id, should_label=True):
        erg_rule = self.alignments.erg_rules[rule_id]
        tag_rule = self.alignments.tag_rules[rule_id]

        if should_label:
            self.tree.nodes[root].label = rule_id

            tag_rule.tree.root = root

            graph_root = erg_rule.graph.root
            graph_root_parent = erg_rule.graph.nodes[graph_root].parent

            # Determine rule name
            rule_name = graph_root_parent['edge']+'/'+self.tree.nodes[root].name
            self.alignments.id2rule[rule_id] = rule_name
            erg_rule.name = rule_name
            tag_rule.name = rule_name

        if root not in self.alignments.tag_rules[rule_id].tree.nodes:
            tag_rule.tree.nodes[root] = copy.copy(self.tree.nodes[root])
            tag_rule.tree.edges[root] = copy.copy(self.tree.edges[root])

        for edge in self.tree.edges[root]:
            self.update_rule_tree(edge, rule_id, False)
            del self.tree.nodes[edge]
            del self.tree.edges[edge]

        self.tree.edges[root] = []

    # TO DO: improve storage
    def create_adjoining(self, root, rule_id):
        def create(root, adj_edge, adjtree):
            adjtree.tree.nodes[root] = copy.copy(self.tree.nodes[root])
            adjtree.tree.edges[root] = []
            for edge in self.tree.edges[root]:
                adjtree.tree.edges[root].append(edge)

                if edge != adj_edge:
                    adjtree = create(edge, adj_edge, adjtree)
                else:
                    adjtree.tree.nodes[edge] = copy.copy(self.tree.nodes[edge])
                    adjtree.tree.nodes[edge].name += '*'
                    adjtree.tree.edges[edge] = []
            del self.tree.nodes[root]
            del self.tree.edges[root]
            return adjtree

        isAdjoined = False
        for edge in self.tree.edges[root]:
            if self.tree.nodes[root].name == self.tree.nodes[edge].name:
                parent = self.tree.nodes[root].parent

                adjtree = TAGRule(name='',
                                  head=self.alignments.erg_rules[rule_id].head,
                                  tree=Tree(root=root, nodes={}, edges={}),
                                  type='adjoining',
                                  rules=[],
                                  parent=self.alignments.erg_rules[rule_id].parent)
                adjtree = create(root, edge, adjtree)

                if rule_id not in self.alignments.adjoining_rules:
                    self.alignments.adjoining_rules[rule_id] = []
                self.alignments.adjoining_rules[rule_id].append(adjtree)

                self.tree.edges[parent][self.tree.edges[parent].index(root)] = edge
                isAdjoined = True
                break
        return isAdjoined

    def prune_tree(self, root, prune_node):
        # Get rule_id, its parent and graph root and its parent
        rule_id = self.tree.nodes[prune_node].label
        tag_rule = self.alignments.tag_rules[rule_id]
        erg_rule = self.alignments.erg_rules[rule_id]

        graph_root = erg_rule.graph.root
        graph_parent = erg_rule.graph.nodes[graph_root].parent
        rule_parent = erg_rule.parent

        tag_parent_rule = self.alignments.tag_rules[rule_parent]
        erg_parent_rule = self.alignments.erg_rules[rule_parent]

        # Update rule name
        rule_name = graph_parent['edge']+'/'+self.tree.nodes[prune_node].name
        self.alignments.id2rule[rule_id] = rule_name
        erg_rule.name = rule_name

        tag_rule.name = rule_name

        # Update graph parents with the new rule name
        external = filter(lambda external: graph_parent['edge'] in external, erg_parent_rule.rules[graph_parent['node']])[0]
        index = erg_parent_rule.rules[graph_parent['node']].index(external)
        erg_parent_rule.rules[graph_parent['node']][index] = rule_name

        external = filter(lambda external: graph_parent['edge'] in external.name, erg_parent_rule.graph.edges[graph_parent['node']])[0]
        external.name = rule_name

        # Update tree parents with the new rule name
        tag_parent_rule.rules.append(rule_name)

        # Create substitution subtree and prune the tree
        self.tree.nodes[self._id] = TAGNode(id=self._id, name=rule_name, parent=root, type='rule', label=-1, lexicon='', index=-1)
        self.tree.edges[self._id] = []
        self.tree.edges[root][self.tree.edges[root].index(prune_node)] = self._id
        del self.tree.nodes[prune_node]
        del self.tree.edges[prune_node]
        self._id = self._id + 1

    def align(self, root, head_rule):
        def get_children_labels():
            labels = []
            for edge in self.tree.edges[root]:
                if self.tree.nodes[edge].label > -1:
                    labels.append(self.tree.nodes[edge].label)
            return labels

        def get_head(root, labels):
            # preference for root_label: always get the head of the sentence
            preference = self.tree.nodes[root].name[0]
            if preference == 'S':
                preference = 'V'
            elif preference == 'A':
                preference = 'J'

            head = -1
            if head_rule in set(labels):
                head = head_rule
            else:
                for edge in self.tree.edges[root]:
                    if self.tree.nodes[edge].name[0] == preference:
                        head = self.tree.nodes[edge].label
            return head

        self.tree.nodes[root].label = -1
        if self.tree.nodes[root].type == 'terminal':
            for rule_id in self.alignments.erg_rules:
                if self.tree.nodes[root].index in self.alignments.erg_rules[rule_id].tokens:
                    parent = self.tree.nodes[root].parent
                    if 'VB' in self.tree.nodes[root].name or self.tree.nodes[root].name == 'MD':
                        self.get_verb_info(root, rule_id)
                    elif self.tree.nodes[parent].name == 'NP':
                        self.get_noun_info(root, rule_id)

                    self.update_rule_tree(root, rule_id)
                    break
        else:
            for edge in self.tree.edges[root]:
                self.align(edge, head_rule)

            # Get children labels (except non-label nodes: -1)
            labels = get_children_labels()

            # If the node is the root of the tree
            if root == 1:
                self.update_rule_tree(root, head_rule)
            elif len(set(labels)) == 1 and labels[0] > -1:
                # Extract tense of the verb in case of a verb phrase
                if self.tree.nodes[root].name == 'VP':
                    for edge in self.tree.edges[root]:
                        if ('VB' in self.tree.nodes[edge].name or self.tree.nodes[edge].name == 'MD') and self.tree.nodes[edge].type == 'terminal' and self.tree.nodes[edge].label == -1:
                            self.get_verb_info(edge, labels[0])
                            break
                elif self.tree.nodes[root].name == 'NP':
                    self.get_noun_info(root, labels[0])

                # Extract adjoining rules
                isAdjoined = self.create_adjoining(root, labels[0])

                if not isAdjoined:
                    label = labels[0]
                    self.update_rule_tree(root, label)
            elif len(set(labels)) > 1:
                # Find the head of the subtree (the most right element from a specific type)
                head = get_head(root, labels)

                for edge in self.tree.edges[root]:
                    if self.tree.nodes[edge].label not in [-1, head]:
                        self.prune_tree(root, edge)

                if head > -1:
                    # Extract tense of the verb in case of a verb phrase
                    if self.tree.nodes[root].name == 'VP':
                        for edge in self.tree.edges[root]:
                            if ('VB' in self.tree.nodes[edge].name or self.tree.nodes[edge].name == 'MD') and self.tree.nodes[edge].type == 'terminal' and self.tree.nodes[edge].label == -1:
                                self.get_verb_info(edge, head)
                                break
                    elif self.tree.nodes[root].name == 'NP':
                        self.get_noun_info(root, head)

                    # Extract adjoining rules
                    isAdjoined = self.create_adjoining(root, head)
                    if not isAdjoined:
                        self.update_rule_tree(root, head)

    def run(self):
        # Check if it is multi-sentence
        regex = re.compile('ROOT')
        aux = regex.findall(self.string_tree)
        if len(aux) > 1:
            self.string_tree = '(MULTI-SENTENCE ' +self.string_tree + ')'

        self.tree = Tree(nodes={}, edges={}, root=1)
        self.tree.parse(self.string_tree)

        self._id = max(self.tree.nodes) + 1

        head_label = ''
        for rule_id in self.alignments.erg_rules:
            if self.alignments.erg_rules[rule_id].name == ':root':
                head_label = rule_id
                break

        self.set_tree_rules()
        self.align(1, head_label)

        for rule_id in self.alignments.erg_rules:
            # Empty references
            if rule_id not in self.alignments.id2rule:
                tag_rule = self.alignments.tag_rules[rule_id]
                erg_rule = self.alignments.erg_rules[rule_id]

                graph_root = erg_rule.graph.root
                graph_parent = erg_rule.graph.nodes[graph_root].parent
                rule_parent = erg_rule.parent

                tag_parent_rule = self.alignments.tag_rules[rule_parent]
                erg_parent_rule = self.alignments.erg_rules[rule_parent]

                rule_name = graph_parent['edge']+'/'+'E'
                erg_rule.name = rule_name

                tag_rule.name = rule_name
                tag_rule.parent = rule_parent
                self.alignments.id2rule[rule_id] = rule_name

                # Update graph parents with the new rule name
                external = filter(lambda external: graph_parent['edge'] in external, erg_parent_rule.rules[graph_parent['node']])[0]
                index = erg_parent_rule.rules[graph_parent['node']].index(external)
                erg_parent_rule.rules[graph_parent['node']][index] = rule_name

                external = filter(lambda external: graph_parent['edge'] in external.name, erg_parent_rule.graph.edges[graph_parent['node']])[0]
                external.name = rule_name

                # Update tree parents with the new rule name
                tag_parent_rule.rules.append(rule_name)

            # Get verb tense
            feature = self.alignments.features[rule_id]
            if feature != None and feature.type == 'verb':
                self.alignments.features[rule_id] = self.get_verb_tense(self.alignments.features[rule_id])

        return self.alignments
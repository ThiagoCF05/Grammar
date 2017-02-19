__author__ = 'thiagocastroferreira'

"""
Author: Thiago Castro Ferreira
Date: 31/10/2016
Description:
    This script aims to extract the rules of our Synchronized Grammar
"""

import copy
import re

from main.aligners.Features import Lexicon
import main.generator.REG as REG
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

    def init_lexicons(self, tree):
        terminals = tree.get_nodes_by(type='terminal', root=tree.root, nodes=[])
        terminals.sort(key=lambda x: tree.nodes[x].index)

        lexicons = []
        for i, terminal in enumerate(terminals):
            w_tm1 = '*'
            if i > 0:
                w_tm1 = tree.nodes[terminals[i-1]].lexicon

            lexicon = Lexicon(w_t=tree.nodes[terminal].lexicon,
                              w_tm1=w_tm1,
                              head='',
                              pos=tree.nodes[terminal].name,
                              edge='',
                              rule_id=-1,
                              index=tree.nodes[terminal].index)

            lexicons.append(lexicon)
        return lexicons

    def get_lexicon_information(self, root, rule_id):
        index = self.tree.nodes[root].index
        if index > 0:
            w_tm1 = self.info['lemmas'][index-1].lower()
        else:
            w_tm1 = '*'

        lexicon = Lexicon(w_t=self.tree.nodes[root].lexicon,
                          w_tm1=w_tm1,
                          head='',
                          pos=self.tree.nodes[root].name,
                          edge='',
                          rule_id=rule_id,
                          index=index)
        return lexicon

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

    def update_rule_tree(self, root, rule_id, should_label=True):
        erg_rule = self.alignments.erg_rules[rule_id]
        tag_rule = self.alignments.tag_rules[rule_id]

        self.tree.nodes[root].rule_id = rule_id

        graph_root = erg_rule.graph.root
        graph_root_parent = erg_rule.graph.nodes[graph_root].parent

        # Update lexicon information
        if self.tree.nodes[root].type == 'terminal':
            self.alignments.lexicons.append(self.get_lexicon_information(root, rule_id))

        if should_label:
            self.tree.nodes[root].label = rule_id

            tag_rule.tree.root = root

            # Determine rule name
            rule_name = graph_root_parent['edge']+'/'+self.tree.nodes[root].name+'~'+erg_rule.head
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
        rule_name = graph_parent['edge']+'/'+self.tree.nodes[prune_node].name+'~'+erg_rule.head
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
                label = labels[0]
                self.update_rule_tree(root, label)
            elif len(set(labels)) > 1:
                # Find the head of the subtree (the most right element from a specific type)
                head = get_head(root, labels)

                for edge in self.tree.edges[root]:
                    if self.tree.nodes[edge].label not in [-1, head]:
                        self.prune_tree(root, edge)

                if head > -1:
                    self.update_rule_tree(root, head)

    def linearization(self):
        rules = []
        rules_control = []
        for i, w in enumerate(self.info['tokens']):
            rule = filter(lambda rule_id: i in self.alignments.erg_rules[rule_id].tokens, self.alignments.erg_rules)

            if len(rule) > 0:
                rule_id = rule[0]
                rule = self.alignments.erg_rules[rule_id].name

                if rule not in rules_control:
                    rules_control.append(rule)
                    edge_pos, head = rule.split('~')
                    edge, pos = edge_pos.split('/')
                    # rules.extend(rule.split('~'))
                    rules.append(edge)

                    if 'name' in head:
                        head = REG.proper_name(self.alignments.erg_rules[rule_id])
                        head = '_'.join(head.split())
                    elif head == 'date-entity':
                        head = REG.date_entity(self.alignments.erg_rules[rule_id])
                        head = '_'.join(head.split())
                    elif head == 'have-org-role-91' or head == 'have-rel-role-91':
                        head = REG.have_role(self.alignments.erg_rules[rule_id])
                    rules.append(head)

        return self.info['tokens'], rules

    def run(self):
        # Check if it is multi-sentence
        regex = re.compile('ROOT')
        aux = regex.findall(self.string_tree)
        if len(aux) > 1:
            self.string_tree = '(MULTI-SENTENCE ' +self.string_tree + ')'

        self.tree = Tree(nodes={}, edges={}, root=1)
        self.tree.parse(self.string_tree)

        # Initialize lexicons
        self.alignments.lexicons = []

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

                rule_name = graph_parent['edge']+'/'+'E~'+erg_rule.head
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

            # self.alignments.erg_rules[rule_id].tokens = map(lambda x: self.info['lemmas'][x], self.alignments.erg_rules[rule_id].tokens)

        return self.alignments
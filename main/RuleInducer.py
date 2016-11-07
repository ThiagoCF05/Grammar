__author__ = 'thiagocastroferreira'

"""
Author: Thiago Castro Ferreira
Date: 31/10/2016
Description:
    This script aims to extract the rules of our Lexicalized Tree Adjoining Grammar
"""

import copy

class RuleInducer(object):
    def __init__(self, text, amr, tree, alignments):
        self.text = text
        self.tokens = text.split()
        self.amr = amr
        self.tree = tree
        self.alignments = alignments

    def get_rules(self):
        rule_id = 1
        id2alignment, id2subtrees = {}, {}
        for i, align in enumerate(self.alignments):
            id2alignment[rule_id] = align

            # Initializing subtrees with their heads
            id2subtrees[rule_id] = {'tree':{}, 'nodes':{}, 'head':[], 'root':''}
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

    def induce(self, root, head_label, id2alignment, id2subtrees, id2rule):
        def get_children_labels():
            labels = []
            for edge in self.tree[root]:
                if self.nodes[edge]['label'] > -1:
                    labels.append(self.nodes[edge]['label'])
            return labels

        # CREATE A NON-LEXICALIZED RULE
        def create_rule(root, label, new_label, should_label=True):

            if should_label:
                self.nodes[root]['label'] = label

            if root not in id2subtrees[label]['nodes']:
                id2subtrees[new_label]['nodes'][root] = copy.copy(self.nodes[root])
                id2subtrees[new_label]['tree'][root] = copy.copy(self.tree[root])

            for edge in self.tree[root]:
                create_rule(edge, label, new_label, False)
                del self.nodes[edge]
                del self.tree[edge]
            self.tree[root] = []

            if should_label:
                id2subtrees[new_label]['root'] = root
                rule_name = id2alignment[label]['edges'][0][0]+'/'+self.nodes[root]['name']
                id2rule[new_label] = rule_name

        # TO DO: refactor this function
        def update_rule(root, label, should_label=True):
            if should_label:
                self.nodes[root]['label'] = label

            if root not in id2subtrees[label]['nodes']:
                id2subtrees[label]['nodes'][root] = copy.copy(self.nodes[root])
                id2subtrees[label]['tree'][root] = copy.copy(self.tree[root])

            for edge in self.tree[root]:
                update_rule(edge, label, False)
                del self.nodes[edge]
                del self.tree[edge]
            self.tree[root] = []

            if should_label:
                id2subtrees[label]['root'] = root
                rule_name = id2alignment[self.nodes[root]['label']]['edges'][0][0]+'/'+self.nodes[root]['name']
                id2rule[self.nodes[root]['label']] = rule_name

        self.nodes[root]['label'] = -1
        if self.nodes[root]['type'] == 'terminal':
            for label in id2alignment:
                if self.nodes[root]['value'] in id2alignment[label]['tokens']:
                    update_rule(root, label)
                    break
        else:
            for edge in self.tree[root]:
                id2subtrees, id2rule = self.induce(edge, head_label, id2alignment, id2subtrees, id2rule)

                # ADJOINING RULE
                if self.nodes[root]['name'] == self.nodes[edge]['name']:
                    pass

            # Get children labels (except non-label nodes: -1)
            labels = get_children_labels()

            if len(set(labels)) == 1 and labels[0] not in [-1, head_label]:
                label = labels[0]
                update_rule(root, label)
            elif len(set(labels)) > 1:
                # preference for root_label: always get the head of the sentence
                preference = self.nodes[root]['name'][0]
                if preference == 'S':
                    preference = 'V'
                elif preference == 'A':
                    preference = 'J'

                # Find the head of the subtree (the most right element from a specific type)
                head = -1
                for edge in self.tree[root]:
                    if self.nodes[edge]['name'][0] == preference:
                        head = self.nodes[edge]['label']

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
                    update_rule(root, head)
                else:
                    new_label = max(id2subtrees.keys()) + 1
                    id2subtrees[new_label] = {'tree':{}, 'nodes':{}, 'head':[], 'root':''}
                    create_rule(root, head_label, new_label)

        # If root node is the head of the sentence, extract initial tree
        # if root == 1:
        #     self.nodes[root]['label'] = head_label
        #
        #     rule_name = id2alignment[head_label]['edges'][0][0]+'/'+self.nodes[root]['name']
        #     id2rule[head_label] = rule_name
        #
        #     id2subtrees[head_label]['root'] = root
        #     id2subtrees[head_label]['nodes'] = self.nodes
        #     id2subtrees[head_label]['tree'] = self.tree[root]

        return id2subtrees, id2rule

    def print_tree(self, root, nodes, tree, printed):
        if nodes[root]['type'] == 'nonterminal':
            printed = printed + '(' + nodes[root]['name'] + ' '

            for node in tree[root]:
                printed = self.print_tree(node, nodes, tree, printed)
        elif nodes[root]['type'] == 'terminal':
            if nodes[root]['label'] > -1:
                lexicon = 'XXX'
            else:
                lexicon = nodes[root]['lexicon']
            printed = printed + '(' + nodes[root]['name'] + ' ' + lexicon
        else:
            printed = printed + '(' + nodes[root]['name']


        printed = printed + ') '
        return printed

    def prettify(self, id2subtree, id2rule, tag, ltag):
        # lexicalized and delexicalized tag
        for _id in id2subtree:
            rule = id2rule[_id]

            head = '['
            for h in id2subtree[_id]['head']:
                head = head + h + ', '
            head = head[:-2] + ']'

            if (rule, head) not in ltag:
                ltag[(rule, head)] = []
            if rule not in tag:
                tag[rule] = []

            if id2subtree[_id]['root'] == '':
                tag[rule].append('empty')
                ltag[(rule, head)].append('empty')
            else:
                tree = self.print_tree(id2subtree[_id]['root'], id2subtree[_id]['nodes'], id2subtree[_id]['tree'], '')
                tag[rule].append(tree)
                ltag[(rule, head)].append(tree)
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

        id2subtrees, id2rule = self.induce(root, head_label, id2alignment, id2subtrees, {})

        for _id in id2subtrees:
            if _id not in id2rule:
                rule_name = id2alignment[_id]['edges'][0][0]+'/'+'E'
                id2rule[_id] = rule_name

        return id2subtrees, id2rule
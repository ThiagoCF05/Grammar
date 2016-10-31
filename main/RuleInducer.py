__author__ = 'thiagocastroferreira'

import copy

class RuleInducer(object):
    def __init__(self, text, amr, tree, alignment):
        self.text = text
        self.tokens = text.split()
        self.amr = amr
        self.tree = tree
        self.alignment = alignment

    def get_rules(self):
        rule_id = 1
        id2tokens, id2subtrees = {}, {}
        for align in self.alignment.split():
            tokens, subgraph = align.split('|')

            tokens = map(lambda x: int(x), tokens.split('-'))
            id2tokens[rule_id] = self.tokens[tokens[0]:tokens[1]]

            # TO DO: ...
            id2subtrees[rule_id] = {'tree':{}, 'nodes':{}}
            rule_id = rule_id + 1
        return id2tokens, id2subtrees

    def parse_tree(self):
        nodes = {}
        tree = {}

        _id = 1
        prev_id = 0

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
                nodes[prev_id]['value'] = terminal
                nodes[prev_id]['type'] = 'terminal'

                for i in xrange(len(closing)):
                    prev_id = nodes[prev_id]['parent']
        return nodes, tree, _id

    def induce(self, root, nodes, tree, id2tokens, id2subtrees, _id):
        def get_children_labels():
            labels = []
            for edge in tree[root]:
                if nodes[edge]['label'] > -1:
                    labels.append(nodes[edge]['label'])
            return labels

        if nodes[root]['type'] == 'terminal':
            nodes[root]['label'] = -1
            for label in id2tokens:
                if nodes[root]['value'] in id2tokens[label]:
                    nodes[root]['label'] = label

                    id2subtrees[label]['nodes'][root] = copy.copy(nodes[root])
                    id2subtrees[label]['tree'][root] = []
                    break
        else:
            for edge in tree[root]:
                nodes, tree, id2subtrees, _id = self.induce(edge, nodes, tree, id2tokens, id2subtrees, _id)

            # Get children labels (except non-label nodes: -1)
            labels = get_children_labels()

            if len(set(labels)) == 1:
                label = labels[0]
                nodes[root]['label'] = label
                id2subtrees[label]['nodes'][root] = copy.copy(nodes[root])
                id2subtrees[label]['tree'][root] = copy.copy(tree[root])

                for edge in tree[root]:
                    if edge not in id2subtrees[label]['nodes']:
                        id2subtrees[label]['nodes'][edge] = copy.copy(nodes[edge])
                        id2subtrees[label]['tree'][edge] = copy.copy(tree[edge])
                    del nodes[edge]
                    del tree[edge]
                tree[root] = []
            else:
                # preference for root_label: always get the head of the sentence
                preference = nodes[root]['name'][0]
                if preference == 'S':
                    preference = 'V'

                root_label = -1
                for edge in tree[root]:
                    if nodes[edge]['name'][0] != preference and nodes[edge]['label'] > -1:
                        nodes[_id] = {'name': str(nodes[edge]['label'])+'/'+nodes[edge]['name'], 'parent': root, 'type':'rule', 'label':-1}
                        tree[_id] = []
                        tree[root][tree[root].index(edge)] = _id
                        del nodes[edge]
                        del tree[edge]
                        _id = _id + 1
                    else:
                        if nodes[edge]['label'] != -1:
                            root_label = nodes[edge]['label']

                nodes[root]['label'] = root_label
                id2subtrees[root_label]['nodes'][root] = copy.copy(nodes[root])
                id2subtrees[root_label]['tree'][root] = copy.copy(tree[root])

                for edge in tree[root]:
                    if edge not in id2subtrees[root_label]['nodes']:
                        id2subtrees[root_label]['nodes'][edge] = copy.copy(nodes[edge])
                        id2subtrees[root_label]['tree'][edge] = copy.copy(tree[edge])
                    del nodes[edge]
                    del tree[edge]
                tree[root] = []

        return nodes, tree, id2subtrees, _id

    def run(self):
        nodes, tree, _id = self.parse_tree()

        id2tokens, id2subtrees = self.get_rules()

        root = filter(lambda x: nodes[x]['name'] == 'ROOT', nodes)[0]
        nodes, tree, id2subtrees, _id = self.induce(root, nodes, tree, id2tokens, id2subtrees, _id)

        return id2subtrees
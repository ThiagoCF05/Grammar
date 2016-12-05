__author__ = 'thiagocastroferreira'

import copy

class TAGNode(object):
    def __init__(self, id=0, name='', parent=0, type='', lexicon='', index=-1, label=-1):
        self.id = id
        self.name = name
        self.parent = parent
        self.type = type
        self.index = index
        self.lexicon = lexicon
        self.label = label

class Tree(object):
    def __init__(self, nodes={}, edges={}, root=1):
        self.nodes = nodes
        self.edges = edges
        self.root = root

    def parse(self, tree):
        node_id = 1
        prev_id = 0
        terminal_id = 0

        for child in tree.replace('\n', '').split():
            closing = filter(lambda x: x == ')', child)
            if child[0] == '(':
                if len(closing) > 0:
                    node = TAGNode(id=node_id, name=child[1:-len(closing)], parent=prev_id, type='rule')
                else:
                    node = TAGNode(id=node_id, name=child[1:], parent=prev_id, type='nonterminal')
                self.nodes[node_id] = node
                self.edges[node_id] = []

                if prev_id > 0:
                    self.edges[prev_id].append(node_id)
                prev_id = copy.copy(node_id)
                node_id = node_id + 1
            else:
                terminal = child.replace(closing, '')

                self.nodes[prev_id].index = terminal_id
                # Abstract punctuation
                if self.nodes[prev_id].name == '.':
                    self.nodes[prev_id].lexicon = '.'
                elif self.nodes[prev_id].name == ':':
                    self.nodes[prev_id].lexicon = ':'
                else:
                    self.nodes[prev_id].lexicon = terminal.lower()
                self.nodes[prev_id].type = 'terminal'

                terminal_id = terminal_id + 1

            for i in xrange(len(closing)):
                prev_id = self.nodes[prev_id].parent

    def prettify(self, root):
        def print_tree(root, tree):
            if self.nodes[root].type == 'nonterminal':
                tree = tree + ' (' + self.nodes[root].name

                for node in self.edges[root]:
                    tree = print_tree(node, tree)
            elif self.nodes[root].type == 'terminal':
                if self.nodes[root].label > -1:
                    lexicon = 'XXX'
                else:
                    lexicon = self.nodes[root].lexicon
                tree = tree + ' (' + self.nodes[root].name + ' ' + lexicon
            else:
                tree = tree + ' (' + self.nodes[root].name

            tree = tree + ')'
            return tree.strip()

        return print_tree(root, '')

class TAGRule(object):
    def __init__(self, name='', parent='', head='', tree=Tree, type='initial', rules=[]):
        self.name = name
        self.parent = parent
        self.head = head
        self.tree = tree
        self.type = type
        self.rules = rules

class TAG(object):
    def __init__(self, rules={}, start=''):
        self.rules = rules
        self.start = start
        self.count = 0
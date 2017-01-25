__author__ = 'thiagocastroferreira'

import copy

class TAGNode(object):
    def __init__(self, id=0, name='', parent=0, type='', lexicon='', index=-1, label=-1, rule_id=-1):
        self.id = id
        self.name = name
        self.parent = parent
        self.type = type
        self.index = index
        self.lexicon = lexicon
        # rule_id and label are the same thing, but they are used in different conditions
        # Label sets only the head of the rule
        self.label = label
        self.rule_id = rule_id

class Tree(object):
    def __init__(self, nodes={}, edges={}, root=1):
        self.nodes = nodes
        self.edges = edges
        self.root = root

    def get_rules(self, root=1, rules=[]):
        if self.nodes[root].type == 'rule':
            rules.append(self.nodes[root].id)

        for node in self.edges[root]:
            rules = self.get_rules(node, rules)

        return rules

    def get_nodes_by(self, type='rule', root=1, nodes=[]):
        if self.nodes[root].type == type:
            nodes.append(self.nodes[root].id)

        for node in self.edges[root]:
            nodes = self.get_nodes_by(type=type, root=node, nodes=nodes)

        return nodes

    def check_validity(self):
        isValid = True

        for node in self.edges:
            if len(self.edges[node]) == 0:
                if self.nodes[node].type == 'nonterminal':
                    isValid = False
                    break

        return isValid

    # insert subtree
    def insert(self, node_id, subtree):
        _id = max(self.nodes.keys())+1
        subtree.root = _id

        oldid2id = {}

        for node in subtree.nodes:
            oldid2id[node] = _id
            self.nodes[_id] = copy.copy(subtree.nodes[node])
            self.nodes[_id].id = _id
            _id = _id + 1

        for node in subtree.edges:
            self.edges[oldid2id[node]] = map(lambda edge: oldid2id[edge], subtree.edges[node])

            if node != 1:
                parent = self.nodes[oldid2id[node]].parent
                self.nodes[oldid2id[node]].parent = oldid2id[parent]

        parent = self.nodes[node_id].parent
        index = self.edges[parent].index(node_id)
        self.edges[parent][index] = subtree.root
        self.nodes[subtree.root].parent = parent
        del self.nodes[node_id]
        del self.edges[node_id]

        return subtree.root

    def parse(self, tree):
        node_id = 1
        prev_id = 0
        terminal_id = 0

        for child in tree.replace('\n', '').split():
            closing = filter(lambda x: x == ')', child)
            if child[0] == '(':
                if len(closing) > 0:
                    node = TAGNode(id=node_id, name=child[1:-len(closing)], parent=prev_id, type='rule', rule_id=-1)
                else:
                    node = TAGNode(id=node_id, name=child[1:], parent=prev_id, type='nonterminal', rule_id=-1)
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

                # Set the label of the rules (> -1)
                if self.nodes[prev_id].lexicon == 'xxx':
                    self.nodes[prev_id].label = 1

                terminal_id = terminal_id + 1

            for i in xrange(len(closing)):
                prev_id = self.nodes[prev_id].parent

    def prettify(self, root, isRule=True):
        def print_tree(root, tree):
            if self.nodes[root].type == 'nonterminal':
                tree = tree + ' (' + self.nodes[root].name

                for node in self.edges[root]:
                    tree = print_tree(node, tree)
            elif self.nodes[root].type == 'terminal':
                if isRule:
                    if self.nodes[root].label > -1:
                        lexicon = 'xxx'
                    else:
                        lexicon = '-'
                else:
                    lexicon = self.nodes[root].lexicon
                tree = tree + ' (' + self.nodes[root].name + ' ' + lexicon
            else:
                tree = tree + ' (' + self.nodes[root].name

            tree = tree + ')'
            return tree.strip()

        return print_tree(root, '')

    def realize(self, root=1, text='', isRule=True):
        if self.nodes[root].type == 'terminal':
            if self.nodes[root].label > -1 and isRule:
                text = text + ' XXX-' + self.nodes[root].name
            elif self.nodes[root].name in [':', '.'] or self.nodes[root].lexicon in ['\'\'']:
                pass
            else:
                text = text + ' ' + self.nodes[root].lexicon
        elif self.nodes[root].type == 'rule':
            text = text + ' ' + self.nodes[root].name

        for node in self.edges[root]:
            text = self.realize(root=node, text=text)
        return text

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
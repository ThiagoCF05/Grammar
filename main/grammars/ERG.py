__author__ = 'thiagocastroferreira'

import copy

class AMREdge(object):
    def __init__(self, name, node_id, isRule=False):
        self.name = name
        self.node_id = node_id
        self.isRule = isRule

class AMRNode(object):
    def __init__(self, id, name, parent, status, tokens):
        self.id = id
        self.name = name
        self.parent = parent
        self.status = status
        self.tokens = tokens

class AMR(object):
    def __init__(self, nodes={}, edges={}, root=''):
        self.nodes = nodes
        self.edges = edges
        self.root = root

    def parse(self, amr):
        self.edges['root'] = []

        node_id, edge, tokens = '', ':root', []
        parent = 'root'
        for instance in amr.replace('/', '').split():
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
                node_id = instance[1:]
            else:
                instance = instance.replace('\'', '').replace('\"', '').split('~e.')
                name = instance[0]
                if len(instance) > 1:
                    tokens.extend(map(lambda x: int(x), instance[1].split(',')))
                if node_id != '':
                    node = AMRNode(id=node_id, name=name, parent={'node':parent, 'edge':edge}, status='unlabeled', tokens=list(set(tokens)))
                    self.nodes[node_id] = node

                    self.edges[node_id] = []
                    _edge = AMREdge(name=edge, node_id=node_id)
                    self.edges[parent].append(_edge)

                    parent = node_id
                else:
                    if edge not in [':wiki', ':mode']:
                        _node = copy.copy(name)
                        i, isCoref = 1, False
                        while _node in self.nodes.keys():
                            _node = name + '-coref' + str(i)
                            isCoref = True
                            i = i + 1
                        if isCoref:
                            name = self.nodes[name].name
                        node = AMRNode(id=_node, name=name, parent={'node':parent, 'edge':edge}, status='unlabeled', tokens=list(set(tokens)))
                        self.nodes[_node] = node

                        self.edges[_node] = []

                        _edge = AMREdge(name=edge, node_id=_node)
                        self.edges[parent].append(_edge)
                node_id, tokens = '', []

            for i in xrange(closing):
                parent = self.nodes[parent].parent['node']
        self.root = self.edges['root'][0].node_id

    def prettify(self, head='', root='', print_constants=True):
        def print_amr(root, head, amr, level):
            closing = False
            level = level + 1
            if root == self.nodes[root].name:
                if print_constants:
                    amr = amr + ' ' + self.nodes[root].name
                else:
                    amr = amr + ' ' + 'c'
            elif 'coref' in root:
                amr = amr + ' ' + 'coref'#root.split('-')[0]
            else:
                if self.nodes[root].name == head:
                    amr = amr + ' (XXX'
                else:
                    amr = amr + ' (' + root + ' / ' + self.nodes[root].name
                closing = True

            for edge in self.edges[root]:
                amr = amr + ' \n' + (level * '\t') + edge.name
                if not edge.isRule:
                    amr = print_amr(edge.node_id, head, amr, level)
                else:
                    amr = amr + ' -'
            if closing:
                amr = amr + ')'
            return amr.strip()

        if root == '':
            root = self.edges['root'][0].node_id
        return print_amr(root, head, '', 0)

class ERGRule(object):
    def __init__(self, name='', parent='', head='', graph=AMR, tokens=[], lemmas=[], rules={}):
        self.name = name
        self.parent = parent
        self.head = head
        self.graph = graph
        self.tokens = tokens
        self.lemmas = lemmas
        self.rules = rules

class ERG(object):
    def __init__(self, rules={}, start=''):
        self.rules = rules
        self.count = 0
        self.start = start

# if __name__ == '__main__':
#     amr = """(s / say-01
#                       :ARG0 (s2 / service
#                             :mod (e / emergency)
#                             :location (c / city :wiki 'London'
#                                   :name (n / name :op1 'London')))
#                       :ARG1 (s3 / send-01
#                             :ARG1 (p / person :quant 11)
#                             :ARG2 (h / hospital)
#                             :mod (a / altogether)
#                             :purpose (t / treat-03
#                                   :ARG1 p
#                                   :ARG2 (w / wound-01
#                                         :ARG1 p
#                                         :mod (m / minor)))))"""
#
#     a = AMR()
#     a.parse(amr)
#     print a.prettify()
__author__ = 'thiagocastroferreira'

import copy
import re

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

    def get_rules(self, root='', rules=[]):
        for edge in self.edges[root]:
            if edge.isRule:
                rules.append(edge.node_id)
            else:
                rules = self.get_rules(edge.node_id, rules)
        return rules

    def insert(self, subgraph):
        for node in subgraph.nodes:
            _id = subgraph.nodes[node].id
            self.nodes[_id] = subgraph.nodes[node]
            self.edges[_id] = subgraph.edges[node]

        if self.root == '':
            self.root = subgraph.root
        else:
            parent = subgraph.nodes[subgraph.root].parent

            for i, edge in enumerate(self.edges[parent['node']]):
                if edge.node_id == subgraph.root:
                    self.edges[parent['node']][i].isRule = False
                    break

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
                # instance = instance.split('~e.')
                edge = instance#[0]
                # if len(instance) > 1:
                #     tokens.extend(map(lambda x: int(x), instance[1].split(',')))
            elif instance[0] == '(':
                node_id = instance[1:]
            else:
                instance = instance.replace('\'', '').replace('\"', '')#.split('~e.')
                name = instance#[0]
                # if len(instance) > 1:
                #     tokens.extend(map(lambda x: int(x), instance[1].split(',')))
                if node_id != '':
                    node = AMRNode(id=node_id, name=name, parent={'node':parent, 'edge':edge}, status='unlabeled', tokens=list(set(tokens)))
                    self.nodes[node_id] = node

                    self.edges[node_id] = []
                    _edge = AMREdge(name=edge, node_id=node_id)
                    self.edges[parent].append(_edge)

                    parent = node_id
                else:
                    if edge not in [':wiki']:
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
                amr = amr + ' \n' + (level * '\t') + ' ' + edge.name
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
    def __init__(self, name='', parent='', head='', graph=None, tokens=[], lemmas=[], rules={}):
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

class ERGFactory(object):
    def __init__(self, verb2noun={}, noun2verb={}, verb2actor={}, actor2verb={}, sub2word={}):
        self.verb2noun = verb2noun
        self.noun2verb = noun2verb
        self.verb2actor = verb2actor
        self.actor2verb = actor2verb
        self.sub2word = sub2word

    def match_subgraph_patterns(self, root):
        # filter subgraphs with the root given as a parameter which the related word is in the sentence
        subgraphs = filter(lambda iter: iter[0] == self.amr.nodes[root].name, self.sub2word)

        if len(subgraphs) > 0:
            subgraphs = sorted(subgraphs, key=len)
            subgraphs.reverse()

            matched = True
            filtered_subgraph = [self.amr.nodes[root].name]
            tokens = []
            for sub in subgraphs:
                matched = True
                tokens = self.sub2word[sub]
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
                return filtered_subgraph, tokens
        return None, []

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

        node = self.amr.nodes[root]
        rule.graph.nodes[root] = AMRNode(id=node.id, name=node.name, parent=node.parent, status=node.status, tokens=node.tokens)

        rule.graph.edges[root] = []
        for edge in self.amr.edges[root]:
            rule.graph.edges[root].append(AMREdge(name=edge.name, node_id=edge.node_id, isRule=True))

            if root not in rule.rules:
                rule.rules[root] = []
            rule.rules[root].append(edge)

        return rule

    def create_subgraph_rule(self, root, edges, tokens):
        rule = self.create_rule(root)
        rule.tokens = tokens

        for edge in edges:
            if self.amr.nodes[edge.node_id].status == 'unlabeled':
                rule = self.create_rule(edge.node_id, rule)

                for _edge in rule.graph.edges[root]:
                    if _edge.name == edge.name:
                        if '-entity' not in self.amr.nodes[root].name and '-quantity' not in self.amr.nodes[root].name:
                            rule.head = rule.head + '/' + self.amr.nodes[edge.node_id].name
                        rule.rules[root] = filter(lambda x: x.name != _edge.name, rule.rules[root])
                        _edge.isRule = False
                        break

        if root in rule.rules and len(rule.rules[root]) == 0:
            del rule.rules[root]

        return rule

    def create_father(self, root, edge):
        self.amr.nodes[root].status = 'labeled'

        for rule_id in self.erg.rules:
            rule = self.erg.rules[rule_id]

            if rule.graph.root == edge.node_id:
                rule.name = self.amr.nodes[root].parent['edge']

                aux = rule.head.split('/')
                rule.head = self.amr.nodes[root].name + '/' + aux[0]

                rule.graph.root = root

                rule.graph.nodes[root] = copy.copy(self.amr.nodes[root])

                rule.graph.edges[root] = []
                for _edge in self.amr.edges[root]:
                    if _edge.name == edge.name:
                        rule.graph.edges[root].append(AMREdge(name=_edge.name, node_id=_edge.node_id, isRule=False))
                    else:
                        rule.graph.edges[root].append(AMREdge(name=_edge.name, node_id=_edge.node_id, isRule=True))
                        if root not in rule.rules:
                            rule.rules[root] = []
                        rule.rules[root].append(_edge)
                break

    def find_subgraphs(self, root, visited):
        visited.append(root)

        # Find entity and quantity nodes
        regex = re.compile("""(.+-entity)$|(.+-quantity)$""")

        if self.amr.nodes[root].status != 'labeled':
            # Find subgraph defined at verbalization-list, and have-org/rel
            subgraph, tokens = self.match_subgraph_patterns(root)
            if subgraph != None:
                # When there is no edges
                if len(subgraph) > 1:
                    rule = self.create_subgraph_rule(root, subgraph[1:], tokens)
                    self.erg.rules[self.erg.count] = rule
                    self.erg.count = self.erg.count + 1

        for i, edge in enumerate(self.amr.edges[root]):
            if edge.node_id not in visited:
                self.find_subgraphs(edge.node_id, visited)

            # MATCH parent of :degree non-matched
            if edge.name == ':degree' and len(self.amr.nodes[edge.node_id].tokens) == 0:
                rule = self.create_subgraph_rule(root, [edge], self.amr.nodes[root].tokens)
                self.erg.rules[self.erg.count] = rule
                self.erg.count = self.erg.count + 1

            # MATCH parent of :name
            if edge.name == ':name':
                self.create_father(root, edge)

            # MATCH reification
            elif self.amr.nodes[edge.node_id].name in ['have-rel-role-91', 'have-org-role-91'] and self.amr.nodes[root].status != 'labeled' and len(self.amr.nodes[root].tokens) == 0:
                self.create_father(root, edge)

        # MATCH NAME NODES
        if self.amr.nodes[root].name == 'name':
            rule = self.create_subgraph_rule(root, self.amr.edges[root], self.amr.nodes[root].tokens)
            self.erg.rules[self.erg.count] = rule
            self.erg.count = self.erg.count + 1
        # MATCH entity and quantity nodes
        elif regex.match(self.amr.nodes[root].name) != None:
            rule = self.create_subgraph_rule(root, self.amr.edges[root], self.amr.nodes[root].tokens)
            self.erg.rules[self.erg.count] = rule
            self.erg.count = self.erg.count + 1
        # MATCH org and rel roles
        elif self.amr.nodes[root].name in ['have-rel-role-91', 'have-org-role-91']:
            edges = filter(lambda edge: edge.name == ':ARG2', self.amr.edges[root])
            rule = self.create_subgraph_rule(root, edges, self.amr.nodes[root].tokens)
            self.erg.rules[self.erg.count] = rule
            self.erg.count = self.erg.count + 1

    def create_erg(self, amr):
        if type(amr) == str:
            self.amr = AMR(nodes={}, edges={}, root='')
            self.amr.parse(amr)
        else:
            self.amr = amr

        self.erg = ERG(rules={}, start='')
        self.find_subgraphs(self.amr.root, [])

        # Create rule for the unlabeled nodes
        for node in self.amr.nodes:
            if self.amr.nodes[node].status != 'labeled':
                rule = self.create_rule(node)
                self.erg.rules[self.erg.count] = rule
                self.erg.count = self.erg.count + 1

        # Set parent rule names
        for rule_id in self.erg.rules:
            graph = self.erg.rules[rule_id].graph
            root = graph.root
            parent = graph.nodes[root].parent

            for _id in self.erg.rules:
                if parent['node'] in self.erg.rules[_id].graph.nodes:
                    self.erg.rules[rule_id].parent = _id

                    for edge in self.erg.rules[_id].rules[parent['node']]:
                        if edge.name == parent['edge']:
                            edge.node_id = rule_id
                            break
                    break
        return self.erg

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
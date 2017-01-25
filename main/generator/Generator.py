__author__ = 'thiagocastroferreira'

from sys import path
path.append('/home/tcastrof/amr/scp_repo')
path.append('/home/tcastrof/amr/Grammar')
path.append('../../')

import copy
import cPickle as p
import main.utils as utils
import operator
import properties as prop

from main.aligners.Features import VerbPhrase
from main.grammars.ERG import AMR, ERGFactory
from Lexicalizer import Lexicalizer
from main.grammars.TAG import Tree
from main.grammars.SynchG import SynchG, SynchRule

class Candidate(object):
    def __init__(self, tree_rules, graph_rules, amr, tree, synchg, prob):
        self.tree_rules = tree_rules
        self.graph_rules = graph_rules
        self.amr = amr
        self.tree = tree
        self.synchg = synchg
        self.prob = prob

class Generator(object):
    def __init__(self, amr='', erg_factory=None, models=[], beam_n=20):
        self.grammar = {'initial':{}, 'substitution':{}}
        for fname in models:
            aux = fname.split('/')[-1].split('_')
            if aux[0] == 'initial':
                self.grammar['initial'][len(aux)-1] = p.load(open(fname))
            elif aux[0] == 'substitution':
                self.grammar['substitution'][len(aux)-1] = p.load(open(fname))

        self.lexicalizer = Lexicalizer()

        # Break the amr into subgraphs and create ERG
        erg = erg_factory.create_erg(amr=amr)
        self.init_synchg(erg)
        self.beam_n = beam_n

    def init_synchg(self, erg):
        self.synchg = SynchG(rules={}, start='', initial_rules=[], substitution_rules=[], adjoining_rules=[])
        self.synchg.count = erg.count

        for rule_id in erg.rules:
            synch_rule = SynchRule(name=erg.rules[rule_id].name,
                                   head=erg.rules[rule_id].head,
                                   parent=erg.rules[rule_id].parent,
                                   graph=erg.rules[rule_id].graph,
                                   graph_rules=erg.rules[rule_id].rules,
                                   tree=None,
                                   tree_rules=[],
                                   features=None,
                                   tokens=erg.rules[rule_id].tokens)
            self.synchg.rules[rule_id] = synch_rule

    def get_template(self, rule_id, synchg, tree_type):
        def filter_grammar(condition_level):
            rule = synchg.rules[rule_id]
            result = []

            if condition_level == 3:
                result = filter(lambda g: rule.name == g[1]
                                          and rule.head == g[3], self.grammar[tree_type][condition_level])
            elif condition_level == 2:
                result = filter(lambda g: rule.name == g[1], self.grammar[tree_type][condition_level])

            return result

        rule = synchg.rules[rule_id]
        condition_level = 2
        templates = []
        while condition_level > 1 and len(templates) == 0:
            # Get rules with the same income edge and head
            templates = filter_grammar(condition_level)

            # Test outcome edges condition
            if len(rule.graph_rules.keys()) == 0:
                templates = filter(lambda g: g[2] == 'empty', templates)
            else:
                graph_rules = map(lambda edge: edge.name, reduce(lambda x, y: x+y, rule.graph_rules.values()))
                templates = filter(lambda g: sorted(list(g[2])) == sorted(graph_rules), templates)

            if len(templates) == 0:
                condition_level = condition_level - 1

        dem = sum(map(lambda x: self.grammar[tree_type][condition_level][x], templates))
        templates = map(lambda x: (x[0], float(self.grammar[tree_type][condition_level][x])), templates)

        candidates = {}
        for template in templates:
            if template[0] not in candidates:
                candidates[template[0]] = 0.0
            candidates[template[0]] += template[1]

        candidates = map(lambda template: (template, candidates[template]/dem), candidates)
        return sorted(candidates, key=operator.itemgetter(1), reverse=True)

    # choose initial rule
    def choose_initial(self):
        # Generation process from the root rule
        start_rule = filter(lambda rule_id: ':root' in self.synchg.rules[rule_id].name, self.synchg.rules)[0]

        isSynchronous = True

        # Choose initial rule
        templates = self.get_template(start_rule, self.synchg, 'initial')[:self.beam_n]
        candidates = []

        if len(templates) == 0:
            isSynchronous = False
            return isSynchronous, candidates

        for template in templates:
            # Update synchronized rule with the predicted tree
            synchg = copy.deepcopy(self.synchg)
            rule = synchg.rules[start_rule]
            rule.update_tree(template[0][0])
            rule.features = VerbPhrase(voice=template[0][1])

            # Update the generated tree
            tree = template[0][0]
            tree = self.lexicalizer.choose_words(tree, rule)

            # Update the generated amr
            amr = AMR(nodes={}, edges={}, root='')
            amr.insert(rule.graph)

            # Get rules in the amr and in the template
            tree_rules = copy.copy(rule.tree_rules)
            graph_rules = amr.get_rules(root=amr.root, rules=[])

            candidate = Candidate(amr=amr, tree=tree, tree_rules=tree_rules, graph_rules=graph_rules, synchg=synchg, prob=template[1])
            candidates.append(candidate)

        return isSynchronous, candidates

    def choose_substitution(self, template):
        tree_rules = template.tree_rules
        graph_rules = template.graph_rules
        amr = template.amr
        tree = template.tree
        synchg = template.synchg
        prob = template.prob

        candidates = []

        # While the amr or the tree have rules...
        isSynchronous = False
        for graph_root in graph_rules:
            # Get the name of the rule
            graph_rule_id = filter(lambda rule: synchg.rules[rule].graph.root == graph_root, synchg.rules)[0]
            graph_rule_name = synchg.rules[graph_rule_id].name

            aux = tree.split()
            for tree_root in tree_rules:
                # Check if the rule edge is in the template rule
                if graph_rule_name == aux[tree_root]:
                    rule_id = graph_rule_id

                    new_templates = self.get_template(rule_id, synchg, 'substitution')[:self.beam_n]

                    if len(new_templates) > 0:
                        for new_template in new_templates:
                            new_synchg = copy.deepcopy(synchg)
                            new_amr = copy.deepcopy(amr)
                            new_tree = copy.deepcopy(tree)

                            rule = new_synchg.rules[rule_id]
                            rule.update_tree(new_template[0][0])
                            rule.features = VerbPhrase(voice=new_template[0][1])
                            new_amr.insert(rule.graph)

                            subtree = new_template[0][0]
                            subtree = self.lexicalizer.choose_words(subtree, rule)

                            new_tree = new_tree.split()
                            new_tree[tree_root] = subtree
                            new_tree = ' '.join(new_tree).replace('empty', '')

                            new_tree_rules = []
                            for i, token in enumerate(str(new_tree).split()):
                                if token[0] == ':' and len(token) > 1:
                                    new_tree_rules.append(i)
                            new_graph_rules = new_amr.get_rules(root=new_amr.root, rules=[])

                            candidate = Candidate(amr=new_amr,
                                                  tree=new_tree,
                                                  tree_rules=new_tree_rules,
                                                  graph_rules=new_graph_rules,
                                                  synchg=new_synchg,
                                                  prob=prob*new_template[1])
                            candidates.append(candidate)

                        isSynchronous = True

            if isSynchronous:
                break
        return isSynchronous, sorted(candidates, key=lambda x: x.prob, reverse=True)[:self.beam_n]

    def run(self):
        concluded, candidates, fails = [], [], []

        isSynchronous, templates = self.choose_initial()
        if isSynchronous:
            for candidate in templates:
                if len(candidate.tree_rules) == 0 and len(candidate.graph_rules) == 0:
                    concluded.append(candidate)
                else:
                    candidates.append(candidate)
        templates = sorted(candidates, key=lambda x: x.prob, reverse=True)[:self.beam_n]

        while len(templates) > 0:
            phrases = []
            candidates = []
            fails = []
            for template in templates:
                isSynchronous, new_candidates = self.choose_substitution(template)

                if isSynchronous:
                    for candidate in new_candidates:
                        if len(candidate.tree_rules) == 0 and len(candidate.graph_rules) == 0 and candidate.tree not in phrases:
                            concluded.append(candidate)
                            phrases.append(candidate.tree)
                        else:
                            candidates.append(candidate)
                else:
                    tree = template.tree
                    aux = []
                    for token in tree.split():
                        if not (token[0] == ':' and len(token) > 1):
                            aux.append(token)
                    template.tree = ' '.join(aux)
                    fails.append(template)
            templates = sorted(candidates, key=lambda x: x.prob, reverse=True)[:self.beam_n]

        if len(concluded) == 0:
            concluded = fails
        return concluded

if __name__ == '__main__':
    models = [prop.initial_rule_edges,
              prop.substitution_rule_edges,
              prop.initial_rule_edges_head,
              prop.substitution_rule_edges_head]
    verb2noun, noun2verb, verb2actor, actor2verb = utils.noun_verb('../data/morph-verbalization-v1.01.txt')
    sub2word = utils.subgraph_word('../data/verbalization-list-v1.06.txt')

    amr = """(s / shut-down-05
               :ARG0 (p / person :wiki "Hugo_Chvez"
                  :name (n / name :op1 "Hugo" :op2 "Chavez"))
               :ARG1 (i / it)
               :time (d / date-entity :year 2004))"""

    amr = """(c / contrast-01
  :ARG2 (r / reply-01
          :ARG0 (h / he)
          :polarity -))"""

    factory = ERGFactory(verb2noun=verb2noun,
                     noun2verb=noun2verb,
                     verb2actor=verb2actor,
                     actor2verb=actor2verb,
                     sub2word=sub2word)

    gen = Generator(amr=amr.lower(),
                    erg_factory=factory,
                    models=models,
                    beam_n=20)

    candidates = gen.run()

    for candidate in candidates:
        tree = candidate.tree

        print tree
        print candidate.prob
        print 10 * '-'
__author__ = 'thiagocastroferreira'

from sys import path
path.append('/home/tcastrof/amr/scp_repo')
path.append('/home/tcastrof/amr/Grammar')
from main.aligners.AMRAligner import AMRAligner
from main.grammars.SynchG import SynchG, SynchRule
from main.aligners.TAGSynchAligner import TAGSynchAligner

import copy
import json
import os
import main.utils as utils
import traceback

from stanford_corenlp_pywrapper import CoreNLP

class RuleProducer(object):
    def __init__(self, aligner, dirs):
        self.aligner = aligner
        self.dirs = dirs

        self.processed, self.errors, self.rules_processed, self.invalid_rules = 0, 0, 0, 0

        self.grammar = SynchG(initial_rules=[], substitution_rules=[], adjoining_rules=[], lexicons=[])

    def print_report(self):
        print 'AMRs processed: ', self.processed
        print 'Errors: ', self.errors
        print 'Rate: ', str(round(float(self.errors)/self.processed, 4))
        print 10 * '-'
        print 'Rules processed', self.rules_processed
        print 'Invalid rules: ', self.invalid_rules
        print 'Rate: ', str(round(float(self.invalid_rules)/self.rules_processed, 4))
        print 20 * '-' + '\n\n'

    def align_amr(self, amr):
        self.processed = self.processed + 1
        alignments, info = self.aligner.run(amr['amr'], amr['sentence'])
        return alignments, info

    def align_tree(self, amr, info, alignments):
        # print amr['sentence']
        # print amr['amr'], '\n\n'
        inducer = TAGSynchAligner(text=amr['sentence'], amr=amr['amr'], info=info, alignments=alignments)
        alignments = inducer.run()
        return alignments

    def extract_lexicons(self, alignments):
        for lexicon in alignments.lexicons:
            rule_id = lexicon.rule_id
            lexicon.head = alignments.erg_rules[rule_id].head

            edge = alignments.erg_rules[rule_id].name.split('/')[0]
            lexicon.edge = edge

            self.grammar.lexicons.append(lexicon)

    def extract_rules(self, alignments):
        for rule_id in alignments.erg_rules:
            try:
                self.rules_processed = self.rules_processed + 1

                name = alignments.erg_rules[rule_id].name
                head = alignments.erg_rules[rule_id].head
                tokens = alignments.erg_rules[rule_id].tokens

                parent = alignments.erg_rules[rule_id].parent
                if parent != '':
                    parent_rule = alignments.id2rule[parent]
                    parent_head = alignments.erg_rules[parent].head
                else:
                    parent_rule, parent_head = '', ''

                graph = alignments.erg_rules[rule_id].graph
                _graph_rules = alignments.erg_rules[rule_id].rules
                # fix rule names
                graph_rules = {}
                for node in _graph_rules:
                    graph_rules[graph.nodes[node].name] = copy.copy(_graph_rules[node])

                tree = alignments.tag_rules[rule_id].tree
                tree_rules = alignments.tag_rules[rule_id].rules
                # TO DO fix rule names

                features = alignments.features[rule_id]

                if tree.check_validity():
                    rule = SynchRule(name=name,
                                     head=head,
                                     parent=parent,
                                     parent_rule=parent_rule,
                                     parent_head=parent_head,
                                     graph=graph,
                                     graph_rules=graph_rules,
                                     tree=tree,
                                     tree_rules=tree_rules,
                                     features=features,
                                     tokens=tokens)

                    if ':root' in rule.name:
                        self.grammar.initial_rules.append(rule)
                    else:
                        self.grammar.substitution_rules.append(rule)

                    if rule_id in alignments.adjoining_rules:
                        for adjoining in alignments.adjoining_rules[rule_id]:
                            tree = adjoining.tree
                            tree_rules = adjoining.rules
                            rule = SynchRule(name=name,
                                             head=head,
                                             parent=parent,
                                             parent_rule=parent_rule,
                                             parent_head=parent_head,
                                             graph=graph,
                                             graph_rules=graph_rules,
                                             tree=tree,
                                             tree_rules=tree_rules,
                                             features=features,
                                             tokens=tokens)
                            self.grammar.adjoining_rules.append(rule)
                else:
                    self.invalid_rules = self.invalid_rules + 1
            except:
                self.errors = self.errors +1
                traceback.print_exc()
                print '\n'
                self.print_report()

    def process(self, amr):
        # print amr
        try:
            alignments, info = self.align_amr(amr)

            try:
                alignments = self.align_tree(amr=amr, alignments=alignments, info=info)
                self.extract_rules(alignments)
                self.extract_lexicons(alignments)
            except:
                self.errors = self.errors +1
                traceback.print_exc()
                print '\n'
                self.print_report()
        except:
            self.errors = self.errors + 1
            print 'ALIGNER ERROR', amr['file'], amr['id'], self.errors
            print traceback.print_exc()
            print '\n'

    def write_lexicons(self, fname):
        lexicons = []

        for lexicon in self.grammar.lexicons:
            aux = {
                'w_t': lexicon.w_t,
                'w_tm1': lexicon.w_tm1,
                'head': lexicon.head,
                'edge': lexicon.edge,
                'pos': lexicon.pos
            }
            lexicons.append(aux)

        json.dump(lexicons, open(fname, 'w'), sort_keys=True, indent=4, separators=(',', ': '))

    def write_voices(self, fname):
        def write(grammar):
            voices = []
            for rule in grammar:
                if rule.features != None:
                    if '/E' in rule.name:
                        tree = 'empty'
                    else:
                        tree = rule.tree.prettify(rule.tree.root)

                    if rule.features.type == 'verb':
                        voice = { 'template': tree, 'voice': rule.features.voice }
                        voices.append(voice)
            return voices

        voices = write(self.grammar.initial_rules)
        voices.extend(write(self.grammar.substitution_rules))

        json.dump(voices, open(fname, 'w'), sort_keys=True, indent=4, separators=(',', ': '))

    def write_rules(self, fnames={}):
        def write(grammar, fname):
            rules = []
            for rule in grammar:
                try:
                    if '/E' in rule.name:
                        tree = 'empty'
                    else:
                        tree = rule.tree.prettify(rule.tree.root)
                    graph = rule.graph.prettify(rule.head, rule.graph.root, print_constants=False)

                    verb, noun = {}, {}
                    if rule.features != None:
                        if rule.features.type == 'verb':
                            verb = {'tense': rule.features.tense, 'voice': rule.features.voice}
                        elif rule.features.type == 'noun':
                            noun = {'form': rule.features.form, 'number': rule.features.number, 'inPP': rule.features.inPP}


                    aux = {
                        'name':rule.name,
                        'head':rule.head,
                        # 'parent_rule':rule.parent_rule,
                        # 'parent_head':rule.parent_head,
                        'graph':graph,
                        'graph_rules':rule.graph_rules,
                        'tree':tree,
                        'tree_rules':rule.tree_rules,
                        'noun_info': noun,
                        'verb_info': verb,
                        # 'tokens':rule.tokens
                    }
                    rules.append(aux)
                except:
                    pass

            json.dump(rules, open(fname, 'w'), sort_keys=True, indent=4, separators=(',', ': '))

        write(self.grammar.initial_rules, fnames['initial'])
        write(self.grammar.substitution_rules, fnames['substitution'])
        write(self.grammar.adjoining_rules, fnames['adjoining'])

    def run(self):
        for dir in self.dirs:
            files = os.listdir(dir)
            for fname in files:
                print fname, '\r',
                amrs = utils.parse_corpus(os.path.join(dir, fname))

                for amr in amrs:
                    self.process(amr)

                    if (self.processed % 1000) == 0:
                        self.print_report()

if __name__ == '__main__':
    proc = CoreNLP("coref")
    freq_table = json.load(open('/home/tcastrof/amr/data/alignments/table.json'))
    verb2noun, noun2verb, verb2actor, actor2verb = utils.noun_verb('/home/tcastrof/amr/data/morph-verbalization-v1.01.txt')
    sub2word = utils.subgraph_word('/home/tcastrof/amr/data/verbalization-list-v1.06.txt')

    aligner = AMRAligner(verb2noun, noun2verb, verb2actor, actor2verb, sub2word, freq_table, proc)

    dirs = ['/home/tcastrof/amr/data/LDC2016E25/data/amrs/unsplit',
            '/home/tcastrof/amr/data/LDC2016E33/data']
    frules = {
        'initial': '/home/tcastrof/amr/data/semeval/rules/initial.json',
        'substitution': '/home/tcastrof/amr/data/semeval/rules/substitution.json',
        'adjoining': '/home/tcastrof/amr/data/semeval/rules/adjoining.json'
    }

    flexicons = '/home/tcastrof/amr/data/TEST/lexicon/lexicon.json'
    fvoices = '/home/tcastrof/amr/data/TEST/lexicon/voices.json'

    producer = RuleProducer(aligner=aligner, dirs=dirs)

    producer.run()
    producer.write_rules(frules)
    producer.write_lexicons(flexicons)
    producer.write_voices(fvoices)
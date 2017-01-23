from main.old import Aligner, RuleInducer

__author__ = 'thiagocastroferreira'

import unittest
import main.utils as utils
import json

from stanford_corenlp_pywrapper import CoreNLP

class RuleInducerTest(unittest.TestCase):
    proc = CoreNLP("coref")
    freq_table = json.load(open('../main/data/alignments/table.json'))
    verb2noun, noun2verb, verb2actor, actor2verb = utils.noun_verb('../main/data/morph-verbalization-v1.01.txt')
    sub2word = utils.subgraph_word('../main/data/verbalization-list-v1.06.txt')

    aligner = Aligner(verb2noun, noun2verb, verb2actor, actor2verb, sub2word, freq_table, proc)

    def test_proper_np(self):
        text = 'Barack Obama'

        amr = """(p / person
                      :name (n / name
                            :op1 \"Barack\"
                            :op2 \"Obama\"))"""

        alignments, info = self.aligner.freq_rules(amr, text)
        inducer = RuleInducer(text, amr, info, alignments)
        id2subtrees, id2rule, adjtrees = inducer.freq_rules()

        tag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        ltag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        tag, ltag = inducer.prettify(id2subtrees, id2rule, adjtrees, tag, ltag)

        original = {
            'ltag': {
                'initial': {
                    (u':root/ROOT', '[person, :name, :op1, :op2]'): [u'(ROOT (NP (NNP XXX) (NNP XXX)))']
                },
                'substitution':{},
                'adjoining':{}
            },
            'tag': {
                'initial': {u':root/ROOT': [u'(ROOT (NP (NNP XXX) (NNP XXX)))']},
                'substitution':{},
                'adjoining':{}
            }}

        self.assertDictEqual(original, {'tag':tag, 'ltag':ltag})

    def test_np(self):
        text = 'The cat'

        amr = """(c / cat)"""

        alignments, info = self.aligner.freq_rules(amr, text)
        inducer = RuleInducer(text, amr, info, alignments)
        id2subtrees, id2rule, adjtrees = inducer.freq_rules()

        tag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        ltag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        tag, ltag = inducer.prettify(id2subtrees, id2rule, adjtrees, tag, ltag)

        original = {
            'ltag': {
                'initial': {
                    (u':root/ROOT', '[cat]'): [u'(ROOT (FRAG (NP (DT the) (NN XXX))))']
                },
                'substitution':{},
                'adjoining':{}
            },
            'tag':
                {
                    'initial': {
                        u':root/ROOT': [u'(ROOT (FRAG (NP (DT the) (NN XXX))))']
                    },
                    'substitution':{},
                    'adjoining':{}
                }}

        self.assertDictEqual(original, {'tag':tag, 'ltag':ltag})

    def test_np2(self):
        text = 'The teacher and the worker'

        amr = """(a / and
                    :op1 (p / person
                            :ARG0-of (t / teach-01))
                    :op2 (p2 / person
                            :ARG0-of (w / work-01))"""

        alignments, info = self.aligner.freq_rules(amr, text)
        inducer = RuleInducer(text, amr, info, alignments)
        id2subtrees, id2rule, adjtrees = inducer.freq_rules()

        tag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        ltag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        tag, ltag = inducer.prettify(id2subtrees, id2rule, adjtrees, tag, ltag)

        original = {
            'ltag': {
                'initial': {
                    (u':root/ROOT', '[and]'): [u'(ROOT (NP (:op1/NP) (CC XXX) (:op2/NP)))']
                },
                'adjoining': {},
                'substitution': {
                    (u':op2/NP', '[person, :ARG0-of]'): [u'(NP (DT the) (NN XXX))'],
                    (u':op1/NP', '[person, :ARG0-of]'): [u'(NP (DT the) (NN XXX))']
                }
            },
            'tag': {
                'initial': {
                    u':root/ROOT': [u'(ROOT (NP (:op1/NP) (CC XXX) (:op2/NP)))']
                },
                'adjoining': {},
                'substitution': {
                    u':op2/NP': [u'(NP (DT the) (NN XXX))'],
                    u':op1/NP': [u'(NP (DT the) (NN XXX))']
                }
            }
        }

        self.assertDictEqual(original, {'tag':tag, 'ltag':ltag})

    def test_domain(self):
        text = 'That is a shame.'
        amr = """(s / shame
                    :domain (t / that))"""

        alignments, info = self.aligner.freq_rules(amr, text)
        inducer = RuleInducer(text, amr, info, alignments)
        id2subtrees, id2rule, adjtrees = inducer.freq_rules()

        tag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        ltag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        tag, ltag = inducer.prettify(id2subtrees, id2rule, adjtrees, tag, ltag)

        original = {
            'ltag': {
                'initial': {
                    (u':root/ROOT', '[shame]', 'active', 'simple present'): [u'(ROOT (S (:domain/NP) (VP (VB be) (NP (DT a) (NN XXX))) (. .)))']
                },
                'adjoining': {},
                'substitution': {
                    (u':domain/NP', '[that]'): [u'(NP (DT XXX))']
                }
            },
            'tag': {
                'initial': {
                    u':root/ROOT': [u'(ROOT (S (:domain/NP) (VP (VB be) (NP (DT a) (NN XXX))) (. .)))']
                },
                'adjoining': {},
                'substitution': {
                    u':domain/NP': [u'(NP (DT XXX))']
                }
            }
        }

        self.assertDictEqual(original, {'tag':tag, 'ltag':ltag})

    def test_subj_verb_obj(self):
        text = 'The girl adjusted the machine .'

        amr = """(a / adjust-01
                      :ARG0 (g / girl)
                      :ARG1 (m / machine))"""

        alignments, info = self.aligner.freq_rules(amr, text)
        inducer = RuleInducer(text, amr, info, alignments)
        id2subtrees, id2rule, adjtrees = inducer.freq_rules()

        tag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        ltag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        tag, ltag = inducer.prettify(id2subtrees, id2rule, adjtrees, tag, ltag)

        original = {
            'ltag':
                {
                    'initial': {
                        (u':root/ROOT', '[adjust-01]', 'active', 'simple past'): [u'(ROOT (S (:ARG0/NP) (VP (VB XXX) (:ARG1/NP)) (. .)))']
                    },
                    'substitution':{
                        (u':ARG1/NP', '[machine]'): [u'(NP (DT the) (NN XXX))'],
                        (u':ARG0/NP', '[girl]'): [u'(NP (DT the) (NN XXX))']
                    },
                    'adjoining':{}
                },
            'tag':
                {
                    'initial': {
                        u':root/ROOT': [u'(ROOT (S (:ARG0/NP) (VP (VB XXX) (:ARG1/NP)) (. .)))']
                    },
                    'substitution':{
                        u':ARG1/NP': [u'(NP (DT the) (NN XXX))'],
                        u':ARG0/NP': [u'(NP (DT the) (NN XXX))']
                    },
                    'adjoining':{}
                }}

        self.assertDictEqual(original, {'tag':tag, 'ltag':ltag})

    def test_subj_verb_obj_mod(self):
        text = 'The man described the mission as a disaster .'

        amr = """(d2 / describe-01
                      :ARG0 (m2 / man)
                      :ARG1 (m / mission)
                      :ARG2 (d / disaster))"""

        alignments, info = self.aligner.freq_rules(amr, text)
        inducer = RuleInducer(text, amr, info, alignments)
        id2subtrees, id2rule, adjtrees = inducer.freq_rules()

        tag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        ltag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        tag, ltag = inducer.prettify(id2subtrees, id2rule, adjtrees, tag, ltag)

        original = {
            'ltag':
                {
                    'initial': {
                        (u':root/ROOT', '[describe-01]', 'active', 'simple past'): [u'(ROOT (S (:ARG0/NP) (VP (VB XXX) (:ARG1/NP) (:ARG2/PP)) (. .)))']
                    },
                    'substitution':{
                        (u':ARG1/NP', '[mission]'): [u'(NP (DT the) (NN XXX))'],
                        (u':ARG0/NP', '[man]'): [u'(NP (DT the) (NN XXX))'],
                        (u':ARG2/PP', '[disaster]'): [u'(PP (IN as) (NP (DT a) (NN XXX)))']
                    },
                    'adjoining':{}
                },
            'tag':
                {
                    'initial': {
                        u':root/ROOT': [u'(ROOT (S (:ARG0/NP) (VP (VB XXX) (:ARG1/NP) (:ARG2/PP)) (. .)))']
                    },
                    'substitution':{
                        u':ARG1/NP': [u'(NP (DT the) (NN XXX))'],
                        u':ARG0/NP': [u'(NP (DT the) (NN XXX))'],
                        u':ARG2/PP': [u'(PP (IN as) (NP (DT a) (NN XXX)))']
                    },
                    'adjoining':{}
                }}

        self.assertDictEqual(original, {'tag':tag, 'ltag':ltag})

    def test_subj_verb_obj_loc(self):
        text = 'The man married the girl at the house .'

        amr = """(m / marry-01
                      :ARG0 (m2 / man)
                      :ARG1 (g / girl
                            :location (h / house)))"""

        alignments, info = self.aligner.freq_rules(amr, text)
        inducer = RuleInducer(text, amr, info, alignments)
        id2subtrees, id2rule, adjtrees = inducer.freq_rules()

        tag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        ltag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        tag, ltag = inducer.prettify(id2subtrees, id2rule, adjtrees, tag, ltag)

        original = {
            'ltag':
                {
                    'initial': {
                        (u':root/ROOT', '[marry-01]', 'active', 'simple past'): [u'(ROOT (S (:ARG0/NP) (VP (VB XXX) (:ARG1/NP)) (. .)))']
                    },
                    'substitution':{
                        (u':ARG1/NP', '[girl]'): [u'(NP (DT the) (NN XXX))'],
                        (u':ARG0/NP', '[man]'): [u'(NP (DT the) (NN XXX))'],
                        (u':location/PP', '[house]'): [u'(PP (IN at) (NP (DT the) (NN XXX)))']
                    },
                    'adjoining':{
                        (u':ARG1/NP', '[girl]'): [u'(NP (NP*) (:location/PP))']
                    }
                },
            'tag':
                {
                    'initial': {
                        u':root/ROOT': [u'(ROOT (S (:ARG0/NP) (VP (VB XXX) (:ARG1/NP)) (. .)))']
                    },
                    'substitution':{
                        u':ARG1/NP': [u'(NP (DT the) (NN XXX))'],
                        u':ARG0/NP': [u'(NP (DT the) (NN XXX))'],
                        u':location/PP': [u'(PP (IN at) (NP (DT the) (NN XXX)))']
                    },
                    'adjoining':{
                        u':ARG1/NP': [u'(NP (NP*) (:location/PP))']
                    }
                }}

        self.assertDictEqual(original, {'tag':tag, 'ltag':ltag})

    def test_loc_subj_verb_obj(self):
        text = 'At the house , the man married the girl .'

        amr = """(m / marry-01
                      :ARG0 (m2 / man)
                      :ARG1 (g / girl
                            :location (h / house)))"""

        alignments, info = self.aligner.freq_rules(amr, text)
        inducer = RuleInducer(text, amr, info, alignments)
        id2subtrees, id2rule, adjtrees = inducer.freq_rules()

        tag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        ltag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        tag, ltag = inducer.prettify(id2subtrees, id2rule, adjtrees, tag, ltag)

        original = {
            'ltag':
                {
                    'initial': {
                        (u':root/ROOT', '[marry-01]', 'active', 'simple past'): [u'(ROOT (S (:location/PP) (, ,) (:ARG0/NP) (VP (VB XXX) (:ARG1/NP)) (. .)))']
                    },
                    'substitution':{
                        (u':ARG1/NP', '[girl]'): [u'(NP (DT the) (NN XXX))'],
                        (u':ARG0/NP', '[man]'): [u'(NP (DT the) (NN XXX))'],
                        (u':location/PP', '[house]'): [u'(PP (IN at) (NP (DT the) (NN XXX)))']
                    },
                    'adjoining':{}
                },
            'tag':
                {
                    'initial': {
                        u':root/ROOT': [u'(ROOT (S (:location/PP) (, ,) (:ARG0/NP) (VP (VB XXX) (:ARG1/NP)) (. .)))']
                    },
                    'substitution':{
                        u':ARG1/NP': [u'(NP (DT the) (NN XXX))'],
                        u':ARG0/NP': [u'(NP (DT the) (NN XXX))'],
                        u':location/PP': [u'(PP (IN at) (NP (DT the) (NN XXX)))']
                    },
                    'adjoining':{}
                }}

        self.assertDictEqual(original, {'tag':tag, 'ltag':ltag})

    def test_modal(self):
        text = 'You can leave .'

        amr = """(p / possible
                      :domain (l / leave-01
                            :ARG0 (y / you)))"""

        alignments, info = self.aligner.freq_rules(amr, text)
        inducer = RuleInducer(text, amr, info, alignments)
        id2subtrees, id2rule, adjtrees = inducer.freq_rules()

        tag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        ltag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        tag, ltag = inducer.prettify(id2subtrees, id2rule, adjtrees, tag, ltag)

        original = {
            'ltag':
                {
                    'initial': {
                        (u':root/ROOT', '[possible]', 'active', 'simple present'): [u'(ROOT (S (:ARG0/NP) (VP (MD XXX) (:domain/VP)) (. .)))']
                    },
                    'substitution':{
                        (u':ARG0/NP', '[you]'): [u'(NP (PRP XXX))'],
                        (u':domain/VP', '[leave-01]', 'active', 'infinitive'): [u'(VP (VB XXX))']
                    },
                    'adjoining':{}
                },
            'tag':
                {
                    'initial': {
                        u':root/ROOT': [u'(ROOT (S (:ARG0/NP) (VP (MD XXX) (:domain/VP)) (. .)))']
                    },
                    'substitution':{
                        u':domain/VP': [u'(VP (VB XXX))'],
                        u':ARG0/NP': [u'(NP (PRP XXX))']
                    },
                    'adjoining':{}
                }}

        self.assertDictEqual(original, {'tag':tag, 'ltag':ltag})

    def test_passive(self):
        text = 'The machine was adjusted by the girl .'

        amr = """(a / adjust-01
                      :ARG0 (g / girl)
                      :ARG1 (m / machine))"""

        alignments, info = self.aligner.freq_rules(amr, text)
        inducer = RuleInducer(text, amr, info, alignments)
        id2subtrees, id2rule, adjtrees = inducer.freq_rules()

        tag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        ltag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        tag, ltag = inducer.prettify(id2subtrees, id2rule, adjtrees, tag, ltag)

        original = {
            'ltag':
                {
                    'initial': {
                        (u':root/ROOT', '[adjust-01]', 'passive', 'simple past'): [u'(ROOT (S (:ARG1/NP) (VP (VB XXX) (:ARG0/PP)) (. .)))']
                    },
                    'substitution':{
                        (u':ARG1/NP', '[machine]'): [u'(NP (DT the) (NN XXX))'],
                        (u':ARG0/PP', '[girl]'): [u'(PP (IN by) (NP (DT the) (NN XXX)))']
                    },
                    'adjoining':{
                        (u':root/ROOT', '[adjust-01]', 'passive', 'simple past'): [u'(VP (VB be) (VP*))']
                    }
                },
            'tag':
                {
                    'initial': {
                        u':root/ROOT': [u'(ROOT (S (:ARG1/NP) (VP (VB XXX) (:ARG0/PP)) (. .)))']
                    },
                    'substitution':{
                        u':ARG1/NP': [u'(NP (DT the) (NN XXX))'],
                        u':ARG0/PP': [u'(PP (IN by) (NP (DT the) (NN XXX)))']
                    },
                    'adjoining':{
                        u':root/ROOT': [u'(VP (VB be) (VP*))']
                    }
                }}

        self.assertDictEqual(original, {'tag':tag, 'ltag':ltag})

    def test_relative_pronoun(self):
        text = 'the car that is not black.'

        amr = """(c / car
                   :ARG1-of (b / black-04
                              :polarity -))"""

        alignments, info = self.aligner.freq_rules(amr, text)
        inducer = RuleInducer(text, amr, info, alignments)
        id2subtrees, id2rule, adjtrees = inducer.freq_rules()

        tag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        ltag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        tag, ltag = inducer.prettify(id2subtrees, id2rule, adjtrees, tag, ltag)

        original = {
            'ltag': {
                'initial': {
                    (u':root/ROOT', '[car]'): [u'(ROOT (NP (DT the) (NN XXX) (SBAR (WHNP (WDT that)) (S (VP (VBZ is) (:polarity/RB) (:ARG1-of/ADJP)))) (. .)))']
                },
                'substitution':{
                    (u':polarity/RB', '[-]'): [u'(RB XXX)'],
                    (u':ARG1-of/ADJP', '[black-04]'): [u'(ADJP (JJ XXX))']
                },
                'adjoining':{}
            },
            'tag': {
                'initial': {
                    u':root/ROOT': [u'(ROOT (NP (DT the) (NN XXX) (SBAR (WHNP (WDT that)) (S (VP (VBZ is) (:polarity/RB) (:ARG1-of/ADJP)))) (. .)))']
                },
                'substitution':{
                    u':ARG1-of/ADJP': [u'(ADJP (JJ XXX))'],
                    u':polarity/RB': [u'(RB XXX)']
                },
                'adjoining':{}
            }}

        self.assertDictEqual(original, {'tag':tag, 'ltag':ltag})

    def test_reflexive(self):
        text= 'He cuts himself'
        amr = """(c / cut-01
                      :ARG0 (h / he)
                      :ARG1 h)"""

        alignments, info = self.aligner.freq_rules(amr, text)
        inducer = RuleInducer(text, amr, info, alignments)
        id2subtrees, id2rule, adjtrees = inducer.freq_rules()

        tag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        ltag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        tag, ltag = inducer.prettify(id2subtrees, id2rule, adjtrees, tag, ltag)

        original = {
            'ltag': {
                'initial': {
                    (u':root/ROOT', '[cut-01]', 'active', 'simple present'): [u'(ROOT (S (:ARG0/NP) (VP (VB XXX) (:ARG1/NP))))']
                },
                'substitution':{
                    (u':ARG1/NP', '[h]'): [u'(NP (PRP XXX))'],
                    (u':ARG0/NP', '[he]'): [u'(NP (PRP XXX))']
                },
                'adjoining':{}
            },
            'tag': {
                'initial': {
                    u':root/ROOT': [u'(ROOT (S (:ARG0/NP) (VP (VB XXX) (:ARG1/NP))))']
                },
                'substitution':{
                    u':ARG1/NP': [u'(NP (PRP XXX))'],
                    u':ARG0/NP': [u'(NP (PRP XXX))']
                },
                'adjoining':{}
            }}

        self.assertDictEqual(original, {'tag':tag, 'ltag':ltag})

    def test_question(self):
        text = 'What determined the position of Hong Kong as a shopping paradise ?'
        amr = """(d / determine-01
                      :ARG0 (a / amr-unknown)
                      :ARG1 (p / position-01
                            :ARG1 (c / city :wiki "Hong_Kong"
                                  :name (n / name :op1 "Hong" :op2 "Kong"))
                            :ARG2 (p2 / paradise
                                  :topic (s / shop-01))))"""

        alignments, info = self.aligner.freq_rules(amr, text)
        inducer = RuleInducer(text, amr, info, alignments)
        id2subtrees, id2rule, adjtrees = inducer.freq_rules()

        tag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        ltag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        tag, ltag = inducer.prettify(id2subtrees, id2rule, adjtrees, tag, ltag)

        original = {
            'ltag': {
                'initial': {
                    (u':root/ROOT', '[determine-01]', 'active', 'simple past'): [u'(ROOT (SBARQ (:ARG0/WHNP) (SQ (VP (VB XXX) (:ARG1/NP) (:ARG2/PP))) (. ?)))']
                },
                'substitution':{
                    (u':ARG2/PP', '[paradise]'): [u'(PP (IN as) (NP (DT a) (:topic/NN) (NN XXX)))'],
                    (u':ARG0/WHNP', '[amr-unknown]'): [u'(WHNP (WDT XXX))'],
                    (u':ARG1/NP', '[position-01]'): [u'(NP (DT the) (NN XXX))'],
                    (u':topic/NN', '[shop-01]'): [u'(NN XXX)'],
                    (u':ARG1/PP', '[city, :name, :op1, :op2]'): [u'(PP (IN of) (NP (NNP XXX) (NNP XXX)))']
                },
                'adjoining':{
                    (u':ARG1/NP', '[position-01]'): [u'(NP (NP*) (:ARG1/PP))']
                }
            },
            'tag': {
                'initial': {
                    u':root/ROOT': [u'(ROOT (SBARQ (:ARG0/WHNP) (SQ (VP (VB XXX) (:ARG1/NP) (:ARG2/PP))) (. ?)))']
                },
                'substitution':{
                    u':ARG0/WHNP': [u'(WHNP (WDT XXX))'],
                    u':topic/NN': [u'(NN XXX)'],
                    u':ARG1/PP': [u'(PP (IN of) (NP (NNP XXX) (NNP XXX)))'],
                    u':ARG1/NP': [u'(NP (DT the) (NN XXX))'],
                    u':ARG2/PP': [u'(PP (IN as) (NP (DT a) (:topic/NN) (NN XXX)))']
                },
                'adjoining':{
                    u':ARG1/NP': [u'(NP (NP*) (:ARG1/PP))']
                }
            }}

        self.assertDictEqual(original, {'tag':tag, 'ltag':ltag})

    def test_two_sentences(self):
        text = 'It continues to explore ; it continues to open new worlds .'
        amr = """(m / multi-sentence
                          :snt1 (c / continue-01
                                :ARG0 (i / it)
                                :ARG1 (e / explore-01
                                      :ARG0 i))
                          :snt2 (c2 / continue-01
                                :ARG0 (i2 / it)
                                :ARG1 (o / open-01
                                      :ARG0 i2
                                      :ARG1 (w / world
                                            :ARG1-of (n / new-02)))))"""

        alignments, info = self.aligner.freq_rules(amr, text)
        inducer = RuleInducer(text, amr, info, alignments)
        id2subtrees, id2rule, adjtrees = inducer.freq_rules()

        tag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        ltag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        tag, ltag = inducer.prettify(id2subtrees, id2rule, adjtrees, tag, ltag)

        original = {
            'ltag': {
                'initial': {
                    (u':root/ROOT', '[multi-sentence]'): [u'(ROOT (S (:snt1/S) (: ;) (:snt2/S) (. .)))']
                },
                'adjoining': {
                    (u':ARG1/S', '[open-01]', 'active', 'infinitive'): [u'(VP (TO to) (VP*))'],
                    (u':ARG1/S', '[explore-01]', 'active', 'infinitive'): [u'(VP (TO to) (VP*))'],
                },
                'substitution': {
                    (u':ARG1/S', '[open-01]', 'active', 'infinitive'): [u'(S (VP (VB XXX) (:ARG1/NP)))'],
                    (u':ARG1/S', '[explore-01]', 'active', 'infinitive'): [u'(S (VP (VB XXX)))'],
                    (u':snt1/S', '[continue-01]', 'active', 'simple present'): [u'(S (:ARG0/NP) (VP (VB XXX) (:ARG1/S)))'],
                    (u':ARG1/NP', '[world]'): [u'(NP (:ARG1-of/JJ) (NNS XXX))'],
                    (':ARG0/E', '[i]'): ['empty'],
                    (':ARG0/E', '[i2]'): ['empty'],
                    (u':ARG1-of/JJ', '[new-02]'): [u'(JJ XXX)'],
                    (u':snt2/S', '[continue-01]', 'active', 'simple present'): [u'(S (:ARG0/NP) (VP (VB XXX) (:ARG1/S)))'],
                    (u':ARG0/NP', '[it]'): [u'(NP (PRP XXX))', u'(NP (PRP XXX))']
                }
            },
            'tag': {
                'initial': {
                    u':root/ROOT': [u'(ROOT (S (:snt1/S) (: ;) (:snt2/S) (. .)))']
                },
                'adjoining': {
                    u':ARG1/S': [u'(VP (TO to) (VP*))',
                                 u'(VP (TO to) (VP*))'],
                },
                'substitution': {
                    u':ARG1/S': [u'(S (VP (VB XXX)))',
                                 u'(S (VP (VB XXX) (:ARG1/NP)))'],
                    u':ARG0/NP': [u'(NP (PRP XXX))', u'(NP (PRP XXX))'],
                    u':ARG1/NP': [u'(NP (:ARG1-of/JJ) (NNS XXX))'],
                    u':ARG1-of/JJ': [u'(JJ XXX)'],
                    u':snt2/S': [u'(S (:ARG0/NP) (VP (VB XXX) (:ARG1/S)))'],
                    u':snt1/S': [u'(S (:ARG0/NP) (VP (VB XXX) (:ARG1/S)))'],
                    ':ARG0/E': ['empty', 'empty']}
            }}

        self.assertDictEqual(original, {'tag':tag, 'ltag':ltag})

    def test_two_clauses(self):
        text = 'The boy wants to ride the red bicycle .'

        amr = """(w / want-01
                      :ARG0 (b2 / boy)
                      :ARG1 (r2 / ride-01
                            :ARG1 (b / bicycle
                                  :mod (r / red))))"""

        alignments, info = self.aligner.freq_rules(amr, text)
        inducer = RuleInducer(text, amr, info, alignments)
        id2subtrees, id2rule, adjtrees = inducer.freq_rules()

        tag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        ltag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        tag, ltag = inducer.prettify(id2subtrees, id2rule, adjtrees, tag, ltag)

        original = {
            'ltag':
                {
                    'initial': {
                        (u':root/ROOT', '[want-01]', 'active', 'simple present'): [u'(ROOT (S (:ARG0/NP) (VP (VB XXX) (:ARG1/S)) (. .)))']
                    },
                    'substitution':{
                        (u':mod/JJ', '[red]'): [u'(JJ XXX)'],
                        (u':ARG0/NP', '[boy]'): [u'(NP (DT the) (NN XXX))'],
                        (u':ARG1/NP', '[bicycle]'): [u'(NP (DT the) (:mod/JJ) (NN XXX))'],
                        (u':ARG1/S', '[ride-01]', 'active', 'infinitive'): [u'(S (VP (VB XXX) (:ARG1/NP)))']
                    },
                    'adjoining':{
                        (u':ARG1/S', '[ride-01]', 'active', 'infinitive'): [u'(VP (TO to) (VP*))']
                    }
                },
            'tag':
                {
                    'initial': {
                        u':root/ROOT': [u'(ROOT (S (:ARG0/NP) (VP (VB XXX) (:ARG1/S)) (. .)))']
                    },
                    'substitution':{
                        u':ARG1/NP': [u'(NP (DT the) (:mod/JJ) (NN XXX))'],
                        u':ARG1/S': [u'(S (VP (VB XXX) (:ARG1/NP)))'],
                        u':ARG0/NP': [u'(NP (DT the) (NN XXX))'],
                        u':mod/JJ': [u'(JJ XXX)']
                    },
                    'adjoining':{
                        u':ARG1/S': [u'(VP (TO to) (VP*))']
                    }
                }}

        self.assertDictEqual(original, {'tag':tag, 'ltag':ltag})

    def test_spec1(self):
        text = 'The London emergency services said that altogether eleven people had been sent to hospital for treatment due to minor wounds.'
        amr = """(s / say-01
                      :ARG0 (s2 / service
                            :mod (e / emergency)
                            :location (c / city :wiki 'London'
                                  :name (n / name :op1 'London')))
                      :ARG1 (s3 / send-01
                            :ARG1 (p / person :quant 11)
                            :ARG2 (h / hospital)
                            :mod (a / altogether)
                            :purpose (t / treat-03
                                  :ARG1 p
                                  :ARG2 (w / wound-01
                                        :ARG1 p
                                        :mod (m / minor)))))"""

        alignments, info = self.aligner.freq_rules(amr, text)
        inducer = RuleInducer(text, amr, info, alignments)
        id2subtrees, id2rule, adjtrees = inducer.freq_rules()

        tag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        ltag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        tag, ltag = inducer.prettify(id2subtrees, id2rule, adjtrees, tag, ltag)

        original = {
            'ltag': {
                'initial': {
                    (u':root/ROOT', '[say-01]', 'active', 'simple past'): [u'(ROOT (S (:ARG0/NP) (VP (VB XXX) (:ARG1/SBAR)) (. .)))']
                },
                'substitution':{
                    (u':ARG1/NP', '[person]'): [u'(NP (:quant/NNS) (NNS XXX))'],
                    (u':ARG2/PP', '[hospital]'): [u'(PP (TO to) (NP (NN XXX)))'],
                    (u':location/NNP', '[city, :name, :op1]'): [u'(NNP XXX)'],
                    (u':ARG1/SBAR', '[send-01]', 'passive', 'past perfect'): [u'(SBAR (IN that) (S (:mod/ADVP) (:ARG1/NP) (VP (VB XXX) (:ARG2/PP) (:purpose/PP))))'],
                    (':ARG1/E', '[p]'): ['empty', 'empty'],
                    (u':mod/NN', '[emergency]'): [u'(NN XXX)'],
                    (u':purpose/PP', '[treat-03]'): [u'(PP (IN for) (NP (NN XXX)))'],
                    (u':ARG0/NP', '[service]'): [u'(NP (DT the) (:location/NNP) (:mod/NN) (NNS XXX))'],
                    (u':quant/NNS', '[11]'): [u'(NNS XXX)'],
                    (u':ARG2/ADJP', '[wound-01]'): [u'(ADJP (JJ due) (PP (TO to) (NP (:mod/JJ) (NNS XXX))))'],
                    (u':mod/JJ', '[minor]'): [u'(JJ XXX)'],
                    (u':mod/ADVP', '[altogether]'): [u'(ADVP (RB XXX))']
                },
                'adjoining':{
                    (u':ARG1/SBAR', '[send-01]', 'passive', 'past perfect'): [u'(VP (VB be) (VP*))',
                                                   u'(VP (VB have) (VP*))'],
                    (u':purpose/PP', '[treat-03]'): [u'(NP (NP*) (:ARG2/ADJP))']
                }
            },
            'tag': {
                'initial': {
                    u':root/ROOT': [u'(ROOT (S (:ARG0/NP) (VP (VB XXX) (:ARG1/SBAR)) (. .)))']
                },
                'substitution':{
                    u':purpose/PP': [u'(PP (IN for) (NP (NN XXX)))'],
                    u':mod/ADVP': [u'(ADVP (RB XXX))'],
                    u':ARG1/SBAR': [u'(SBAR (IN that) (S (:mod/ADVP) (:ARG1/NP) (VP (VB XXX) (:ARG2/PP) (:purpose/PP))))'],
                    u':ARG0/NP': [u'(NP (DT the) (:location/NNP) (:mod/NN) (NNS XXX))'],
                    u':quant/NNS': [u'(NNS XXX)'], u':ARG1/NP': [u'(NP (:quant/NNS) (NNS XXX))'],
                    u':mod/NN': [u'(NN XXX)'],
                    ':ARG1/E': ['empty', 'empty'],
                    u':location/NNP': [u'(NNP XXX)'],
                    u':ARG2/ADJP': [u'(ADJP (JJ due) (PP (TO to) (NP (:mod/JJ) (NNS XXX))))'],
                    u':ARG2/PP': [u'(PP (TO to) (NP (NN XXX)))'],
                    u':mod/JJ': [u'(JJ XXX)']
                },
                'adjoining':{
                    u':ARG1/SBAR': [u'(VP (VB be) (VP*))',
                                    u'(VP (VB have) (VP*))'],
                    u':purpose/PP': [u'(NP (NP*) (:ARG2/ADJP))']
                }
            }}

        self.assertDictEqual(original, {'tag':tag, 'ltag':ltag})

    def test_spec2(self):
        text = 'The Tokyo Stock Exchange said that this company will officially be listed on the stock exchange on August 8.'
        amr = """(s / say-01
                  :ARG0 (o / organization :wiki "Tokyo_Stock_Exchange"
                        :name (n / name :op1 "Tokyo" :op2 "Stock" :op3 "Exchange"))
                  :ARG1 (l / list-01
                        :ARG1 (c / company
                              :mod (t / this))
                        :ARG2 (e / exchange-01
                              :ARG1 (s2 / stock-01))
                        :mod (o2 / official)
                        :time (d / date-entity :month 8 :day 8)))"""

        alignments, info = self.aligner.freq_rules(amr, text)
        inducer = RuleInducer(text, amr, info, alignments)
        id2subtrees, id2rule, adjtrees = inducer.freq_rules()

        tag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        ltag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        tag, ltag = inducer.prettify(id2subtrees, id2rule, adjtrees, tag, ltag)

        original = {
            'ltag': {
                'initial': {
                    (u':root/ROOT', '[say-01]', 'active', 'simple past'): [u'(ROOT (S (:ARG0/NP) (VP (VB XXX) (:ARG1/SBAR)) (. .)))']
                },
                'substitution':{
                    (u':mod/DT', '[this]'): [u'(DT XXX)'],
                    (u':time/PP', '[date-entity, :month, :day]'): [u'(PP (IN on) (NP (NNP XXX) (CD XXX)))'],
                    (u':ARG0/NP', '[organization, :name, :op1, :op2, :op3]'): [u'(NP (DT the) (NNP XXX) (NNP XXX) (NNP XXX))'],
                    (u':ARG1/SBAR', '[list-01]', 'passive', 'simple future'): [u'(SBAR (IN that) (S (:ARG1/NP) (VP (VB XXX) (:ARG2/PP))))'],
                    (u':mod/ADVP', '[official]'): [u'(ADVP (RB XXX))'],
                    (u':ARG2/PP', '[exchange-01]'): [u'(PP (IN on) (NP (DT the) (:ARG1/NN) (NN XXX)))'],
                    (u':ARG1/NN', '[stock-01]'): [u'(NN XXX)'],
                    (u':ARG1/NP', '[company]'): [u'(NP (:mod/DT) (NN XXX))']
                },
                'adjoining':{
                    (u':ARG1/SBAR', '[list-01]', 'passive', 'simple future'): [u'(VP (VB be) (VP*))',
                                                   u'(VP (MD will) (:mod/ADVP) (VP*))'],
                    (u':ARG2/PP', '[exchange-01]'): [u'(NP (NP*) (:time/PP))']
                }
            },
            'tag': {
                'initial': {
                    u':root/ROOT': [u'(ROOT (S (:ARG0/NP) (VP (VB XXX) (:ARG1/SBAR)) (. .)))']
                },
                'substitution':{
                    u':time/PP': [u'(PP (IN on) (NP (NNP XXX) (CD XXX)))'],
                    u':mod/ADVP': [u'(ADVP (RB XXX))'],
                    u':ARG1/SBAR': [u'(SBAR (IN that) (S (:ARG1/NP) (VP (VB XXX) (:ARG2/PP))))'],
                    u':ARG0/NP': [u'(NP (DT the) (NNP XXX) (NNP XXX) (NNP XXX))'],
                    u':ARG1/NN': [u'(NN XXX)'], u':ARG1/NP': [u'(NP (:mod/DT) (NN XXX))'],
                    u':mod/DT': [u'(DT XXX)'],
                    u':ARG2/PP': [u'(PP (IN on) (NP (DT the) (:ARG1/NN) (NN XXX)))']
                },
                'adjoining':{
                    u':ARG1/SBAR': [u'(VP (VB be) (VP*))',
                                    u'(VP (MD will) (:mod/ADVP) (VP*))'],
                    u':ARG2/PP': [u'(NP (NP*) (:time/PP))']
                }
            }}

        self.assertDictEqual(original, {'tag':tag, 'ltag':ltag})

    def test_spec3(self):
        text = 'I headed straight for the center of activities, but in actual fact traffic was being controlled as early as 4 o\'clock, and they had already started limiting the crowds entering the sports center.'
        amr = """(c / contrast-01
                      :ARG1 (h / head-02
                            :ARG0 (i / i)
                            :ARG1 (c6 / center
                                  :mod (a2 / activity-06))
                            :ARG1-of (s2 / straight-04))
                      :ARG2 (a / and
                            :op1 (c2 / control-01
                                  :ARG1 (t / traffic)
                                  :prep-in (f / fact
                                        :ARG1-of (a3 / actual-02))
                                  :time (d / date-entity :time "4:00"
                                        :mod (e / early)))
                            :op2 (s / start-01
                                  :ARG0 (t2 / they)
                                  :ARG1 (l2 / limit-01
                                        :ARG1 (c4 / crowd
                                              :ARG0-of (e2 / enter-01
                                                    :ARG1 (c5 / center
                                                          :mod (s3 / sport)))))
                                  :time (a4 / already))))"""

        alignments, info = self.aligner.freq_rules(amr, text)
        inducer = RuleInducer(text, amr, info, alignments)
        id2subtrees, id2rule, adjtrees = inducer.freq_rules()

        tag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        ltag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        tag, ltag = inducer.prettify(id2subtrees, id2rule, adjtrees, tag, ltag)

        original = {
            'ltag': {
                'initial': {
                    (u':root/ROOT', '[contrast-01]'): [u'(ROOT (S (S (:ARG0/NP) (VP (:ARG1/VP) (, ,) (CC XXX) (:op1/VP))) (, ,) (:ARG2/CC) (:op2/S) (. .)))']
                },
                'substitution':{
                    (u':ARG0/NP', '[they]'): [u'(NP (PRP XXX))'],
                    (u':time/PP', '[date-entity, :time, :mod]'): [u"(PP (IN as) (NP (NP (JJ XXX)) (PP (IN as) (NP (CD XXX) (RB o'clock)))))"],
                    (u':ARG1/PP', '[traffic]'): [u'(PP (IN in) (NP (:ARG1-of/JJ) (:prep-in/NN) (NN XXX)))'],
                    (u':ARG1/NP', '[center]'): [u'(NP (DT the) (:mod/NNS) (NN XXX))'],
                    (u':mod/PP', '[activity-06]'): [u'(PP (IN of) (NP (NNS XXX)))'],
                    (u':ARG1-of/ADVP', '[straight-04]'): [u'(ADVP (RB XXX))'],
                    (u':ARG0-of/S', '[enter-01]'): [u'(S (VP (VB XXX) (:ARG1/NP)))'],
                    (u':ARG1/PP', '[center]'): [u'(PP (IN for) (NP (NP (DT the) (NN XXX)) (:mod/PP)))'],
                    (u':op2/S', '[start-01]'): [u'(S (:ARG0/NP) (VP (VB XXX) (:ARG1/S)))'],
                    (u':ARG1/VP', '[head-02]'): [u'(VP (VB XXX) (:ARG1-of/ADVP) (:ARG1/PP))'],
                    (u':op1/VP', '[control-01]'): [u'(VP (VB XXX) (:time/PP))'],
                    (u':time/ADVP', '[already]'): [u'(ADVP (RB XXX))'],
                    (u':ARG1/NP', '[crowd]'): [u'(NP (DT the) (NNS XXX))'],
                    (u':ARG2/CC', '[and]'): [u'(CC XXX)'],
                    (u':mod/NNS', '[sport]'): [u'(NNS XXX)'],
                    (u':ARG1-of/JJ', '[actual-02]'): [u'(JJ XXX)'],
                    (u':prep-in/NN', '[fact]'): [u'(NN XXX)'],
                    (u':ARG1/S', '[limit-01]'): [u'(S (VP (VB XXX) (:ARG1/NP) (:ARG0-of/S)))'],
                    (u':ARG0/NP', '[i]'): [u'(NP (PRP XXX))']
                },
                'adjoining':{
                    (u':op2/S', '[start-01]'): [u'(VP (VB have) (:time/ADVP) (VP*))'],
                    (u':op1/VP', '[control-01]'): [u'(VP (VB be) (VP*))',
                                                   u'(VP (:ARG1/PP) (VBD be) (VP*))'],
                    (u':time/PP', '[date-entity, :time, :mod]'): []
                }
            },
            'tag': {
                'initial': {
                    u':root/ROOT': [u'(ROOT (S (S (:ARG0/NP) (VP (:ARG1/VP) (, ,) (CC XXX) (:op1/VP))) (, ,) (:ARG2/CC) (:op2/S) (. .)))']
                },
                'substitution':{
                    u':time/PP': [u"(PP (IN as) (NP (NP (JJ XXX)) (PP (IN as) (NP (CD XXX) (RB o'clock)))))"],
                    u':ARG1/S': [u'(S (VP (VB XXX) (:ARG1/NP) (:ARG0-of/S)))'],
                    u':mod/NNS': [u'(NNS XXX)'],
                    u':ARG1-of/ADVP': [u'(ADVP (RB XXX))'],
                    u':prep-in/NN': [u'(NN XXX)'],
                    u':ARG1/PP': [u'(PP (IN for) (NP (NP (DT the) (NN XXX)) (:mod/PP)))',
                                  u'(PP (IN in) (NP (:ARG1-of/JJ) (:prep-in/NN) (NN XXX)))'],
                    u':time/ADVP': [u'(ADVP (RB XXX))'],
                    u':ARG0-of/S': [u'(S (VP (VB XXX) (:ARG1/NP)))'],
                    u':op1/VP': [u'(VP (VB XXX) (:time/PP))'],
                    u':ARG1/NP': [u'(NP (DT the) (NNS XXX))',
                                  u'(NP (DT the) (:mod/NNS) (NN XXX))'],
                    u':ARG1-of/JJ': [u'(JJ XXX)'],
                    u':mod/PP': [u'(PP (IN of) (NP (NNS XXX)))'],
                    u':ARG0/NP': [u'(NP (PRP XXX))', u'(NP (PRP XXX))'],
                    u':ARG1/VP': [u'(VP (VB XXX) (:ARG1-of/ADVP) (:ARG1/PP))'],
                    u':ARG2/CC': [u'(CC XXX)'],
                    u':op2/S': [u'(S (:ARG0/NP) (VP (VB XXX) (:ARG1/S)))']
                },
                'adjoining':{
                    u':op2/S': [u'(VP (VB have) (:time/ADVP) (VP*))'],
                    u':op1/VP': [u'(VP (VB be) (VP*))',
                                 u'(VP (:ARG1/PP) (VB be) (VP*))']
                }
            }}

        self.assertDictEqual(original, {'tag':tag, 'ltag':ltag})

    def test_spec4(self):
        text= 'The family planning policy is extremely stupid, brings disasters to both the country and the people, and is totally void of conscience!'
        amr = """(a3 / and
                      :op1 (s / stupid
                            :degree (e / extreme)
                            :domain (p / policy
                                  :topic (p2 / plan-01
                                        :ARG1 (f / family))))
                      :op2 (b2 / bring-01
                            :ARG0 p
                            :ARG1 (d / disaster)
                            :ARG2 (a2 / and
                                  :op1 (c2 / country)
                                  :op2 (p3 / person)))
                      :op3 (v / void-03
                            :ARG1 p
                            :ARG2 (c / conscience)
                            :degree (t / total)))"""

        alignments, info = self.aligner.freq_rules(amr, text)
        inducer = RuleInducer(text, amr, info, alignments)
        id2subtrees, id2rule, adjtrees = inducer.freq_rules()

        tag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        ltag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        tag, ltag = inducer.prettify(id2subtrees, id2rule, adjtrees, tag, ltag)

        original = {
            'ltag': {
                'initial': {(u':root/ROOT', '[and]'): [
                    u'(ROOT (S (:domain/NP) (VP (:op1/VP) (, ,) (VP (:op2/VBZ) (:ARG1/NP) (PP (TO to) (NP (CC both) (:op1/NP) (CC XXX) (:op2/NP)))) (, ,) (:ARG2/CC) (:ARG2/VP)) (. !)))']
                },
                'substitution':{
                    (u':degree/RB', '[extreme]'): [u'(RB XXX)'],
                    (':ARG0/E', '[p]'): ['empty'],
                    (u':op1/VP', '[stupid]'): [u'(VP (VBZ is) (ADJP (:degree/RB) (JJ XXX)))'],
                    (u':domain/NP', '[policy]'): [u'(NP (DT the) (:ARG1/NN) (:topic/NN) (NN XXX))'],
                    (u':topic/NN', '[plan-01]'): [u'(NN XXX)'],
                    (u':ARG1/NP', '[disaster]'): [u'(NP (NNS XXX))'],
                    (u':ARG1/NN', '[family]'): [u'(NN XXX)'],
                    (':ARG1/E', '[p]'): ['empty'],
                    (u':op2/NP', '[person]'): [u'(NP (DT the) (NNS XXX))'],
                    (u':ARG2/CC', '[and]'): [u'(CC XXX)'],
                    (u':degree/RB', '[total]'): [u'(RB XXX)'],
                    (u':op3/NN', '[void-03]'): [u'(NN XXX)'],
                    (u':op2/VBZ', '[bring-01]'): [u'(VB XXX)'],
                    (u':op1/NP', '[country]'): [u'(NP (DT the) (NN XXX))'],
                    (u':ARG2/VP', '[conscience]'): [u'(VP (VBZ is) (ADJP (:degree/RB) (:op3/NN)) (PP (IN of) (NP (NN XXX))))']
                },
                'adjoining':{}
            },
            'tag': {
                'initial': {
                    u':root/ROOT': [u'(ROOT (S (:domain/NP) (VP (:op1/VP) (, ,) (VP (:op2/VBZ) (:ARG1/NP) (PP (TO to) (NP (CC both) (:op1/NP) (CC XXX) (:op2/NP)))) (, ,) (:ARG2/CC) (:ARG2/VP)) (. !)))']
                },
                'substitution':{
                    u':op2/VBZ': [u'(VBZ XXX)'],
                    u':topic/NN': [u'(NN XXX)'],
                    u':op2/NP': [u'(NP (DT the) (NNS XXX))'],
                    u':ARG2/VP': [u'(VP (VBZ is) (ADJP (:degree/RB) (:op3/NN)) (PP (IN of) (NP (NN XXX))))'],
                    u':ARG1/NN': [u'(NN XXX)'],
                    ':ARG0/E': ['empty'],
                    u':ARG1/NP': [u'(NP (NNS XXX))'],
                    u':domain/NP': [u'(NP (DT The) (:ARG1/NN) (:topic/NN) (NN XXX))'],
                    ':ARG1/E': ['empty'],
                    u':op1/VP': [u'(VP (VBZ is) (ADJP (:degree/RB) (JJ XXX)))'],
                    u':op1/NP': [u'(NP (DT the) (NN XXX))'],
                    u':degree/RB': [u'(RB XXX)', u'(RB XXX)'],
                    u':ARG2/CC': [u'(CC XXX)'],
                    u':op3/NN': [u'(NN XXX)']
                },
                'adjoining':{}
            }}

        self.assertDictEqual(original, {'tag':tag, 'ltag':ltag})

    def test_spec5(self):
        text = 'The most terrible thing is not the government officials, but the power that lies in the hands of these officials.'
        amr = """(c / contrast-01
                      :ARG1 (t2 / terrible-01 :polarity -
                            :ARG1 (p2 / person
                                  :ARG0-of (h2 / have-org-role-91
                                        :ARG1 (g / government-organization
                                              :ARG0-of (g2 / govern-01))
                                        :ARG2 (o2 / official)))
                            :degree (m / most))
                      :ARG2 (t3 / terrible-01
                            :ARG1 (p / power
                                  :ARG1-of (l / lie-07
                                        :ARG2 (h / hand
                                              :part-of p2)))
                            :degree (m2 / most)))"""

        alignments, info = self.aligner.freq_rules(amr, text)
        inducer = RuleInducer(text, amr, info, alignments)
        id2subtrees, id2rule, adjtrees = inducer.freq_rules()

        tag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        ltag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        tag, ltag = inducer.prettify(id2subtrees, id2rule, adjtrees, tag, ltag)

        original = {
            'ltag': {
                'initial': {
                    (u':root/ROOT', '[contrast-01]', 'active', 'simple present'): [u'(ROOT (S (:ARG1/NP) (VP (VB be) (NP (:polarity/RB) (:ARG1/NP) (, ,) (CC XXX) (:ARG1/NP))) (. .)))']
                },
                'substitution':{
                    (u':part-of/PP', '[p2]'): [u'(PP (IN of) (NP (DT XXX) (NNS XXX)))'],
                    (u':ARG1/NN', '[government-organization, :ARG0-of]'): [u'(NN XXX)'],
                    (u':ARG1-of/SBAR', '[lie-07]', 'active', 'simple present'): [u'(SBAR (WHNP (WDT that)) (S (VP (VB XXX) (:ARG2/PP))))'],
                    (u':ARG1/NP', '[power]'): [u'(NP (DT the) (NN XXX))'],
                    (u':polarity/RB', '[-]'): [u'(RB XXX)'],
                    (u':ARG2/PP', '[hand]'): [u'(PP (IN in) (NP (DT the) (NNS XXX)))'],
                    (':ARG2/E', '[terrible-01, :degree]'): ['empty'],
                    (u':ARG1/NP', '[person, :ARG0-of, :ARG2]'): [u'(NP (DT the) (:ARG1/NN) (NNS XXX))'],
                    (u':ARG1/NP', '[terrible-01]'): [u'(NP (DT the) (ADJP (:degree/RBS) (JJ XXX)) (NN thing))'],
                    (u':degree/RBS', '[most]'): [u'(RBS XXX)']
                },
                'adjoining':{
                    (u':ARG1/NP', '[power]'): [u'(NP (NP*) (:ARG1-of/SBAR))'],
                    (u':ARG2/PP', '[hand]'): [u'(NP (NP*) (:part-of/PP))']
                }
            },
            'tag': {
                'initial': {
                    u':root/ROOT': [u'(ROOT (S (:ARG1/NP) (VP (VB be) (NP (:polarity/RB) (:ARG1/NP) (, ,) (CC XXX) (:ARG1/NP))) (. .)))']
                },
                'substitution':{
                    u':ARG1-of/SBAR': [u'(SBAR (WHNP (WDT that)) (S (VP (VB XXX) (:ARG2/PP))))'],
                    u':degree/RBS': [u'(RBS XXX)'],
                    u':ARG1/NN': [u'(NN XXX)'],
                    u':ARG1/NP': [u'(NP (DT the) (:ARG1/NN) (NNS XXX))',
                                  u'(NP (DT the) (ADJP (:degree/RBS) (JJ XXX)) (NN thing))',
                                  u'(NP (DT the) (NN XXX))'],
                    u':part-of/PP': [u'(PP (IN of) (NP (DT XXX) (NNS XXX)))'],
                    ':ARG2/E': ['empty'],
                    u':ARG2/PP': [u'(PP (IN in) (NP (DT the) (NNS XXX)))'],
                    u':polarity/RB': [u'(RB XXX)']
                },
                'adjoining':{
                    u':ARG1/NP': [u'(NP (NP*) (:ARG1-of/SBAR))'],
                    u':ARG2/PP': [u'(NP (NP*) (:part-of/PP))']
                }
            }}

        self.assertDictEqual(original, {'tag':tag, 'ltag':ltag})

    def test_spec6(self):
        text = 'Pledge to fight to the death defending the Diaoyu Islands and the related islands.'
        amr = """(p / pledge-01 :mode imperative
                      :ARG0 (y / you)
                      :ARG2 (f / fight-01
                            :ARG0 y
                            :ARG2 (d2 / defend-01
                                  :ARG0 y
                                  :ARG1 (a / and
                                        :op1 (i / island :wiki "Senkaku_Islands" :name (n / name :op1 "Diaoyu" :op2 "Islands"))
                                        :op2 (i2 / island
                                              :ARG1-of (r / relate-01
                                                    :ARG2 i))))
                            :manner (d / die-01
                                  :ARG1 y)))"""

        alignments, info = self.aligner.freq_rules(amr, text)
        inducer = RuleInducer(text, amr, info, alignments)
        id2subtrees, id2rule, adjtrees = inducer.freq_rules()

        tag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        ltag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        tag, ltag = inducer.prettify(id2subtrees, id2rule, adjtrees, tag, ltag)

        original = {
            'ltag': {
                'initial': {
                    (u':root/ROOT', '[pledge-01]'): [u'(ROOT (FRAG (NP (NN XXX)) (:ARG2/S) (. .)))']
                },
                'substitution':{
                    (u':ARG1-of/JJ', '[relate-01]'): [u'(JJ XXX)'],
                    (':ARG0/E', '[y]'): ['empty', 'empty'],
                    (':ARG0/E', '[you]'): ['empty'],
                    (u':ARG1/CC', '[and]'): [u'(CC XXX)'],
                    (u':ARG2/S', '[fight-01]'): [u'(S (VP (TO to) (VP (VB XXX) (:manner/PP))))'],
                    (':op2/E', '[island]'): ['empty'],
                    (':ARG1/E', '[y]'): ['empty'],
                    (':ARG2/E', '[i]'): ['empty'],
                    (u':op1/NP', '[island, :name, :op1, :op2]'): [u'(NP (NP (DT the) (NNP XXX) (NNPS XXX)) (:ARG1/CC) (NP (DT the) (:ARG1-of/JJ) (NNS XXX)))'],
                    (u':ARG2/VP', '[defend-01]'): [u'(VP (VB XXX) (:op1/NP))'],
                    (u':manner/PP', '[die-01]'): [u'(PP (TO to) (NP (NP (DT the) (NN XXX)) (:ARG2/VP)))']
                },
                'adjoining':{}
            },
            'tag': {
                'initial': {
                    u':root/ROOT': [u'(ROOT (FRAG (NP (NN XXX)) (:ARG2/S) (. .)))']
                },
                'substitution':{
                    u':op1/NP': [u'(NP (NP (DT the) (NNP XXX) (NNPS XXX)) (:ARG1/CC) (NP (DT the) (:ARG1-of/JJ) (NNS XXX)))'],
                    ':op2/E': ['empty'],
                    u':ARG2/VP': [u'(VP (VB XXX) (:op1/NP))'],
                    u':ARG1-of/JJ': [u'(JJ XXX)'],
                    ':ARG2/E': ['empty'],
                    u':ARG1/CC': [u'(CC XXX)'],
                    u':manner/PP': [u'(PP (TO to) (NP (NP (DT the) (NN XXX)) (:ARG2/VP)))'],
                    ':ARG1/E': ['empty'],
                    ':ARG0/E': ['empty', 'empty', 'empty'],
                    u':ARG2/S': [u'(S (VP (TO to) (VP (VB XXX) (:manner/PP))))']
                },
                'adjoining':{}
            }}

        self.assertDictEqual(original, {'tag':tag, 'ltag':ltag})

    def test_spec7(self):
        text = 'Audit cadres must require themselves to adhere to the standards they apply when auditing others .'

        amr = """(o2 / obligate-01
                      :ARG2 (r / require-01
                            :ARG0 (c / cadre
                                  :ARG0-of (a / audit-01))
                            :ARG1 (a2 / adhere-02
                                  :ARG0 c
                                  :ARG1 (s / standard
                                        :ARG1-of (a3 / apply-02
                                              :ARG0 c
                                              :ARG2 (a4 / audit-01
                                                    :ARG0 c
                                                    :ARG1 (o / other)))))
                            :ARG2 c))"""

        alignments, info = self.aligner.freq_rules(amr, text)
        inducer = RuleInducer(text, amr, info, alignments)
        id2subtrees, id2rule, adjtrees = inducer.freq_rules()

        tag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        ltag={'initial':{}, 'substitution':{}, 'adjoining':{}}
        tag, ltag = inducer.prettify(id2subtrees, id2rule, adjtrees, tag, ltag)

        original = {
            'ltag': {
                'initial': {
                    (u':root/ROOT', '[obligate-01]', 'active', 'simple present'): [u'(ROOT (S (:ARG0/NP) (VP (MD XXX) (:ARG2/VP)) (. .)))']
                },
                'adjoining': {
                    (u':ARG1/S', '[adhere-02]', 'active', 'infinitive'): [u'(VP (TO to) (VP*))'],
                    (u':ARG1/PP', '[standard]'): [u'(NP (NP*) (:ARG1-of/SBAR))']
                },
                'substitution': {
                    (':ARG2/E', '[c]'): ['empty'],
                    (u':ARG1/SBAR', '[other]'): [u'(SBAR (WHADVP (WRB when)) (FRAG (NP (:ARG2/NN) (NNS XXX))))'],
                    (':ARG0/E', '[c]'): ['empty'],
                    (u':ARG2/NN', '[audit-01]'): [u'(NN XXX)'],
                    (u':ARG0/NP', '[c]'): [u'(NP (PRP XXX))', u'(NP (PRP XXX))'],
                    (u':ARG1-of/SBAR', '[apply-02]', 'active', 'simple present'): [u'(SBAR (S (:ARG0/NP) (VP (VB XXX))))'],
                    (u':ARG1/PP', '[standard]'): [u'(PP (TO to) (NP (DT the) (NNS XXX)))'],
                    (u':ARG2/VP', '[require-01]', 'active', 'infinitive'): [u'(VP (VB XXX) (:ARG1/S))'],
                    (u':ARG0-of/NNP', '[audit-01]'): [u'(NNP XXX)'],
                    (u':ARG0/NP', '[cadre]'): [u'(NP (:ARG0-of/NNP) (NNS XXX))'],
                    (u':ARG1/S', '[adhere-02]', 'active', 'infinitive'): [u'(S (:ARG0/NP) (VP (VB XXX) (:ARG1/PP) (:ARG1/SBAR)))']
                }
            },
            'tag': {
                'initial': {
                    u':root/ROOT': [u'(ROOT (S (:ARG0/NP) (VP (MD XXX) (:ARG2/VP)) (. .)))']
                },
                'adjoining': {
                    u':ARG1/S': [u'(VP (TO to) (VP*))'],
                    u':ARG1/PP': [u'(NP (NP*) (:ARG1-of/SBAR))']
                },
                'substitution': {
                    u':ARG0-of/NNP': [u'(NNP XXX)'],
                    u':ARG1/S': [u'(S (:ARG0/NP) (VP (VB XXX) (:ARG1/PP) (:ARG1/SBAR)))'],
                    u':ARG1-of/SBAR': [u'(SBAR (S (:ARG0/NP) (VP (VB XXX))))'],
                    u':ARG1/SBAR': [u'(SBAR (WHADVP (WRB when)) (FRAG (NP (:ARG2/NN) (NNS XXX))))'],
                    u':ARG0/NP': [u'(NP (:ARG0-of/NNP) (NNS XXX))', u'(NP (PRP XXX))', u'(NP (PRP XXX))'],
                    u':ARG2/VP': [u'(VP (VB XXX) (:ARG1/S))'],
                    ':ARG0/E': ['empty'],
                    ':ARG2/E': ['empty'],
                    u':ARG2/NN': [u'(NN XXX)'],
                    u':ARG1/PP': [u'(PP (TO to) (NP (DT the) (NNS XXX)))']
                }
            }
        }

        self.assertDictEqual(original, {'tag':tag, 'ltag':ltag})

    def test_spec8(self):
        text = 'Pierre Vinken , 61 years old , will join the board as a nonexecutive director Nov. 29 .'

        amr = """(j / join-01
                  :ARG0 (p / person :wiki -
                        :name (p2 / name :op1 "Pierre" :op2 "Vinken")
                        :age (t / temporal-quantity :quant 61
                              :unit (y / year)))
                  :ARG1 (b / board
                        :ARG1-of (h / have-org-role-91
                              :ARG0 p
                              :ARG2 (d2 / director
                                    :mod (e / executive :polarity -))))
                  :time (d / date-entity :month 11 :day 29))"""

        self.assertEqual('', 'thiago')

    def test_spec9(self):
        text = 'If that is the case, after the child is born, the father will go to the mother\'s home, and present the family matriarch with gifts, asking to be accepted as the father.'

        amr = """(a / and
                      :op1 (g / go-02
                            :ARG0 (p3 / person
                                  :ARG0-of (h3 / have-rel-role-91
                                        :ARG1 c
                                        :ARG2 (f / father)))
                            :ARG4 (h / home
                                  :poss (p4 / person
                                        :ARG0-of (h4 / have-rel-role-91
                                              :ARG1 c
                                              :ARG2 (m / mother)))))
                      :op2 (p / present-01
                            :ARG0 p3
                            :ARG1 (g2 / gift)
                            :ARG2 (p2 / person
                                  :ARG0-of (h2 / have-org-role-91
                                        :ARG1 (f2 / family)
                                        :ARG2 (m2 / matriarch))))
                      :op3 (a3 / ask-02
                            :ARG0 p3
                            :ARG1 (a4 / accept-01
                                  :ARG1 h3))
                      :time (a2 / after
                            :op1 (b / bear-02
                                  :ARG1 (c / child)))
                      :condition (t / that)) """

        self.assertEqual('', 'thiago')

    def test_spec10(self):
        text = 'According to the international reports on January 11 , eBay announced that it will acquire online ticket website StubHub for 310 million US dollars in cash to further expand its influence on electronic commerce .'

        amr = """(s / say-01
                  :ARG0 (r / report-01
                        :mod (i2 / international))
                  :ARG1 (a / announce-01
                        :ARG0 (c / company :wiki "EBay"
                              :name (n / name :op1 "eBay"))
                        :ARG1 (a2 / acquire-01
                              :ARG0 c
                              :ARG1 (c2 / company :wiki "StubHub"
                                    :name (n2 / name :op1 "StubHub")
                                    :mod (w / website
                                          :purpose (t / ticket)
                                          :mod (o / online)))
                              :ARG3 (m / monetary-quantity :quant 310000000
                                    :unit (d / dollar)
                                    :mod (c3 / country :wiki "United_States"
                                          :name (n3 / name :op1 "US"))
                                    :consist-of (c4 / cash))
                              :purpose (e / expand-01
                                    :ARG0 c
                                    :ARG1 (i / influence-01
                                          :ARG0 c
                                          :ARG1 (c5 / commerce
                                                :mod (e2 / electronic)))
                                    :degree (f / further))))
                  :time (d2 / date-entity :month 1 :day 11))"""

        self.assertEqual('', 'thiago')

if __name__ == '__main__':
    unittest.main()

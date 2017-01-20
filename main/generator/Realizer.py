__author__ = 'thiagocastroferreira'

import copy
import sys
sys.path.append("/Users/thiagocastroferreira/workspace/simplenlg/SimpleNLG-4.4.8.jar")
sys.path.append("/home/tcastrof/amr/simplenlg/SimpleNLG-4.4.8.jar")
sys.path.append('../../')

# SimpleNLG will do the NLG generation
from simplenlg.framework import NLGFactory, CoordinatedPhraseElement, ListElement, PhraseElement
from simplenlg.lexicon import Lexicon
from simplenlg.realiser.english import Realiser

from simplenlg.framework import *
from simplenlg.lexicon import *
from simplenlg.realiser.english import *
from simplenlg.phrasespec import *
from simplenlg.features import *

from java.lang import Boolean, String

from main.grammars.ERG import ERGFactory
from Generator import Generator

import main.utils as utils
import properties as prop

class Realizer(object):
    def __init__(self):
        verb2noun, noun2verb, verb2actor, actor2verb = utils.noun_verb(prop.morph_verb)
        self.verb2noun = verb2noun
        self.verb2actor = verb2actor

        sub2word = utils.subgraph_word(prop.verbalization)
        self.sub2word = sub2word

        lexicon = Lexicon.getDefaultLexicon()
        self.nlgFactory = NLGFactory(lexicon)
        self.realiser = Realiser(lexicon)

    def create_clause(self, subject, vp, _object, frontmodifiers, complements):
        phrase = self.nlgFactory.createClause()
        phrase.setSubject(subject)
        phrase.setVerbPhrase(vp)

        if _object != None:
            phrase.setObject(_object)

        for frontmodifier in frontmodifiers:
            phrase = self.add_frontmodifier(phrase, frontmodifier)

        for complement in complements:
            phrase = self.add_complement(phrase, complement)
        return phrase

    def create_np(self, determiner, head, number, premodifiers, postmodifiers):
        np = self.nlgFactory.createNounPhrase()
        np.setNoun(head)

        if determiner != '':
            np.setDeterminer(determiner)

        if number == 'singular':
            np.setFeature(Feature.NUMBER, NumberAgreement.SINGULAR)
        elif number == 'plural':
            np.setFeature(Feature.NUMBER, NumberAgreement.PLURAL)

        for premodifier in premodifiers:
            np = self.add_premodifier(np, premodifier)

        for postmodifier in postmodifiers:
            np = self.add_postmodifier(np, postmodifier)

        return np

    def create_vp(self, sentence):
        verb = sentence['verb']
        voice = sentence['voice']
        tense = sentence['tense']
        perfect = sentence['perfect']
        form = sentence['form']
        modal = sentence['modal']

        vp = self.nlgFactory.createVerbPhrase()
        vp.setVerb(verb)

        if tense=="past":
            vp.setFeature(Feature.TENSE, Tense.PAST)
        elif tense=="present":
            vp.setFeature(Feature.TENSE, Tense.PRESENT)
        elif tense=="future":
            vp.setFeature(Feature.TENSE, Tense.FUTURE)

        if voice=="active":
            vp.setFeature(Feature.PASSIVE, Boolean(False))
        else:
            vp.setFeature(Feature.PASSIVE, Boolean(True))

        if perfect:
            vp.setFeature(Feature.PERFECT, Boolean(True))
        else:
            vp.setFeature(Feature.PERFECT, Boolean(False))

        if form == 'negative':
            vp.setFeature(Feature.NEGATED, Boolean(True))
        elif form == 'infinitive':
            vp.setFeature(Feature.FORM, Form.INFINITIVE)

        if modal == 'possible':
            vp.setFeature(Feature.MODAL, "can")
        elif modal == 'obligate':
            vp.setFeature(Feature.MODAL, "must")
        elif modal == 'permit':
            vp.setFeature(Feature.MODAL, "may")
        elif modal == 'recommend':
            vp.setFeature(Feature.MODAL, "should")
        return vp

    def create_pp(self, preposition, np):
        pp = self.nlgFactory.createPrepositionPhrase()
        pp.addComplement(np)
        pp.setPreposition(preposition)
        return pp

    def create_adjp(self, adjective):
        adjp = self.nlgFactory.createAdjectivePhrase(adjective)
        return adjp

    def create_advp(self, adverb):
        advp = self.nlgFactory.createAdverbPhrase(adverb)
        return advp
    
    def create_possessive(self):
        np = self.nlgFactory.createNounPhrase()
        np.setFeature(Feature.PRONOMINAL, Boolean(True))
        np.setFeature(Feature.POSSESSIVE, Boolean(True))
        return np

    def add_complement(self, phrase, complement):
        phrase.addComplement(complement)
        return phrase

    def add_premodifier(self, phrase, premodifier):
        phrase.addPreModifier(premodifier)
        return phrase

    def add_postmodifier(self, phrase, postmodifier):
        phrase.addPostModifier(postmodifier)
        return phrase

    def add_frontmodifier(self, phrase, frontmodifier):
        phrase.addFrontModifier(frontmodifier)
        return phrase

    def add_complementiser(self, phrase, complement):
        phrase.setFeature(Feature.COMPLEMENTISER, complement)
        return phrase

    def process_np(self, root):
        determiner, premodifiers, head, postmodifiers = '', [], '', []
        for node in self.tree.edges[root]:
            if self.tree.nodes[node].type == 'terminal':
                if self.tree.nodes[node].name == 'DT':
                    determiner = self.tree.nodes[node].lexicon
                elif self.tree.nodes[node].label > -1 and self.tree.nodes[node].rule_id == self.tree.nodes[root].rule_id:
                    head = self.tree.nodes[node].lexicon
                elif self.tree.nodes[node].name == 'PRP$':
                    mod = self.create_possessive()
                    premodifiers.append(mod)
                else:
                    mod = self.tree.nodes[node].lexicon
                    if head == '':
                        premodifiers.append(mod)
                    else:
                        postmodifiers.append(mod)
            else:
                mod = self.process(node)
                if mod != None:
                    if head == '':
                        premodifiers.append(mod)
                    else:
                        postmodifiers.append(mod)

        if head == '':
            head = copy.copy(determiner)
            determiner = ''
        p = self.create_np(determiner=determiner, head=head, number='singular', premodifiers=premodifiers, postmodifiers=postmodifiers)
        return p

    def process_vp(self, root, sentence):
        for node in self.tree.edges[root]:
            if self.tree.nodes[node].type == 'terminal':
                # treat modals
                if self.tree.nodes[node].name == 'MD':
                    sentence['modal'] = self.tree.nodes[node].lexicon
                # treat infinitive
                elif self.tree.nodes[node].name == 'TO':
                    sentence['form'] = 'infinitive'
                # treat negative
                elif self.tree.nodes[node].lexicon == 'not':
                    sentence['form'] = 'negative'
                elif self.tree.nodes[node].name == 'VB':
                    sentence['verb'] = self.tree.nodes[node].lexicon
#                     if self.tree.nodes[node].label > -1 and self.tree.nodes[node].rule_id == self.tree.nodes[root].rule_id:
#                         sentence['verb'] = self.tree.nodes[node].lexicon
            else:
                if self.tree.nodes[node].name == 'VP':
                    sentence = self.process_vp(node, sentence)
                else:
                    p = self.process(node)
                    if p != None:
                        rule_id = self.tree.nodes[node].rule_id
                        rule = self.synchg.rules[rule_id]
                        edge = rule.name.split('/')[0]
                        pos = self.tree.nodes[node].name

                        if 'NP' in pos:
                            if edge == ':ARG1' and sentence['voice'] == 'active':
                                sentence['object'] = p
                            else:
                                sentence['complements'].append(p)
                        elif pos == 'PP':
                            if edge == ':ARG0' and sentence['voice'] == 'passive':
                                p = p.getChildren()[1]
                                sentence['subject'] = p
                            else:
                                sentence['complements'].append(p)
                        else:
                            sentence['complements'].append(p)
        return sentence

    def process_pp(self, root):
        preposition, np = '', None
        for node in self.tree.edges[root]:
            if self.tree.nodes[node].type == 'terminal':
                preposition = self.tree.nodes[node].lexicon
            else:
                np = self.process(node)
        p = self.create_pp(preposition, np)
        return p

    def process_adjvp(self, root):
        premodifiers, head, postmodifiers = [], '', []
        for node in self.tree.edges[root]:
            if self.tree.nodes[node].type == 'terminal':
                if self.tree.nodes[node].label > -1 and self.tree.nodes[node].rule_id == self.tree.nodes[root].rule_id:
                    head = self.tree.nodes[node].lexicon
                else:
                    mod = self.tree.nodes[node].lexicon
                    if head == '':
                        premodifiers.append(mod)
                    else:
                        postmodifiers.append(mod)
            else:
                mod = self.process(node)
                if head == '':
                    premodifiers.append(mod)
                else:
                    postmodifiers.append(mod)
        if self.tree.nodes[root].name == 'ADJP':
            p = self.create_adjp(head)
        else:
            p = self.create_advp(head)

        for premodifier in premodifiers:
            self.add_premodifier(p, premodifier)

        for postmodifier in postmodifiers:
            self.add_postmodifier(p, postmodifier)
        return p

    def process_s(self, root):
        # get voice
        rule_id = self.tree.nodes[root].rule_id
        rule = self.synchg.rules[rule_id]
        voice = rule.features.voice

        sentence = {
            'subject': None,
            'object': None,
            'verb':'',
            'tense': 'present',
            'modal': '',
            'voice': voice,
            'perfect': False,
            'form': 'affirmative',
            'frontmodifiers': [],
            'complements':[]
        }

        for node in self.tree.edges[root]:
            if self.tree.nodes[node].name not in ['.', ':']:
                rule_id = self.tree.nodes[node].rule_id
                rule = self.synchg.rules[rule_id]
                
                edge = rule.name.split('/')[0]
                pos = self.tree.nodes[node].name

                if pos == 'VP':
                    sentence = self.process_vp(node, sentence)
                else:
                    p = self.process(node)

                    if 'NP' in pos:
                        if edge == ':ARG0':
                            sentence['subject'] = p
                        elif edge == ':ARG1':
                            if voice == 'active':
                                sentence['subject'] = p
                            else:
                                sentence['object'] = p
                        else:
                            if sentence['verb'] == '':
                                sentence['frontmodifiers'].append(p)
                            else:
                                sentence['complements'].append(p)
                    elif pos == 'PP':
                        if edge == ':ARG0' and self.voice == 'passive':
                            p = p.getChildren()[1]
                            sentence['subject'] = p
                        else:
                            if sentence['verb'] == '':
                                sentence['frontmodifiers'].append(p)
                            else:
                                sentence['complements'].append(p)

        vp = self.create_vp(sentence)
        subject = sentence['subject']
        object = sentence['object']
        frontmodifiers = sentence['frontmodifiers']
        complements = sentence['complements']

        p = self.create_clause(subject=subject, vp=vp, _object=object, frontmodifiers=frontmodifiers, complements=complements)
        return p

    def process_sbar(self, root):
        p, complement = None, 'that'
        for node in self.tree.edges[root]:
            if self.tree.nodes[node].name == 'S':
                p = self.process_s(node)
            elif self.tree.nodes[node].name[0] == 'W':
                child = self.tree.edges[node][0]
                complement = self.tree.nodes[child].lexicon
        if p != None:
            p = self.add_complementiser(p, complement)
        return p

    def check_coordination(self, root):
        pass

    def process(self, root):
        if self.tree.nodes[root].name == 'S':
            p = self.process_s(root)
        # SUBORDINATE CLAUSE
        elif self.tree.nodes[root].name == 'SBAR':
            p = self.process_sbar(root)
        # NOUN PHRASE
        elif 'NP' in self.tree.nodes[root].name:
            p = self.process_np(root)
        # PREPOSITIONAL PHRASES
        elif self.tree.nodes[root].name == 'PP':
            p = self.process_pp(root)
        # ADJECTIVE AND ADVERBIAL PHRASES
        elif self.tree.nodes[root].name in ['ADJP', 'ADVP']:
            p = self.process_adjvp(root)
        elif self.tree.nodes[root].name == 'FRAG':
            p = self.process(self.tree.edges[root][0])
        else:
            p = None
        return p

    def run(self, tree, synchg):
        self.tree = tree
        self.synchg = synchg

        root = tree.root
        # TO DO: treat multi sentences
        if self.tree.nodes[root].name == 'MULTI-SENTENCE':
            p = None
        else:
            root = self.tree.edges[self.tree.root][0]
            self.subject, self.vp, self.object = None, None, None
            self.complements, self.frontmodifiers = [], []

            p = self.process(root)

        if p != None:
            return self.realiser.realise(p)
        else:
            return '-'

if __name__ == '__main__':
    models = ['../data/TEST/rules/initial_rule_edges.pickle',
              '../data/TEST/rules/substitution_rule_edges.pickle',
              '../data/TEST/rules/initial_rule_edges_head.pickle',
              '../data/TEST/rules/substitution_rule_edges_head.pickle']
    verb2noun, noun2verb, verb2actor, actor2verb = utils.noun_verb('../data/morph-verbalization-v1.01.txt')
    sub2word = utils.subgraph_word('../data/verbalization-list-v1.06.txt')

    amr = """(s / shut-down-05
               :ARG0 (p / person :wiki "Hugo_Chvez"
                  :name (n / name :op1 "Hugo" :op2 "Chavez"))
               :ARG1 (i / it)
               :time (d / date-entity :year 2004))"""

    amr = """(b / boat
   :poss (h / he))"""

    factory = ERGFactory(verb2noun=verb2noun,
                         noun2verb=noun2verb,
                         verb2actor=verb2actor,
                         actor2verb=actor2verb,
                         sub2word=sub2word)

    gen = Generator(amr=amr,
                    erg_factory=factory,
                    models=models,
                    beam_n=20)

    amr, tree = gen.run()

    if tree != None:
        print 'Synchronous Grammar'
        print tree.prettify(root=tree.root)
        print 10 * '-'
        print 'Lexicalized Tree'
        print tree.prettify(root=tree.root, isRule=False)
#         print 10 * '-'
#         print 'Lexicons'
#         print tree.realize(root=tree.root)

        realizer = Realizer()
        print 10 * '-'
        print 'SimpleNLG'
        print realizer.run(tree, gen.synchg)
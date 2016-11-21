from main.old import Aligner

__author__ = 'thiagocastroferreira'

from stanford_corenlp_pywrapper import CoreNLP

import unittest
import main.utils as utils

class AlignerTest(unittest.TestCase):
    def __init__(self):
        proc = CoreNLP("coref")
        verb2noun, noun2verb, verb2actor, actor2verb = utils.noun_verb('data/morph-verbalization-v1.01.txt')
        sub2word = utils.subgraph_word('data/verbalization-list-v1.06.txt')

        self.aligner = Aligner(verb2noun, noun2verb, verb2actor, actor2verb, sub2word, proc)


    def test_1(self):
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
        self.aligner.run(amr, text)

        self.assertDictEqual({}, {1:1})

    def test_2(self):
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
        self.aligner.run(amr, text)

        self.assertDictEqual({}, {1:1})

    def test_3(self):
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
        self.aligner.run(amr, text)

        self.assertDictEqual({}, {1:1})

    def test_4(self):
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
        self.aligner.run(amr, text)

        self.assertDictEqual({}, {1:1})

    def test_5(self):
        text= 'He cut himself'
        amr = """(c / cut-01
                      :ARG0 (h / he)
                      :ARG1 h)"""
        self.aligner.run(amr, text)

        self.assertDictEqual({}, {1:1})

    def test_6(self):
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
        self.aligner.run(amr, text)

        self.assertDictEqual({}, {1:1})

    def test_7(self):
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
        self.aligner.run(amr, text)

        self.assertDictEqual({}, {1:1})

    def test_8(self):
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
            self.aligner.run(amr, text)

            self.assertDictEqual({}, {1:1})

    def test_9(self):
        text = 'What determined the position of Hong Kong as a shopping paradise ?'
        amr = """(d / determine-01
                      :ARG0 (a / amr-unknown)
                      :ARG1 (p / position-01
                            :ARG1 (c / city :wiki "Hong_Kong"
                                  :name (n / name :op1 "Hong" :op2 "Kong"))
                            :ARG2 (p2 / paradise
                                  :topic (s / shop-01))))"""
        self.aligner.run(amr, text)

        self.assertDictEqual({}, {1:1})
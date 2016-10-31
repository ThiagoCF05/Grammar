__author__ = 'thiagocastroferreira'

import unittest

from main.RuleInducer import RuleInducer

class RuleInducerTest(unittest.TestCase):
    def test_proper_np(self):
        text = 'Barack Obama'

        alignment = '0-2|0.0.0+0.0.1+0.0+0'

        tree = """(ROOT
                    (NP (NNP Barack) (NNP Obama)))"""

        amr = """(p / person
                      :name (n / name
                            :op1 \"Barack\"
                            :op2 \"Obama\"))"""

        inducer = RuleInducer(text, amr, tree, alignment)
        subtrees = inducer.run()

        original_subtrees = {1: {'nodes':{}, 'tree':{}}}
        original_subtrees[1]['nodes'] = {1: {'type': 'nonterminal', 'name': 'ROOT', 'parent': 0, 'label': 1},
                                         2: {'type': 'nonterminal', 'name': 'NP', 'parent': 1, 'label': 1},
                                         3: {'parent': 2, 'type': 'terminal', 'name': 'NNP', 'value': 'Barack', 'label': 1},
                                         4: {'parent': 2, 'type': 'terminal', 'name': 'NNP', 'value': 'Obama', 'label': 1}}
        original_subtrees[1]['tree'] = {1: [2], 2: [3, 4], 3: [], 4: []}

        self.assertDictEqual(original_subtrees, subtrees)

    def test_np(self):
        text = 'The cat'

        alignment = '1-2|0'

        tree = """(ROOT
                        (NP (DT The) (NN cat) (. .)))"""

        amr = """(c / cat)"""

        inducer = RuleInducer(text, amr, tree, alignment)
        subtrees = inducer.run()

        original_subtrees = {1: {'nodes':{}, 'tree':{}}}
        original_subtrees[1]['nodes'] = {1: {'type': 'nonterminal', 'name': 'ROOT', 'parent': 0, 'label': 1},
                                         2: {'type': 'nonterminal', 'name': 'NP', 'parent': 1, 'label': 1},
                                         3: {'parent': 2, 'type': 'terminal', 'name': 'DT', 'value': 'The', 'label': -1},
                                         4: {'parent': 2, 'type': 'terminal', 'name': 'NN', 'value': 'cat', 'label': 1},
                                         5: {'parent': 2, 'type': 'terminal', 'name': '.', 'value': '.', 'label': -1}}
        original_subtrees[1]['tree'] = {1: [2], 2: [3, 4, 5], 3: [], 4: [], 5: []}

        self.assertDictEqual(original_subtrees, subtrees)

    def test_subj_verb_obj(self):
        text = 'The girl adjusted the machine .'

        alignment = '4-5|0.1 2-3|0 1-2|0.0'

        tree = """(ROOT
                      (S
                        (NP (DT The) (NN girl))
                        (VP (VBD adjusted)
                          (NP (DT the) (NN machine)))
                        (. .)))"""

        amr = """(a / adjust-01
                      :ARG0 (g / girl)
                      :ARG1 (m / machine))"""

        inducer = RuleInducer(text, amr, tree, alignment)
        subtrees = inducer.run()

        original_subtrees = {1: {'nodes':{}, 'tree':{}}, 2: {'nodes':{}, 'tree':{}}, 3: {'nodes':{}, 'tree':{}}}
        original_subtrees[1]['nodes'] = {8: {'type': 'nonterminal', 'name': 'NP', 'parent': 6, 'label': 1},
                                         9: {'parent': 8, 'type': 'terminal', 'name': 'DT', 'value': 'the', 'label': -1},
                                         10: {'parent': 8, 'type': 'terminal', 'name': 'NN', 'value': 'machine', 'label': 1}}
        original_subtrees[1]['tree'] = {8: [9, 10], 9: [], 10: []}

        original_subtrees[2]['nodes'] = {1: {'type': 'nonterminal', 'name': 'ROOT', 'parent': 0, 'label': 2},
                                         2: {'type': 'nonterminal', 'name': 'S', 'parent': 1, 'label': 2},
                                         6: {'type': 'nonterminal', 'name': 'VP', 'parent': 2, 'label': 2},
                                         7: {'parent': 6, 'type': 'terminal', 'name': 'VBD', 'value': 'adjusted', 'label': 2},
                                         11: {'parent': 2, 'type': 'terminal', 'name': '.', 'value': '.', 'label': -1},
                                         12: {'type': 'rule', 'name': '1/NP', 'parent': 6, 'label': -1},
                                         13: {'type': 'rule', 'name': '3/NP', 'parent': 2, 'label': -1}}
        original_subtrees[2]['tree'] = {1: [2], 2: [13, 6, 11], 6: [7, 12], 7: [], 11: [], 12: [], 13: []}

        original_subtrees[3]['nodes'] = {3: {'type': 'nonterminal', 'name': 'NP', 'parent': 2, 'label': 3},
                                         4: {'parent': 3, 'type': 'terminal', 'name': 'DT', 'value': 'The', 'label': -1},
                                         5: {'parent': 3, 'type': 'terminal', 'name': 'NN', 'value': 'girl', 'label': 3}}
        original_subtrees[3]['tree'] = {3: [4, 5], 4: [], 5: []}

        self.assertDictEqual(original_subtrees, subtrees, 'They are not equal')

    def test_subj_verb_obj_mod(self):
        text = 'The man described the mission as a disaster .'

        alignment = '7-8|0.2 4-5|0.1 2-3|0 1-2|0.0'

        tree = """(ROOT
                      (S
                        (NP (DT The) (NN man))
                        (VP (VBD described)
                          (NP (DT the) (NN mission))
                          (PP (IN as)
                            (NP (DT a) (NN disaster))))
                        (. .)))"""

        amr = """(d2 / describe-01
                      :ARG0 (m2 / man)
                      :ARG1 (m / mission)
                      :ARG2 (d / disaster))"""

        inducer = RuleInducer(text, amr, tree, alignment)
        subtrees = inducer.run()

        original_subtrees = {1: {'nodes':{}, 'tree':{}}, 2: {'nodes':{}, 'tree':{}}, 3: {'nodes':{}, 'tree':{}}, 4: {'nodes':{}, 'tree':{}}}
        original_subtrees[1]['nodes'] = {11: {'type': 'nonterminal', 'name': 'PP', 'parent': 6, 'label': 1},
                                         12: {'parent': 11, 'type': 'terminal', 'name': 'IN', 'value': 'as', 'label': -1},
                                         13: {'type': 'nonterminal', 'name': 'NP', 'parent': 11, 'label': 1},
                                         14: {'parent': 13, 'type': 'terminal', 'name': 'DT', 'value': 'a', 'label': -1},
                                         15: {'parent': 13, 'type': 'terminal', 'name': 'NN', 'value': 'disaster', 'label': 1}}
        original_subtrees[1]['tree'] = {11: [12, 13], 12: [], 13: [14, 15], 14: [], 15: []}

        original_subtrees[2]['nodes'] = {8: {'type': 'nonterminal', 'name': 'NP', 'parent': 6, 'label': 2},
                                         9: {'parent': 8, 'type': 'terminal', 'name': 'DT', 'value': 'the', 'label': -1},
                                         10: {'parent': 8, 'type': 'terminal', 'name': 'NN', 'value': 'mission', 'label': 2}}
        original_subtrees[2]['tree'] = {8: [9, 10], 9: [], 10: []}

        original_subtrees[3]['nodes'] = {1: {'type': 'nonterminal', 'name': 'ROOT', 'parent': 0, 'label': 3},
                                         2: {'type': 'nonterminal', 'name': 'S', 'parent': 1, 'label': 3},
                                         6: {'type': 'nonterminal', 'name': 'VP', 'parent': 2, 'label': 3},
                                         7: {'parent': 6, 'type': 'terminal', 'name': 'VBD', 'value': 'described', 'label': 3},
                                         16: {'parent': 2, 'type': 'terminal', 'name': '.', 'value': '.', 'label': -1},
                                         17: {'type': 'rule', 'name': '2/NP', 'parent': 6, 'label': -1},
                                         18: {'type': 'rule', 'name': '1/PP', 'parent': 6, 'label': -1},
                                         19: {'type': 'rule', 'name': '4/NP', 'parent': 2, 'label': -1}}
        original_subtrees[3]['tree'] = {1: [2], 2: [19, 6, 16], 6: [7, 17, 18], 7: [], 16: [], 17: [], 18: [], 19: []}

        original_subtrees[4]['nodes'] = {3: {'type': 'nonterminal', 'name': 'NP', 'parent': 2, 'label': 4},
                                         4: {'parent': 3, 'type': 'terminal', 'name': 'DT', 'value': 'The', 'label': -1},
                                         5: {'parent': 3, 'type': 'terminal', 'name': 'NN', 'value': 'man', 'label': 4}}
        original_subtrees[4]['tree'] = {3: [4, 5], 4: [], 5: []}

        self.assertDictEqual(original_subtrees, subtrees, 'They are not equal')

    def test_subj_verb_obj_loc(self):
        text = 'The man married the girl at the house .'

        alignment = '7-8|0.1.0 4-5|0.1 2-3|0 1-2|0.0'

        tree = """(ROOT
                      (S
                        (NP (DT The) (NN man))
                        (VP (VBD married)
                          (NP (DT the) (NN girl))
                          (PP (IN at)
                            (NP (DT the) (NN house))))
                        (. .)))"""

        amr = """(m / marry-01
                      :ARG0 (m2 / man)
                      :ARG1 (g / girl
                            :location (h / house)))"""

        inducer = RuleInducer(text, amr, tree, alignment)
        subtrees = inducer.run()

        original_subtrees = {1: {'nodes':{}, 'tree':{}}, 2: {'nodes':{}, 'tree':{}}, 3: {'nodes':{}, 'tree':{}}, 4: {'nodes':{}, 'tree':{}}}
        original_subtrees[1]['nodes'] = {11: {'type': 'nonterminal', 'name': 'PP', 'parent': 6, 'label': 1},
                                         12: {'parent': 11, 'type': 'terminal', 'name': 'IN', 'value': 'at', 'label': -1},
                                         13: {'type': 'nonterminal', 'name': 'NP', 'parent': 11, 'label': 1},
                                         14: {'parent': 13, 'type': 'terminal', 'name': 'DT', 'value': 'the', 'label': -1},
                                         15: {'parent': 13, 'type': 'terminal', 'name': 'NN', 'value': 'house', 'label': 1}}
        original_subtrees[1]['tree'] = {11: [12, 13], 12: [], 13: [14, 15], 14: [], 15: []}

        original_subtrees[2]['nodes'] = {8: {'type': 'nonterminal', 'name': 'NP', 'parent': 6, 'label': 2},
                                         9: {'parent': 8, 'type': 'terminal', 'name': 'DT', 'value': 'the', 'label': -1},
                                         10: {'parent': 8, 'type': 'terminal', 'name': 'NN', 'value': 'girl', 'label': 2}}
        original_subtrees[2]['tree'] = {8: [9, 10], 9: [], 10: []}

        original_subtrees[3]['nodes'] = {1: {'type': 'nonterminal', 'name': 'ROOT', 'parent': 0, 'label': 3},
                                         2: {'type': 'nonterminal', 'name': 'S', 'parent': 1, 'label': 3},
                                         6: {'type': 'nonterminal', 'name': 'VP', 'parent': 2, 'label': 3},
                                         7: {'parent': 6, 'type': 'terminal', 'name': 'VBD', 'value': 'married', 'label': 3},
                                         16: {'parent': 2, 'type': 'terminal', 'name': '.', 'value': '.', 'label': -1},
                                         17: {'type': 'rule', 'name': '2/NP', 'parent': 6, 'label': -1},
                                         18: {'type': 'rule', 'name': '1/PP', 'parent': 6, 'label': -1},
                                         19: {'type': 'rule', 'name': '4/NP', 'parent': 2, 'label': -1}}
        original_subtrees[3]['tree'] = {1: [2], 2: [19, 6, 16], 6: [7, 17, 18], 7: [], 16: [], 17: [], 18: [], 19: []}

        original_subtrees[4]['nodes'] = {3: {'type': 'nonterminal', 'name': 'NP', 'parent': 2, 'label': 4},
                                         4: {'parent': 3, 'type': 'terminal', 'name': 'DT', 'value': 'The', 'label': -1},
                                         5: {'parent': 3, 'type': 'terminal', 'name': 'NN', 'value': 'man', 'label': 4}}
        original_subtrees[4]['tree'] = {3: [4, 5], 4: [], 5: []}

        self.assertDictEqual(original_subtrees, subtrees, 'They are not equal')

    def test_loc_subj_verb_obj(self):
        text = 'At the house , the man married the girl .'

        alignment = '8-9|0.1 6-7|0 5-6|0.0 2-3|0.1.0'

        tree = """(ROOT
                      (S
                        (PP (IN At)
                          (NP (DT the) (NN house)))
                        (, ,)
                        (NP (DT the) (NN man))
                        (VP (VBD married)
                          (NP (DT the) (NN girl)))
                        (. .)))"""

        amr = """(m / marry-01
                      :ARG0 (m2 / man)
                      :ARG1 (g / girl
                            :location (h / house)))"""

        inducer = RuleInducer(text, amr, tree, alignment)
        subtrees = inducer.run()

        original_subtrees = {1: {'nodes':{}, 'tree':{}}, 2: {'nodes':{}, 'tree':{}}, 3: {'nodes':{}, 'tree':{}}, 4: {'nodes':{}, 'tree':{}}}
        original_subtrees[1]['nodes'] = {16: {'parent': 14, 'type': 'terminal', 'name': 'NN', 'value': 'girl', 'label': 1},
                                         14: {'type': 'nonterminal', 'name': 'NP', 'parent': 12, 'label': 1},
                                         15: {'parent': 14, 'type': 'terminal', 'name': 'DT', 'value': 'the', 'label': -1}}
        original_subtrees[1]['tree'] = {16: [], 14: [15, 16], 15: []}

        original_subtrees[2]['nodes'] = {1: {'type': 'nonterminal', 'name': 'ROOT', 'parent': 0, 'label': 2},
                                         2: {'type': 'nonterminal', 'name': 'S', 'parent': 1, 'label': 2},
                                         8: {'parent': 2, 'type': 'terminal', 'name': ',', 'value': ',', 'label': -1},
                                         12: {'type': 'nonterminal', 'name': 'VP', 'parent': 2, 'label': 2},
                                         13: {'parent': 12, 'type': 'terminal', 'name': 'VBD', 'value': 'married', 'label': 2},
                                         17: {'parent': 2, 'type': 'terminal', 'name': '.', 'value': '.', 'label': -1},
                                         18: {'type': 'rule', 'name': '1/NP', 'parent': 12, 'label': -1},
                                         19: {'type': 'rule', 'name': '4/PP', 'parent': 2, 'label': -1},
                                         20: {'type': 'rule', 'name': '3/NP', 'parent': 2, 'label': -1}}
        original_subtrees[2]['tree'] = {1: [2], 2: [19, 8, 20, 12, 17], 8: [], 12: [13, 18], 13: [], 17: [], 18: [], 19: [], 20: []}

        original_subtrees[3]['nodes'] = {9: {'type': 'nonterminal', 'name': 'NP', 'parent': 2, 'label': 3},
                                         10: {'parent': 9, 'type': 'terminal', 'name': 'DT', 'value': 'the', 'label': -1},
                                         11: {'parent': 9, 'type': 'terminal', 'name': 'NN', 'value': 'man', 'label': 3}}
        original_subtrees[3]['tree'] = {9: [10, 11], 10: [], 11: []}

        original_subtrees[4]['nodes'] = {3: {'type': 'nonterminal', 'name': 'PP', 'parent': 2, 'label': 4},
                                         4: {'parent': 3, 'type': 'terminal', 'name': 'IN', 'value': 'At', 'label': -1},
                                         5: {'type': 'nonterminal', 'name': 'NP', 'parent': 3, 'label': 4},
                                         6: {'parent': 5, 'type': 'terminal', 'name': 'DT', 'value': 'the', 'label': -1},
                                         7: {'parent': 5, 'type': 'terminal', 'name': 'NN', 'value': 'house', 'label': 4}}
        original_subtrees[4]['tree'] = {3: [4, 5], 4: [], 5: [6, 7], 6: [], 7: []}

        self.assertDictEqual(original_subtrees, subtrees, 'They are not equal')

    def test_modal(self):
        text = 'You can leave .'

        alignment = '2-3|0.0 1-2|0 0-1|0.0.0'

        tree = """(ROOT
                      (S
                        (NP (PRP You))
                        (VP (MD can)
                          (VP (VB leave)))
                        (. .)))"""

        amr = """(p / possible
                      :domain (l / leave-01
                            :ARG0 (y / you)))"""

        inducer = RuleInducer(text, amr, tree, alignment)
        subtrees = inducer.run()

        original_subtrees = {1: {'nodes':{}, 'tree':{}}, 2: {'nodes':{}, 'tree':{}}, 3: {'nodes':{}, 'tree':{}}}
        original_subtrees[1]['nodes'] = {1: {'type': 'nonterminal', 'name': 'ROOT', 'parent': 0, 'label': 1},
                                         2: {'type': 'nonterminal', 'name': 'S', 'parent': 1, 'label': 1},
                                         5: {'type': 'nonterminal', 'name': 'VP', 'parent': 2, 'label': 1},
                                         7: {'type': 'nonterminal', 'name': 'VP', 'parent': 5, 'label': 1},
                                         8: {'parent': 7, 'type': 'terminal', 'name': 'VB', 'value': 'leave', 'label': 1},
                                         9: {'parent': 2, 'type': 'terminal', 'name': '.', 'value': '.', 'label': -1},
                                         10: {'type': 'rule', 'name': '2/MD', 'parent': 5, 'label': -1},
                                         11: {'type': 'rule', 'name': '3/NP', 'parent': 2, 'label': -1}}
        original_subtrees[1]['tree'] = {1: [2], 2: [11, 5, 9], 5: [10, 7], 7: [8], 8: [], 9: [], 10: [], 11: []}

        original_subtrees[2]['nodes'] = {6: {'parent': 5, 'type': 'terminal', 'name': 'MD', 'value': 'can', 'label': 2}}
        original_subtrees[2]['tree'] = {6: []}

        original_subtrees[3]['nodes'] = {3: {'type': 'nonterminal', 'name': 'NP', 'parent': 2, 'label': 3},
                                         4: {'parent': 3, 'type': 'terminal', 'name': 'PRP', 'value': 'You', 'label': 3}}
        original_subtrees[3]['tree'] = {3: [4], 4: []}

        self.assertDictEqual(original_subtrees, subtrees, 'They are not equal')

    def test_passive(self):
        text = 'The machine was adjusted by the girl .'

        alignment = '6-7|0.0 3-4|0 1-2|0.1'

        tree = """(ROOT
                      (S
                        (NP (DT The) (NN machine))
                        (VP (VBD was)
                          (VP (VBN adjusted)
                            (PP (IN by)
                              (NP (DT the) (NN girl)))))
                        (. .)))"""

        amr = """(a / adjust-01
                      :ARG0 (g / girl)
                      :ARG1 (m / machine))"""

        inducer = RuleInducer(text, amr, tree, alignment)
        subtrees = inducer.run()

        original_subtrees = {1: {'nodes':{}, 'tree':{}}, 2: {'nodes':{}, 'tree':{}}, 3: {'nodes':{}, 'tree':{}}}
        original_subtrees[1]['nodes'] = {
            10: {'type': 'nonterminal', 'name': 'PP', 'parent': 8, 'label': 1},
            11: {'parent': 10, 'type': 'terminal', 'name': 'IN', 'value': 'by', 'label': -1},
            12: {'type': 'nonterminal', 'name': 'NP', 'parent': 10, 'label': 1},
            13: {'parent': 12, 'type': 'terminal', 'name': 'DT', 'value': 'the', 'label': -1},
            14: {'parent': 12, 'type': 'terminal', 'name': 'NN', 'value': 'girl', 'label': 1}}
        original_subtrees[1]['tree'] = {10: [11, 12], 11: [], 12: [13, 14], 13: [], 14: []}

        original_subtrees[2]['nodes'] = {1: {'type': 'nonterminal', 'name': 'ROOT', 'parent': 0, 'label': 2},
                                         2: {'type': 'nonterminal', 'name': 'S', 'parent': 1, 'label': 2},
                                         6: {'type': 'nonterminal', 'name': 'VP', 'parent': 2, 'label': 2},
                                         7: {'parent': 6, 'type': 'terminal', 'name': 'VBD', 'value': 'was', 'label': -1},
                                         8: {'type': 'nonterminal', 'name': 'VP', 'parent': 6, 'label': 2},
                                         9: {'parent': 8, 'type': 'terminal', 'name': 'VBN', 'value': 'adjusted', 'label': 2},
                                         15: {'parent': 2, 'type': 'terminal', 'name': '.', 'value': '.', 'label': -1},
                                         16: {'type': 'rule', 'name': '1/PP', 'parent': 8, 'label': -1},
                                         17: {'type': 'rule', 'name': '3/NP', 'parent': 2, 'label': -1}}
        original_subtrees[2]['tree'] = {1: [2], 2: [17, 6, 15], 6: [7, 8], 7: [], 8: [9, 16], 9: [], 15: [], 16: [], 17: []}

        original_subtrees[3]['nodes'] = {3: {'type': 'nonterminal', 'name': 'NP', 'parent': 2, 'label': 3},
                                         4: {'parent': 3, 'type': 'terminal', 'name': 'DT', 'value': 'The', 'label': -1},
                                         5: {'parent': 3, 'type': 'terminal', 'name': 'NN', 'value': 'machine', 'label': 3}}
        original_subtrees[3]['tree'] = {3: [4, 5], 4: [], 5: []}

        self.assertDictEqual(original_subtrees, subtrees, 'They are not equal')

    def test_relative_pronoun(self):
        self.assertEqual(1, 2, 'The aligner should be fixed.')

    def test_two_clauses(self):
        text = 'The boy wants to ride the red bicycle .'

        alignment = '7-8|0.1.0 6-7|0.1.0.0 4-5|0.1 2-3|0 1-2|0.0'

        tree = """(ROOT
                      (S
                        (NP (DT The) (NN boy))
                        (VP (VBZ wants)
                          (S
                            (VP (TO to)
                              (VP (VB ride)
                                (NP (DT the) (JJ red) (NN bicycle))))))
                        (. .)))"""

        amr = """(w / want-01
                      :ARG0 (b2 / boy)
                      :ARG1 (r2 / ride-01
                            :ARG1 (b / bicycle
                                  :mod (r / red))))"""

        inducer = RuleInducer(text, amr, tree, alignment)
        subtrees = inducer.run()

        original_subtrees = {1: {'nodes':{}, 'tree':{}},
                             2: {'nodes':{}, 'tree':{}},
                             3: {'nodes':{}, 'tree':{}},
                             4: {'nodes':{}, 'tree':{}},
                             5: {'nodes':{}, 'tree':{}}}
        original_subtrees[1]['nodes'] = {16: {'parent': 13, 'type': 'terminal', 'name': 'NN', 'value': 'bicycle', 'label': 1},
                                         18: {'type': 'rule', 'name': '2/JJ', 'parent': 13, 'label': -1},
                                         13: {'type': 'nonterminal', 'name': 'NP', 'parent': 11, 'label': 1},
                                         14: {'parent': 13, 'type': 'terminal', 'name': 'DT', 'value': 'the', 'label': -1}}
        original_subtrees[1]['tree'] = {16: [], 18: [], 13: [14, 18, 16], 14: []}

        original_subtrees[2]['nodes'] = {15: {'parent': 13, 'type': 'terminal', 'name': 'JJ', 'value': 'red', 'label': 2}}
        original_subtrees[2]['tree'] = {15: []}

        original_subtrees[3]['nodes'] = {8: {'type': 'nonterminal', 'name': 'S', 'parent': 6, 'label': 3},
                                         9: {'type': 'nonterminal', 'name': 'VP', 'parent': 8, 'label': 3},
                                         10: {'parent': 9, 'type': 'terminal', 'name': 'TO', 'value': 'to', 'label': -1},
                                         11: {'type': 'nonterminal', 'name': 'VP', 'parent': 9, 'label': 3},
                                         12: {'parent': 11, 'type': 'terminal', 'name': 'VB', 'value': 'ride', 'label': 3},
                                         19: {'type': 'rule', 'name': '1/NP', 'parent': 11, 'label': -1}}
        original_subtrees[3]['tree'] = {8: [9], 9: [10, 11], 10: [], 11: [12, 19], 12: [], 19: []}

        original_subtrees[4]['nodes'] = {1: {'type': 'nonterminal', 'name': 'ROOT', 'parent': 0, 'label': 4},
                                         2: {'type': 'nonterminal', 'name': 'S', 'parent': 1, 'label': 4},
                                         6: {'type': 'nonterminal', 'name': 'VP', 'parent': 2, 'label': 4},
                                         7: {'parent': 6, 'type': 'terminal', 'name': 'VBZ', 'value': 'wants', 'label': 4},
                                         17: {'parent': 2, 'type': 'terminal', 'name': '.', 'value': '.', 'label': -1},
                                         20: {'type': 'rule', 'name': '3/S', 'parent': 6, 'label': -1},
                                         21: {'type': 'rule', 'name': '5/NP', 'parent': 2, 'label': -1}}
        original_subtrees[4]['tree'] = {1: [2], 2: [21, 6, 17], 6: [7, 20], 7: [], 17: [], 20: [], 21: []}

        original_subtrees[5]['nodes'] = {3: {'type': 'nonterminal', 'name': 'NP', 'parent': 2, 'label': 5},
                                         4: {'parent': 3, 'type': 'terminal', 'name': 'DT', 'value': 'The', 'label': -1},
                                         5: {'parent': 3, 'type': 'terminal', 'name': 'NN', 'value': 'boy', 'label': 5}}
        original_subtrees[5]['tree'] = {3: [4, 5], 4: [], 5: []}

        self.assertDictEqual(original_subtrees, subtrees, 'They are not equal')

if __name__ == '__main__':
    unittest.main()

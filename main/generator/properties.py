import os

local_dir = '../data/'
server_dir = '/home/tcastrof/amr/data/'

prince_dir = os.path.join(server_dir, 'prince')
semeval_dir = os.path.join(server_dir, 'semeval')

morph_verb = os.path.join(local_dir, 'morph-verbalization-v1.01.txt')
verbalization = os.path.join(local_dir, 'verbalization-list-v1.06.txt')

initial_rules = os.path.join(prince_dir, 'rules/initial.json')
substitution_rules = os.path.join(prince_dir, 'rules/substitution.json')
adjoining_rules = os.path.join(prince_dir, 'rules/adjoining.json')

lexicons = os.path.join(prince_dir, 'lexicon/lexicon.json')
lexicon_laplace= os.path.join(prince_dir, 'lexicon/laplace.pickle')
lexicon_w= os.path.join(prince_dir, 'lexicon/w.pickle')
lexicon_w_tm1= os.path.join(prince_dir, 'lexicon/w_wtm1.pickle')
lexicon_w_head= os.path.join(prince_dir, 'lexicon/w_head.pickle')
lexicon_w_pos= os.path.join(prince_dir, 'lexicon/w_pos.pickle')
lexicon_w_edge= os.path.join(prince_dir, 'lexicon/w_edge.pickle')

initial_rule_edges = os.path.join(prince_dir, 'rules/initial_rule_edges.pickle')
substitution_rule_edges = os.path.join(prince_dir, 'rules/substitution_rule_edges.pickle')
initial_rule_edges_head = os.path.join(prince_dir, 'rules/initial_rule_edges_head.pickle')
substitution_rule_edges_head = os.path.join(prince_dir, 'rules/substitution_rule_edges_head.pickle')

voices = os.path.join(prince_dir, '/rules/voices.json')
template_voice = os.path.join(prince_dir, '/rules/voices.pickle')
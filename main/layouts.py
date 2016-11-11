__author__ = 'thiagocastroferreira'

# AMR
node = {'name':'', 'parent':{'node':-1, 'edge':-1}, 'status':'unlabeled', 'tokens':[]}
edge = ('edge', 'node')

# Aligner lemma
lemma = ('lemma', 'status')

# Stanford CoreNLP result
info = {'lemmas':[], 'entitymentions':[], 'pos':[], 'parse':''}

# Alignment
alignment = {'edges':[], 'tokens':[], 'ids':[], 'lemmas':[]}

# Rule Inducer
rule = {'tree':{}, 'nodes':{}, 'head':[], 'root':'', 'info':{'voice':'active', 'tense':''}}

# Constituent tree
nonterminal_node = {'name': '', 'parent': -1, 'type':'nonterminal'}
terminal_node = node = {'name': '', 'parent': -1, 'type':'terminal', 'lexicon':'', 'value':''}

# Tree adjoining grammars
tag = {'initial':{}, 'substitution':{}, 'adjoining':{}}
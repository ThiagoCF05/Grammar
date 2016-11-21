__author__ = 'thiagocastroferreira'

"""
Author: Thiago Castro Ferreira
Date: 14/11/2016
Description:
    This script aims to generate a text based on an AMR
"""

class Generator(object):
    def __init__(self):
        pass

    {
        'external_edges': {'r2': [':ARG1']},
        'lemmas': [u'ride'],
        'tokens': [4],
        'edges': {'r2': []},
        'nodes': {
            'r2': {'name': 'ride-01'}
        },
        'root': 'r2'
    }
    {
        'external_edges': {'r': []},
        'lemmas': [u'red'],
        'tokens': [6],
        'edges': {'r': []},
        'nodes': {'r': {'name': 'red'}},
        'root': 'r'
    }
    {
        'external_edges': {'b': [':mod']},
        'lemmas': [u'bicycle'],
        'tokens': [7],
        'edges': {'b': []},
        'nodes': {
            'b': {'name': 'bicycle'}
        },
        'root': 'b'
    }
    {
        'external_edges': {'b2': []},
        'lemmas': [u'boy'],
        'tokens': [1],
        'edges': {'b2': []},
        'nodes': {
            'b2': {'name': 'boy'}
        },
        'root': 'b2'
    }
    {
        'external_edges': {'w': [':ARG0', ':ARG1']},
        'lemmas': [u'want'],
        'tokens': [2],
        'edges': {'w': []},
        'nodes': {
            'w': {'name': 'want-01'}
        },
        'root': 'w'
    }
    {
        'external_edges': {'b2-coref1': []},
        'lemmas': [],
        'tokens': [],
        'edges': {'b2-coref1': []},
        'nodes': {
            'b2-coref1': {'name': 'boy'}
        },
        'root': 'b2-coref1'
    }
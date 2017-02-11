import gzip
import nltk
import os

import xml.etree.ElementTree as ET

def process_text(_xml):
    root = ET.fromstring(_xml)

    headline = root.find('HEADLINE')
    text = str(headline.text).replace('\n', ' ').lower()
    headline = ' '.join(nltk.word_tokenize(text)) + '\n'

    t = root.find('TEXT')
    paragraphs = t.findall('P')
    article = ''
    for paragraph in paragraphs:
        text = str(paragraph.text).replace('\n', ' ').lower()
        text = ' '.join(nltk.word_tokenize(text)) + '\n'
        article = article + text
    return headline, article

def process(fname, data, ndoc, nerror):
    f = gzip.open(fname)
    doc = f.read()
    f.close()

    _xml = ''
    for line in doc.split('\n'):
        _xml = _xml + line + '\n'
        if line.strip() == '</DOC>':
            try:
                headline, article = process_text(_xml)
                data = data + headline + article
                _xml = ''
                ndoc = ndoc + 1
            except:
                _xml = ''
                nerror = nerror + 1
    return data, ndoc, nerror

if __name__ == '__main__':
    dirs = [#'/roaming/tcastrof/gigaword/LDC2007T07/gigaword_eng_3a/data/afp_eng']
             # '/roaming/tcastrof/gigaword/LDC2007T07/gigaword_eng_3a/data/apw_eng',
            '/roaming/tcastrof/gigaword/LDC2007T07/gigaword_eng_3a/data/cna_eng']
            # '/roaming/tcastrof/gigaword/LDC2007T07/gigaword_eng_3b/data/ltw_eng',
            # '/roaming/tcastrof/gigaword/LDC2007T07/gigaword_eng_3b/data/nyt_eng',
            # '/roaming/tcastrof/gigaword/LDC2007T07/gigaword_eng_3b/data/xin_eng']

    data, ndoc, nerror = '', 0, 0
    for dir in dirs:
        for fname in os.listdir(dir):
            try:
                print fname
                data, ndoc, nerror =  process(os.path.join(dir, fname), data, ndoc, nerror)
            except:
                print 'Initial error'

            print '\nPROCESSED: ', ndoc, '/ ERRORS: ', nerror

    fwrite = '/roaming/tcastrof/gigaword/cna_eng.txt'
    f = open(fwrite, 'w')
    f.write(data.encode('utf-8'))
    f.close()
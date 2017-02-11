import gzip
import nltk
import os

import xml.etree.ElementTree as ET

def process_text(xml, data):
    root = ET.fromstring(xml)

    t = root.find('TEXT')

    headline = t.find('HEADLINE')
    text = str(headline.text).replace('\n', ' ').lower()
    text = ' '.join(nltk.word_tokenize(text)) + '\n'
    data = data + text

    paragraphs = t.findall('P')
    for paragraph in paragraphs:
        text = str(paragraph.text).replace('\n', ' ').lower()
        text = ' '.join(nltk.word_tokenize(text)) + '\n'
        data = data + text

def process(fname, data, ndoc, nerror):
    print 'READ'
    f = gzip.open(fname)
    doc = f.read()
    f.close()

    print 'PROCESS'
    xml = ''
    for line in doc.split('\n'):
        xml = xml + line + '\n'
        if line.strip() == '</DOC>':
            try:
                data = process_text(xml, data)
                xml = ''
                ndoc = ndoc + 1
            except:
                nerror = nerror + 1
    return data, ndoc, nerror


if __name__ == '__main__':
    dirs = ['/roaming/tcastrof/gigaword/LDC2007T07/gigaword_eng_3a/data/afp_eng']
            # '/roaming/tcastrof/gigaword/LDC2007T07/gigaword_eng_3a/data/apw_eng',
            # '/roaming/tcastrof/gigaword/LDC2007T07/gigaword_eng_3a/data/cna_eng'
            # '/roaming/tcastrof/gigaword/LDC2007T07/gigaword_eng_3b/data/ltw_eng',
            # '/roaming/tcastrof/gigaword/LDC2007T07/gigaword_eng_3b/data/nyt_eng',
            # '/roaming/tcastrof/gigaword/LDC2007T07/gigaword_eng_3b/data/xin_eng']

    data, ndoc, nerror = '', 0, 0
    for dir in dirs:
        for fname in os.listdir(dir):
            print fname
            data, ndoc, nerror =  process(os.path.join(dir, fname), data, ndoc, nerror)

            print '\nPROCESSED: ', ndoc, '/ ERRORS: ', nerror

    fwrite = '/roaming/tcastrof/gigaword/training.txt'
    f = open(fwrite, 'w')
    f.write(data)
    f.close()
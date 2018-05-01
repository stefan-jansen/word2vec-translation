#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Stefan Jansen'

import sys
from google.cloud import translate
from collections import Counter
import pandas as pd
from inspect import getfile, currentframe
from os.path import join, dirname, abspath

currentdir = dirname(abspath(getfile(currentframe())))
parentdir = dirname(currentdir)
sys.path.insert(0, parentdir)
from paths import DATA_DIR

with open(join(DATA_DIR, 'analogies-en.txt'), 'r') as f:
    text = [l.strip().lower() for l in f.readlines()]

counter = Counter(' '.join(text).split())
words = list(counter.keys())
languages = ['fr', 'es', 'de']


def get_translations():
    client = translate.Client()
    translations = pd.DataFrame()
    for language in languages:
        translation = {}
        for w, word in enumerate(words):
            print(w, word)
            try:
                translation[word] = client.translate(word, source_language='en', target_language=language)[
                    'translatedText']
            except:
                translation[word] = None
        translations[language] = pd.Series(translation)

    with pd.HDFStore('analogies.h5') as store:
        store.put('translations', translations)


def translate_analogies():
    with pd.HDFStore('analogies.h5') as store:
        translations = store.get('translations')
    for language in targets:
        translated = []
        translation = translations[language].str.lower().str.split().str.join('_').to_dict()
        for line in text:
            if line.startswith(':'):
                translated.append(line)
            else:
                translated.append(' '.join([translation[w].lower() for w in line.split()]))

        with pd.HDFStore('analogies.h5') as store:
            store.put(join(language, 'analogies'))

        with open(join(DATA_DIR, 'analogies-{}.txt').format(language), 'w') as f:
            f.write('\n'.join(translated))


def make_analogies(csv=True):
    """Create analogies in various languages"""
    data = pd.read_csv('../preprocessing/translations.csv')
    data.topic = data.topic.fillna(method='ffill')
    data.set_index('topic', inplace=True)
    data.columns = pd.MultiIndex.from_tuples([tuple(c.split('_')) for c in data.columns])
    data = data.apply(lambda x: x.str.lower())

    for language in languages:
        print('\n', language)
        result = pd.DataFrame()
        df = data.loc[:, language]
        for topic, words in df.groupby(level=0):
            if csv:
                result = result.append(pd.DataFrame([[':'], [topic], [''], ['']]).T)
            for i, pair in words.iterrows():
                words_ = words[(words['1'] != pair[0]) & (words['2'] != pair[1])]
                to_append = pd.DataFrame(np.hstack((np.tile(pair.values, (len(words_), 1)), words_.values)))
            if not csv:
                to_append['topic'] = topic
            result = pd.concat([result, to_append])

        if csv:
            result.drop_duplicates().to_csv('../data/analogies/analogies-{}.txt'.format(language), sep=' ', index=False,
                                            header=None)
        else:
            with pd.HDFStore('analogies.h5') as store:
                store.put(join(language, 'analogies'), result)
                print(store)



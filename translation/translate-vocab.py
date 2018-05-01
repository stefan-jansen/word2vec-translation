#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Stefan Jansen'

import pandas as pd
from google.cloud import translate


languages = ['en', 'es']


def get_translations(words):
    client = translate.Client()
    translations = pd.DataFrame(index=words, columns=languages[1:])
    for w, word in enumerate(words):
        for target in languages[1:]:
            try:
                translations.loc[word, target] = \
                    client.translate(word,
                                     format_='text',
                                     source_language='en',
                                     target_language=target)['translatedText']
            except:
                translations.loc[word, target] = None
        print(w, word, translations.loc[word].tolist())

    with pd.HDFStore('translations.h5') as store:
        store.put('translations', translations)

    print(translations)
    translations.to_csv('translations.csv')


def translate_from_en():
    with pd.HDFStore('translations.h5') as store:
        df = store.get('words-en').iloc[1:]
        df.word = df.word.str.replace('_', ' ')
        df = df[df.word.str.len() > 1]
        to_translate = df.loc[:10000, 'word'].tolist()
        get_translations(to_translate)


def match_translations():
    with pd.HDFStore('translations.h5') as store:

        base = store.get('words-en').drop('count', axis=1).iloc[1:]
        base.word = base.word.str.replace('_', ' ')
        base = base[base.word.str.len() > 1].loc[:10000]

        trans = store.get('translations').apply(lambda x: x.str.lower())

        matches = base.merge(trans, left_on='word', right_index=True)

        for language in languages[1:]:
            print('\n', language)
            target = store.get('words-{}'.format(language)).drop('count', axis=1).squeeze().str.replace('_', ' ')
            id_map = {w: i for i, w in target.to_dict().items()}
            matches[language + '_id'] = matches[language].map(id_map)
        matches = matches.reset_index().rename(columns={'index': 'en_id', 'word': 'en'}).sort_index(axis=1)
        print(matches.info())
        store.put('matches', matches)
        print(store)

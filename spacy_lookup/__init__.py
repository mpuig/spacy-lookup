# coding: utf8
from __future__ import unicode_literals

import os

from spacy.tokens import Doc, Span, Token
from flashtext import KeywordProcessor

from .about import __version__

data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class Entity(object):

    name = 'entity'

    def __init__(self, nlp, keywords_list=[], keywords_dict={}, keywords_file=None, label='',
                 attrs=('has_entities', 'is_entity', 'entity_desc', 'entities')):
        self._has_entities, self._is_entity, self._entity_desc, self._entities = attrs
        self.keyword_processor = KeywordProcessor()
        self.keyword_processor.add_keywords_from_list(keywords_list)
        self.keyword_processor.add_keywords_from_dict(keywords_dict)
        if keywords_file:
            self.keyword_processor.add_keyword_from_file(keywords_file)
        self.label = label
        # Add attributes
        Doc.set_extension(self._has_entities, getter=self.has_entities)
        Doc.set_extension(self._entities, getter=self.iter_entities)
        Span.set_extension(self._has_entities, getter=self.has_entities)
        Span.set_extension(self._entities, getter=self.iter_entities)
        Token.set_extension(self._is_entity, default=False)
        Token.set_extension(self._entity_desc, getter=self.get_entity_desc)

    def __call__(self, doc):
        matches = self.keyword_processor.extract_keywords(doc.text, span_info=True)
        spans = []  # keep spans here to merge them later
        for _, start, end in matches:
            entity = doc.char_span(start, end, label=self.label)
            for token in entity:
                token._.set(self._is_entity, True)
            spans.append(entity)
            # Overwrite doc.ents and add entity – be careful not to replace!
            doc.ents = list(doc.ents) + [entity]

        for span in spans:
            span.merge()
        return doc

    def has_entities(self, tokens):
        return any(token._.get(self._is_entity) for token in tokens)

    def iter_entities(self, tokens):
        return [(t.text, i, t._.get(self._entity_desc))
                for i, t in enumerate(tokens)
                if t._.get(self._is_entity)]

    def get_entity_desc(self, token):
        return token.text


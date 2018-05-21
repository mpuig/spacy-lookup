# coding: utf8
from __future__ import unicode_literals

import os

from spacy.tokens import Doc, Span, Token
from flashtext import KeywordProcessor

from .about import __version__

data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


class Entity(object):

    name = 'entity'

    def __init__(self, keywords_list=[], keywords_dict={}, keywords_file=None, label='',
                 attrs=('has_entities', 'is_entity', 'entity_desc', 'entities')):
        """Initialise the pipeline component.
        """
        self._has_entities, self._is_entity, self._entity_desc, self._entities = attrs

        # Set up the KeywordProcessor
        self.keyword_processor = KeywordProcessor()
        self.keyword_processor.add_keywords_from_list(keywords_list)
        self.keyword_processor.add_keywords_from_dict(keywords_dict)
        if keywords_file:
            self.keyword_processor.add_keyword_from_file(keywords_file)
        self.label = label

        # Register attribute on the Doc and Span
        Doc.set_extension(self._has_entities, getter=self.has_entities, force=True)
        Doc.set_extension(self._entities, getter=self.iter_entities, force=True)
        Span.set_extension(self._has_entities, getter=self.has_entities, force=True)
        Span.set_extension(self._entities, getter=self.iter_entities, force=True)

        # Register attribute on the Token.
        Token.set_extension(self._is_entity, default=False, force=True)
        Token.set_extension(self._entity_desc, getter=self.get_entity_desc, force=True)

    def __call__(self, doc):
        """Apply the pipeline component on a Doc object and modify it if matches
        are found. Return the Doc, so it can be processed by the next component
        in the pipeline, if available.
        """
        matches = self.keyword_processor.extract_keywords(doc.text, span_info=True)
        spans = []  # keep spans here to merge them later
        for _, start, end in matches:
            # Generate Span representing the entity & set label
            # Using doc.char_span() instead of Span() because the keyword processor returns
            # index values based on character positions, not words
            entity = doc.char_span(start, end, label=self.label)
            # Set custom attribute on each token of the entity
            if entity:
                for token in entity:
                    token._.set(self._is_entity, True)
            spans.append(entity)
            # Overwrite doc.ents and add entity – be careful not to replace!
            doc.ents = list(doc.ents) + [entity]

        for span in spans:
            # Iterate over all spans and merge them into one token. This is done
            # after setting the entities – otherwise, it would cause mismatched
            # indices!
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


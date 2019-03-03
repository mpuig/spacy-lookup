# coding: utf8
from __future__ import unicode_literals

from flashtext import KeywordProcessor
from spacy.tokens import Doc, Span, Token

from .about import __version__


class Entity(object):
    name = 'entity'

    def __init__(self, keywords_list=[], keywords_dict={}, keywords_file=None,
                 label='', case_sensitive=False,
                 attrs=('has_entities', 'is_entity', 'entity_desc', 'entities', 'canonical')):
        """Initialise the pipeline component.
        """
        self._has_entities, self._is_entity, self._entity_desc, self._entities, self.canonical = attrs

        # Set up the KeywordProcessor
        self.keyword_processor = KeywordProcessor(case_sensitive=case_sensitive)
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
        Token.set_extension(self.canonical, default=None, force=True)

    def __call__(self, doc):
        """Apply the pipeline component on a Doc object and modify it if matches
        are found. Return the Doc, so it can be processed by the next component
        in the pipeline, if available.
        """
        matches = self.keyword_processor.extract_keywords(doc.text, span_info=True)

        if len(matches)>0:
            entities = [ent.text for ent in doc.ents]

        spans = []  # keep spans here to merge them later
        for canonical, start, end in matches:
            # Generate Span representing the entity & set label
            # Using doc.char_span() instead of Span() because the keyword processor returns
            # index values based on character positions, not words
            entity = doc.char_span(start, end, label=self.label)
            if entity and entity.text not in entities:
                spans.append(entity)
                for token in entity:  # set values of token attributes
                    token._.set(self._is_entity, True)
                    token._.set('canonical', canonical)

        # Overwrite doc.ents and add entity – be careful not to replace!
        doc.ents = list(doc.ents) + spans

        for span in spans:
            # Iterate over all spans and merge them into one token. This is done
            # after setting the entities – otherwise, it would cause mismatched
            # indices!
            span.merge()

        return doc

    def has_entities(self, tokens):
        return any(token._.get(self._is_entity) for token in tokens)

    def iter_entities(self, tokens):
        return [(t.text, i, t._.get(self.canonical))
                for i, t in enumerate(tokens)
                if t._.get(self._is_entity)]

    def get_entity_desc(self, token):
        return token.text

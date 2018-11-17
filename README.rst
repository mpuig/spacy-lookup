spacy-lookup: Named Entity Recognition based on dictionaries
************************************************************

`spaCy v2.0 <https://spacy.io/usage/v2>`_ extension and pipeline component
for adding Named Entities metadata to ``Doc`` objects. Detects Named Entities
using dictionaries. The extension sets the custom ``Doc``,
``Token`` and ``Span`` attributes ``._.is_entity``, ``._.entity_type``,
``._.has_entities`` and ``._.entities``.

Named Entities are matched using the python module ``flashtext``, and
looks up in the data provided by different dictionaries.

Installation
===============

``spacy-lookup`` requires ``spacy`` v2.0.16 or higher.

.. code:: bash

    pip install spacy-lookup

Usage
=====
First, you need to download a language model.

.. code:: bash

    python -m spacy download en

Import the component and initialise it with the shared ``nlp`` object (i.e. an
instance of ``Language``), which is used to initialise ``flashtext``
with the shared vocab, and create the match patterns. Then add the component
anywhere in your pipeline.

.. code:: python

    import spacy
    from spacy_lookup import Entity

    nlp = spacy.load('en')
    entity = Entity(keywords_list=['python', 'product manager', 'java platform'])
    nlp.add_pipe(entity, last=True)

    doc = nlp(u"I am a product manager for a java and python.")
    assert doc._.has_entities == True
    assert doc[0]._.is_entity == False
    assert doc[3]._.entity_desc == 'product manager'
    assert doc[3]._.is_entity == True
    print(doc._.entities)

``spacy-lookup`` only cares about the token text, so you can use it on a blank
``Language`` instance (it should work for all
`available languages <https://spacy.io/usage/models#languages>`_!), or in
a pipeline with a loaded model. If you're loading a model and your pipeline
includes a tagger, parser and entity recognizer, make sure to add  the entity
component as ``last=True``, so the spans are merged at the end of the pipeline.

Available attributes
--------------------

The extension sets attributes on the ``Doc``, ``Span`` and ``Token``. You can
change the attribute names on initialisation of the extension. For more details
on custom components and attributes, see the
`processing pipelines documentation <https://spacy.io/usage/processing-pipelines#custom-components>`_.

====================== ======= ===
``Token._.is_entity``   bool    Whether the token is an entity.
``Token._.entity_type`` unicode A human-readable description of the entity.
``Doc._.has_entities``    bool    Whether the document contains entity.
``Doc._.entities``        list    ``(entity, index, description)`` tuples of the document's entities.
``Span._.has_entities``   bool    Whether the span contains entity.
``Span._.entities``       list    ``(entity, index, description)`` tuples of the span's entities.
====================== ======= ===

Settings
--------

On initialisation of ``Entity``, you can define the following settings:

=============== ============ ===
``nlp``         ``Language`` The shared ``nlp`` object. Used to initialise the matcher with the shared ``Vocab``, and create ``Doc`` match patterns.
``attrs``       tuple        Attributes to set on the ._ property. Defaults to ``('has_entities', 'is_entity', 'entity_type', 'entity')``.
``keywords_list``      list         Optional lookup table with the list of terms to look for.
``keywords_dict``      dict         Optional lookup table with the list of terms to look for.
``keywords_file``      string         Optional filename with the list of terms to look for.
=============== ============ ===

.. code:: python

    entity = Entity(nlp, keywords_list=['python', 'java platform'], label='ACME')
    nlp.add_pipe(entity)
    doc = nlp(u"I am a product manager for a java platform and python.")
    assert doc[3]._.is_entity

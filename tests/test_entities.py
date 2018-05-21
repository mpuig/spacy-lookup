# coding: utf-8
from __future__ import unicode_literals

from spacy.lang.en import English
import pytest
import os


from spacy_lookup import Entity

def ensure_path(path):
    """Ensure string is converted to a Path.

    path: Anything. If string, it's converted to Path.
    RETURNS: Path or original argument.
    """
    if isinstance(path, basestring_):
        return Path(path)
    else:
        return path


@pytest.fixture(scope='function')
def nlp():
    return English()


@pytest.fixture(scope='function')
def keyword_dict():
    return {
        "java": ["java_2e", "java programing"],
        "product management": ["PM", "product manager"]
    }


@pytest.fixture(scope='function')
def keyword_list():
    return ["java", "python"]


def test_integration(nlp):
    entity = Entity()
    nlp.add_pipe(entity, last=True)
    assert nlp.pipe_names[-1] == 'entity'


def test_usage_no_entity(nlp):
    entity = Entity(keywords_list=keyword_list(), label='ACME')
    nlp.add_pipe(entity, last=True)
    doc = nlp(u"This is a sentence without entities.")
    assert not doc._.has_entities
    for token in doc:
        assert not token._.is_entity


def test_usage_multiple_entities_from_list(nlp):
    entity = Entity(keywords_list=keyword_list(), label='ACME')
    nlp.add_pipe(entity, last=True)
    doc = nlp(u"I am a product manager for a java platform and python.")
    assert doc._.has_entities
    assert len(doc._.entities) == 2
    assert doc[:8]._.has_entities
    assert len(doc[:8]._.entities) == 1

def test_usage_multiple_entities_from_dict(nlp):
    entity = Entity(keywords_dict=keyword_dict(), label='ACME')
    nlp.add_pipe(entity, last=True)
    doc = nlp(u"I am a product manager for a java_2e platform and python.")
    assert doc._.has_entities
    assert len(doc._.entities) == 2
    assert doc[:8]._.has_entities
    assert doc[3]._.entity_desc == 'product manager'
    assert len(doc[:4]._.entities) == 1
    assert doc[6]._.entity_desc == 'java_2e'


def test_usage_multiple_entities_from_list_and_dict(nlp):
    entity = Entity(keywords_list=keyword_list(), keywords_dict=keyword_dict(), label='ACME')
    nlp.add_pipe(entity, last=True)
    doc = nlp(u"I am a product manager for a java_2e platform and python.")
    assert doc._.has_entities
    assert len(doc._.entities) == 3
    assert doc[:8]._.has_entities
    assert doc[3]._.entity_desc == 'product manager'
    assert len(doc[:4]._.entities) == 1
    assert doc[6]._.entity_desc == 'java_2e'
    assert doc[9]._.entity_desc == 'python'


@pytest.mark.parametrize('file_name', ["keywords.txt"])
def test_usage_entities_from_file(nlp, file_name):
    keyword_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)
    entity = Entity(keywords_file=keyword_file, keywords_dict=keyword_dict(), label='ACME')
    nlp.add_pipe(entity, last=True)
    doc = nlp(u"I am a product manager for a java_2e platform and python.")
    assert doc._.has_entities
    assert len(doc._.entities) == 2
    assert doc[:8]._.has_entities
    assert doc[3]._.entity_desc == 'product manager'
    assert len(doc[:4]._.entities) == 1
    assert doc[6]._.entity_desc == 'java_2e platform'


def test_usage_multiple_components(nlp):
    entity1 = Entity(keywords_list=keyword_list(), label='ACME_1')
    nlp.add_pipe(entity1, first=False, name='entity1')
    entity2 = Entity(keywords_dict=keyword_dict(), label='ACME_2')
    nlp.add_pipe(entity2, first=False, name='entity2')
    doc = nlp(u"I am a product manager for a java_2e platform and python.")
    assert doc._.has_entities
    assert len(doc._.entities) == 3
    assert doc[:8]._.has_entities
    assert doc[3]._.entity_desc == 'product manager'
    assert len(doc[:4]._.entities) == 1
    assert doc[6]._.entity_desc == 'java_2e'
    assert doc[9]._.entity_desc == 'python'

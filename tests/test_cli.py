import os
import sys
import pytest

sys.path.insert(0, os.path.abspath('.'))
import cli


def idfn(val):
    return str(val)


def test_get_index_html():
    index_html = cli.get_index_html('./tests')
    assert index_html == os.path.join('./tests', 'index.html')


def test_get_title():
    title = cli.get_title('./tests/index.html')
    assert title == 'Groovy 2.5.0-SNAPSHOT'


def test_get_title_no_dir():
    title = cli.get_title('./tests/index_no_title.html')
    assert title == 'Javadoc Title'

titles = [
    ('Javadoc Title', 'javadoc_title'),
    ('Javadoc.Title', 'javadoc-title'),
    ('Java.doc Title', 'java-doc_title')
]


@pytest.mark.parametrize('title,project', titles, ids=idfn)
def test_get_project_name(title, project):
    assert cli.get_project_name(title) == project

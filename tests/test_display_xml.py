"""
"""
from display_xml import tostring
import lxml.etree as ET
import pytest


@pytest.fixture
def element():
    xml = """<root>
    <parent class="royals">
    Princess Diana - Prince Charles
    <child>Prince William</child>
    <child>Prince Harry</child>
    </parent>
    the end
    </root>
    """
    element = ET.fromstring(xml)
    return element


def test_to_string(element):
    """Test implementation of tostring against lxml's version."""
    assert tostring(element) == ET.tostring(element).decode('utf-8')


def test_to_string_hook(element):
    """Show how we can now control formatting of xml recursively by
    using a hook function that receives each formatted component.

    Here we upcase the tags and put the whole element on one line.
    """
    def one_liner_hook(tag, attributes, text, children, tail, indent):
        print(locals())
        tag = tag.upper()
        return f"""<{tag}{attributes}>{text.strip()}{children}</{tag}>{tail.strip()}""" # noqa

    assert tostring(element, hook=one_liner_hook, pretty_print=False) == (
        '<ROOT><PARENT class="royals">Princess Diana - Prince Charles'
        '<CHILD>Prince William</CHILD><CHILD>Prince Harry</CHILD></PARENT>the end</ROOT>' # noqa
    )

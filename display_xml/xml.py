"""from https://github.com/mpacer/display_xml

Make IPython foldable XML display, similar to the JSON functionality.
"""
from pygments import highlight
from pygments.lexers import XmlLexer
from pygments.formatters import HtmlFormatter
from pygments.styles import get_all_styles
import lxml.etree as et
from uuid import uuid4

from IPython.display import display

no_blank_parser = et.XMLParser(remove_blank_text=False)


def tostring(element, hook=None, indent=0, indent_increment_size=1):
    """Turn XML element to string.

    Applied recursively (depth first to all elements in the tree.

    Parameters
    ----------
    element: xml.etree.Element
        An XML element.
    hook: callable
        A function of the form f(tag, attributes, text, children,
        tail) that receives strings representing all the components of
        the element and that returns a string representation of the
        entire element. This can be used to have more control over the
        formatting of the element.
    indent: int
        Indentation level for element.
    indent_increment_size: bool
        By how much to increase the indentation level when going
        deeper into the tree.
    """
    child_indent = indent + indent_increment_size
    children = ''.join(
        tostring(child, hook, child_indent, indent_increment_size)
        for child in element
    )
    attributes = ' '.join(
        f'{key}="{value}"' for (key, value) in element.attrib.items()
    )

    if attributes:
        attributes = ' ' + attributes
    if callable(hook):
        return hook(
            element.tag,
            attributes,
            element.text or '', children,
            element.tail or '',
            indent
        )
    else:
        indentation = indent * "&nbsp;"  # non breakable space
        result = (
            f"{indentation}<{element.tag}{attributes}>"
            f"{element.text or ''}{children}"
            f"</{element.tag}>{element.tail or ''}"
        )
        return result


class XML:
    """Class for displaying XML in a pretty way that supports pygments styles.
    """
    HTML_TEMPLATE = """
    <div class="{uuid_class}">
        <style>
            {style_css}
        </style>
        {content}
    </div>

    """

    NAMED_STYLE_TEMPLATE = (
        """<h3 style="margin-bottom:.3em"> {extras[style_name]} </h3>""" +
        HTML_TEMPLATE +
        "<hr/>"
        )

    _other_params_docstring = """expand: bool
        Whether or not to expand the XML elements by default.
    pretty_print: int
        By how much to increase the indentation level between parent element
        and child element.
    """

    def __init__(self, in_obj, style='default', template=None,
                 extras=None, expand=False, pretty_print=1):
        f"""
        Parameters
        ----------
        in_obj : str, lxml.etree._Element, lxml.etree._ElementTree, or bytes
            Object to be displayed as html
        style : str, optional
            Pygment style names (the default is 'default')
        expand: bool
            Whether or not to expand the XML elements by default.
        pretty_print: int
            By how much to increase the indentation level between parent element
            and child element.
        """
        if extras is None:
            extras = {}

        if template is None:
            template = self.HTML_TEMPLATE

        if isinstance(in_obj, (str, bytes)):
            self._xml = et.fromstring(in_obj, parser=no_blank_parser)
        elif isinstance(in_obj, et._ElementTree):
            self._xml = in_obj.getroot()
        elif isinstance(in_obj, et._Element):
            self._xml = in_obj
        else:
            raise TypeError(f"{in_obj} is of type {type(in_obj)}."
                            "This object only can displays objects of type "
                            "str, bytes, lxml.etree._ElementTree, or "
                            "lxml.etree._Element.")

        self.style = style
        self.formatter = HtmlFormatter(style=self.style)
        self.uuid_class = "a"+str(self.uuid)
        self.template = template
        self.extras = extras
        self.expand = expand
        self.pretty_print = pretty_print


    def _make_foldable(self, xml):
        """Make the document foldable.

        Add <details> elements above all parent nodes.
        """
        details = et.Element("details")
        summary = et.Element("summary")
        summary.text = xml.tag # TODO: include attributes
        details.append(summary)
        root = et.Element(xml.tag)
        root.text = xml.text
        root.tail = xml.tail
        for node in xml:
            foldable_node = self._make_foldable(node)
            root.append(foldable_node)
        details.append(root)
        return details

    @classmethod
    def display_all_styles(cls, in_obj, **kwargs):
        """
        Displays all available pygments styles using XML.style_gen()

        Parameters
        ----------

        in_obj: str lxml.etree._Element, lxml.ettree._ElementTree, or bytes
            Object to be displayed as html
        kwargs: passed to cls.style_gen method.
        """.format(cls._other_params_docstring)
        for disp in cls.style_gen(in_obj, **kwargs):
            display(disp)

    @classmethod
    def style_gen(cls, in_obj, **kwargs):
        """
        Generator for iterating over all of the styles available from pygments.

        If you declare this xml = XML.style_gen(text), use next(xml).

        in_obj: str lxml.etree._Element, lxml.ettree._ElementTree, or bytes
            Object to be displayed as html
        kwargs: passed to cls.__init__.
        """
        for style in get_all_styles():
            yield(cls(in_obj,
                      style=style,
                      template=cls.NAMED_STYLE_TEMPLATE,
                      extras={"style_name": style},
                      **kwargs
                      ))

    @property
    def style_css(self):
        """
        Generates the css classes needed to apply this uniquely.

        TODO: it might be nice to move toward a vdom based displayer
        for more versatile control
        """
        details_css = """
{div} pre {{ margin: 0 0; font-family: inherit;}} /* consistent font for opening and closing tags */
{div} .highlight {{ display: inline}}
{div} summary::marker {{ font-size: 0.66em; margin-inline-end: 0.4em; }}  /* marker for firefox */
{div} summary::-webkit-details-marker {{width: 0.66em; margin-inline-end: 0.4em;}} /* marker for chrome */
{div} .indented-xml-content {{padding-left:1.06em;}}
""".format(div=f"div.{self.uuid_class}")  # noqa
        temp_css = self.formatter.get_style_defs()
        css_list = [
            f"div.{self.uuid_class} {x}" for x in temp_css.split("\n")
        ] + details_css.split('\n')
        return "\n".join(css_list)

    @property
    def uuid(self):
        return uuid4()

    def _repr_html_(self):
        content = tostring(
            self._xml,
            hook=self._foldable_to_string_hook,
            indent_increment_size=int(self.pretty_print)
        )
        return self.template.format(
            uuid_class=self.uuid_class,
            style_css=self.style_css,
            content=content,
            extras=self.extras,
        )

    def _foldable_to_string_hook(self, tag, attributes, text, children,
                                 tail, indent):
        """Return foldable content string.

        Use <details> element to make the string foldable.
        https://developer.mozilla.org/en-US/docs/Web/HTML/Element/details

        This is a hook function to use in combination with the ``tostring``
        function defined in this module. It receives HTML string representation
        of all the components in the XML's element.

        Parameters
        ----------
        tag: str
           The element's tag name.
        attributes: str
           The element's tag's attributes, of teh form "attr1='val1'
           attr2='val2'".
        text: str
           The element's text.
        children: str
           The HTML text representing the element's children.
        tail: str
           Text representing the element's tail.
        indent: integer
           Indentation level for this element (in ems).
       """
        def highlight_string(string):
            return highlight(string, XmlLexer(), self.formatter)

        opening_tag = highlight_string(f"<{tag}{attributes}>").replace(
            '<pre>', '').replace('</pre>', '')
        closing_tag = highlight_string(f"</{tag}>")
        foldable_content = f"""
    <div class="indented-xml" style="margin-left:{indent}em;">
        <details{" open" if self.expand else ''}>
            <summary>{opening_tag}</summary>
            <div class="indented-xml-content">
                {text}{children}
                {closing_tag}{tail}
            </div>
        </details>
    </div>
"""
        return foldable_content

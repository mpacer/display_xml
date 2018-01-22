from pygments import highlight
from pygments.lexers import XmlLexer
from pygments.formatters import HtmlFormatter
from pygments.styles import get_all_styles
import lxml.etree as et
from uuid import uuid4

from IPython.display import display

no_blank_parser = et.XMLParser(remove_blank_text=True)


class XML:
    '''Class for displaying XML in a pretty way that supports pygments styles.
    '''
    HTML_TEMPLATE = """
    <div class={uuid_class}> 
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

    def __init__(self, in_obj, style='default', template=HTML_TEMPLATE, 
                 extras={}):
        '''
        Parameters
        ----------
        in_obj : str lxml.etree._Element, lxml.ettree._ElementTree, or bytes
            Object to be displayed as html
        style : str, optional
            Pygment style names (the default is 'default')
        '''
        if isinstance(in_obj, str):
            self.xml = et.fromstring(in_obj, parser=no_blank_parser)
        elif isinstance(in_obj, bytes): 
            self.xml = et.fromstring(in_obj, parser=no_blank_parser)
        elif isinstance(in_obj, et._ElementTree):
            self.xml = in_obj.getroot()
        else:  # assume isinstance(in_obj, et._Element)
            self.xml = in_obj
        
        self.text = et.tostring(self.xml, pretty_print=True)
        self.style = style
        self.formatter = HtmlFormatter(style=self.style)
        self.uuid_class = "a"+str(self.uuid)
        self.template = template
        self.extras = extras
    
    @classmethod
    def display_all_styles(cls, in_obj):
        """
        Displays all available pygments styles using XML.style_gen()
        
        Parameters
        ----------
        
        in_obj: str lxml.etree._Element, lxml.ettree._ElementTree, or bytes
            Object to be displayed as html
        """
        for disp in cls.style_gen(in_obj):
            display(disp)
                        
    @classmethod
    def style_gen(cls, in_obj):
        """
        Generator for iterating over all of the styles available from pygments.
        
        If you declare this xml = XML.style_gen(text), use next(xml).
        """
        for style in get_all_styles():
            yield(cls(in_obj, 
                      style=style, 
                      template=cls.NAMED_STYLE_TEMPLATE, 
                      extras={"style_name": style}
                      ))
    
    @property
    def style_css(self):
        temp_css = self.formatter.get_style_defs()
        css_list = [f"div.{self.uuid_class} {x}" for x in temp_css.split("\n")]
        return "\n".join(css_list)

    @property
    def uuid(self):
        return uuid4()

    def _repr_html_(self):
        content = highlight(self.text, XmlLexer(), self.formatter)
        return self.template.format(uuid_class=self.uuid_class,
                                    style_css=self.style_css,
                                    content=content,
                                    extras=self.extras
    )

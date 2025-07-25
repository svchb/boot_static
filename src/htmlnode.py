from typing import List, Dict, Optional
from textnode import TextNode, TextType

class HTMLNode:
    def __init__(
        self,
        tag: Optional[str] = None,
        value: Optional[str] = None,
        children: Optional[List['HTMLNode']] = None,
        props: Optional[Dict[str, str]] = None
    ):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self) -> str:
        raise NotImplementedError("Subclasses must implement to_html()")

    def props_to_html(self) -> str:
        if not self.props:
            return ''
        parts = [f' {key}="{value}"' for key, value in self.props.items()]
        return ''.join(parts)

    def __repr__(self):
        return (
            f"HTMLNode(tag={self.tag!r}, value={self.value!r}, "
            f"children={self.children!r}, props={self.props!r})"
        )

class LeafNode(HTMLNode):
    def __init__(self, tag: Optional[str], value: str, props: Optional[Dict[str, str]] = None):
        # children must always be None for a leaf
        super().__init__(tag=tag, value=value, children=None, props=props)

    def to_html(self) -> str:
        if self.value is None:
            raise ValueError("LeafNode must have a value to render")
        # Raw text if no tag
        if self.tag is None:
            return self.value
        # Proper HTML tag with props
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"

class ParentNode(HTMLNode):
    def __init__(
        self,
        tag: str,
        children: List[HTMLNode],
        props: Optional[Dict[str, str]] = None
    ):
        super().__init__(tag=tag, value=None, children=children, props=props)

    def to_html(self) -> str:
        if self.tag is None:
            raise ValueError("ParentNode must have a tag")
        if self.children is None:
            raise ValueError("ParentNode must have children")
        inner = ''.join(child.to_html() for child in self.children)
        return f"<{self.tag}{self.props_to_html()}>{inner}</{self.tag}>"

def text_node_to_html_node(text_node: TextNode) -> LeafNode:
    if not isinstance(text_node, TextNode):
        raise TypeError("Expected a TextNode instance")
    ttype = text_node.text_type
    text = text_node.text
    url = text_node.url
    if ttype == TextType.PLAIN:
        return LeafNode(None, text)
    elif ttype == TextType.BOLD:
        return LeafNode("b", text)
    elif ttype == TextType.ITALIC:
        return LeafNode("i", text)
    elif ttype == TextType.CODE:
        return LeafNode("code", text)
    elif ttype == TextType.LINK:
        return LeafNode("a", text, {"href": url})
    elif ttype == TextType.IMAGE:
        return LeafNode("img", "", {"src": url, "alt": text})
    else:
        raise ValueError(f"Unsupported TextType: {ttype}")

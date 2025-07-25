from enum import Enum

class TextType(Enum):
    PLAIN = "plain"
    BOLD = "bold"
    ITALIC = "italic"
    UNDERLINE = "underline"
    STRIKETHROUGH = "strikethrough"
    LINK = "link"
    IMAGE = "image"
    CODE = "code"
    QUOTE = "quote"

class TextNode:
    def __init__(self, text: str, text_type: TextType, url: str = None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        if not isinstance(other, TextNode):
            return NotImplemented
        return (
            self.text == other.text and
            self.text_type == other.text_type and
            self.url == other.url
        )

    def __repr__(self):
        return f"TextNode({self.text!r}, {self.text_type.value!r}, {self.url!r})"

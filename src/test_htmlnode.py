import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode, text_node_to_html_node
from textnode import TextNode, TextType

class TestHTMLNode(unittest.TestCase):
    def test_props_to_html_empty(self):
        node = HTMLNode(tag="a", value="link")
        self.assertEqual(node.props_to_html(), '')

    def test_props_to_html_single(self):
        node = HTMLNode(tag="img", props={"src": "image.png"})
        self.assertEqual(node.props_to_html(), ' src="image.png"')

    def test_props_to_html_multiple(self):
        node = HTMLNode(tag="a", props={"href": "https://example.com", "target": "_blank"})
        html = node.props_to_html()
        # Order of attributes in dict may vary
        self.assertIn(' href="https://example.com"', html)
        self.assertIn(' target="_blank"', html)

    def test_repr(self):
        node = HTMLNode(tag="p", value="text", children=[], props={"id": "para1"})
        expected = (
            "HTMLNode(tag='p', value='text', children=[], props={'id': 'para1'})"
        )
        self.assertEqual(repr(node), expected)

class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_raw(self):
        # No tag should return raw text
        node = LeafNode(None, "Just text")
        self.assertEqual(node.to_html(), "Just text")

    def test_leaf_to_html_with_props(self):
        node = LeafNode("a", "Click here", {"href": "https://foo.com"})
        self.assertEqual(node.to_html(), "<a href=\"https://foo.com\">Click here</a>")

    def test_leaf_missing_value(self):
        # Missing value should raise ValueError
        node = LeafNode("span", None)
        with self.assertRaises(ValueError):
            _ = node.to_html()

class TestParentNode(unittest.TestCase):
    def test_to_html_with_children(self):
        child = LeafNode("span", "child")
        parent = ParentNode("div", [child])
        self.assertEqual(parent.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grand = LeafNode("b", "grandchild")
        child = ParentNode("span", [grand])
        parent = ParentNode("div", [child])
        self.assertEqual(parent.to_html(), "<div><span><b>grandchild</b></span></div>")

    def test_to_html_no_tag(self):
        child = LeafNode("span", "x")
        parent = ParentNode(None, [child])
        with self.assertRaises(ValueError):
            parent.to_html()

    def test_to_html_no_children(self):
        parent = ParentNode("div", None)
        with self.assertRaises(ValueError):
            parent.to_html()

class TestTextNodeToHtmlNode(unittest.TestCase):
    def test_text(self):
        node = TextNode("This is a text node", TextType.PLAIN)
        html_node = text_node_to_html_node(node)
        self.assertIsInstance(html_node, LeafNode)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        node = TextNode("bold text", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "bold text")

    def test_link(self):
        node = TextNode("link text", TextType.LINK, "http://a.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.props, {"href": "http://a.com"})

    def test_image(self):
        node = TextNode("alt text", TextType.IMAGE, "img.png")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.props, {"src": "img.png", "alt": "alt text"})

    def test_unsupported(self):
        node = TextNode("x", TextType.UNDERLINE)
        with self.assertRaises(ValueError):
            _ = text_node_to_html_node(node)

if __name__ == "__main__":
    unittest.main()

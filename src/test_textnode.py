import unittest

from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        # Two nodes with identical text and type (default url=None)
        node1 = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node1, node2)

    def test_eq_default_url(self):
        # Default url should be None and treated the same as explicit None
        node1 = TextNode("Sample", TextType.PLAIN)
        node2 = TextNode("Sample", TextType.PLAIN, None)
        self.assertEqual(node1, node2)

    def test_not_equal_text(self):
        # Different text should not be equal
        node1 = TextNode("one", TextType.PLAIN)
        node2 = TextNode("two", TextType.PLAIN)
        self.assertNotEqual(node1, node2)

    def test_not_equal_type(self):
        # Same text but different type should not be equal
        node1 = TextNode("text", TextType.UNDERLINE)
        node2 = TextNode("text", TextType.ITALIC)
        self.assertNotEqual(node1, node2)

    def test_not_equal_url(self):
        # Same text and type but different url should not be equal
        node1 = TextNode("link text", TextType.LINK, "http://a.com")
        node2 = TextNode("link text", TextType.LINK, "http://b.com")
        self.assertNotEqual(node1, node2)

    def test_repr(self):
        # repr should return the exact string format
        node = TextNode("abc", TextType.ITALIC)
        expected = "TextNode('abc', 'italic', None)"
        self.assertEqual(repr(node), expected)


if __name__ == "__main__":
    unittest.main()

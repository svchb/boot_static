import unittest

from textnode import TextNode, TextType
from markdown_utils import (
    split_nodes_delimiter,
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_image,
    split_nodes_link,
    text_to_textnodes,
    markdown_to_blocks,
    BlockType,
    block_to_block_type,
    markdown_to_html_node,
)


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_code(self):
        node = TextNode("This is text with a `code block` word", TextType.PLAIN)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("This is text with a ", TextType.PLAIN),
            TextNode("code block", TextType.CODE),
            TextNode(" word", TextType.PLAIN),
        ]
        self.assertEqual(result, expected)

    def test_bold(self):
        node = TextNode("An **important** note", TextType.PLAIN)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [
            TextNode("An ", TextType.PLAIN),
            TextNode("important", TextType.BOLD),
            TextNode(" note", TextType.PLAIN),
        ]
        self.assertEqual(result, expected)

    def test_multiple(self):
        node = TextNode("A `x` and `y`", TextType.PLAIN)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("A ", TextType.PLAIN),
            TextNode("x", TextType.CODE),
            TextNode(" and ", TextType.PLAIN),
            TextNode("y", TextType.CODE),
            TextNode("", TextType.PLAIN),
        ]
        self.assertEqual(result, expected)

    def test_skip_non_plain(self):
        node1 = TextNode("bold", TextType.BOLD)
        node2 = TextNode(" plain `c`", TextType.PLAIN)
        result = split_nodes_delimiter([node1, node2], "`", TextType.CODE)
        expected = [
            TextNode("bold", TextType.BOLD),
            TextNode(" plain ", TextType.PLAIN),
            TextNode("c", TextType.CODE),
            TextNode("", TextType.PLAIN),
        ]
        self.assertEqual(result, expected)

class TestExtractMarkdown(unittest.TestCase):
    def test_extract_markdown_images(self):
        text = "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        expected = [("image", "https://i.imgur.com/zjjcJKZ.png")]
        self.assertListEqual(extract_markdown_images(text), expected)

    def test_extract_multiple_images(self):
        text = "Here ![one](url1) and ![two](url2)"
        expected = [("one", "url1"), ("two", "url2")]
        self.assertListEqual(extract_markdown_images(text), expected)

    def test_extract_markdown_links(self):
        text = "A [link](https://example.com) and [another](http://test.com)"
        expected = [("link", "https://example.com"), ("another", "http://test.com")]
        self.assertListEqual(extract_markdown_links(text), expected)

    def test_links_not_images(self):
        text = "Image ![alt](img) and [link](url)"
        exp_images = [("alt", "img")]
        exp_links = [("link", "url")]
        self.assertListEqual(extract_markdown_images(text), exp_images)
        self.assertListEqual(extract_markdown_links(text), exp_links)

    def test_no_matches(self):
        text = "No markdown here"
        self.assertListEqual(extract_markdown_images(text), [])
        self.assertListEqual(extract_markdown_links(text), [])

class TestSplitImageNodes(unittest.TestCase):
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.PLAIN,
        )
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("This is text with an ", TextType.PLAIN),
            TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            TextNode(" and another ", TextType.PLAIN),
            TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
        ]
        self.assertListEqual(new_nodes, expected)

class TestSplitLinkNodes(unittest.TestCase):
    def test_split_links(self):
        node = TextNode(
            "Link [to boot dev](https://www.boot.dev) and [YouTube](https://youtube.com)",
            TextType.PLAIN,
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Link ", TextType.PLAIN),
            TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            TextNode(" and ", TextType.PLAIN),
            TextNode("YouTube", TextType.LINK, "https://youtube.com"),
        ]
        self.assertListEqual(new_nodes, expected)

class TestTextToTextNodes(unittest.TestCase):
    def test_full_markdown(self):
        text = (
            "This is **text** with an _italic_ word and a `code block`"
            " and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg)"
            " and a [link](https://boot.dev)"
        )
        result = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.PLAIN),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.PLAIN),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.PLAIN),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.PLAIN),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.PLAIN),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        self.assertEqual(result, expected)

class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

class TestBlockType(unittest.TestCase):
    def test_heading(self):
        block = "## Heading level 2"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_code_block(self):
        block = "```\nprint(\"hi\")\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_quote_block(self):
        block = "> Quote line 1\n> Quote line 2"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_unordered_list(self):
        block = "- item1\n- item2"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_ordered_list(self):
        block = "1. first\n2. second\n3. third"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_paragraph(self):
        block = "This is just a paragraph."
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)


class TestMarkdownToHtmlNode(unittest.TestCase):
    def test_paragraphs(self):
        md = """
    This is **bolded** paragraph
    text in a p
    tag here

    This is another paragraph with _italic_ text and `code` here

    """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
    ```
    This is text that _should_ remain
    the **same** even with inline stuff
    ```
    """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

if __name__ == "__main__":
    unittest.main()


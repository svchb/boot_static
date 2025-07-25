import re
import textwrap
from typing import List
from enum import Enum
from textnode import TextNode, TextType
from htmlnode import text_node_to_html_node, LeafNode, ParentNode


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    """
    Split TEXT-type TextNode objects on a delimiter into a mix of plain and typed nodes.
    Args:
        old_nodes: list of TextNode
        delimiter: string delimiter to split on
        text_type: TextType to use for the parts between delimiters
    Returns:
        list of TextNode with types PLAIN or text_type
    """
    new_nodes = []
    for node in old_nodes:
        # Only split plain text nodes
        if node.text_type != TextType.PLAIN:
            new_nodes.append(node)
            continue
        parts = node.text.split(delimiter)
        for idx, part in enumerate(parts):
            if idx % 2 == 0:
                # plain text segment
                new_nodes.append(TextNode(part, TextType.PLAIN))
            else:
                # delimited segment
                new_nodes.append(TextNode(part, text_type))
    return new_nodes


def extract_markdown_images(text: str):
    """
    Extract markdown image tags of the form ![alt](url) from text.
    Returns list of (alt, url) tuples.
    """
    pattern = r'!\[([^\]]*)\]\(([^\)]+)\)'
    return re.findall(pattern, text)


def extract_markdown_links(text: str):
    """
    Extract markdown link tags of the form [text](url) from text.
    Returns list of (text, url) tuples.
    """
    # To avoid capturing images, negative lookbehind for '!'
    pattern = r'(?<!!)\[([^\]]+)\]\(([^\)]+)\)'
    return re.findall(pattern, text)

def split_nodes_image(old_nodes):
    """
    Split plain TextNode objects around markdown image syntax into Text and Image nodes.
    """
    new_nodes = []
    image_pattern = re.compile(r'!\[([^\]]*)\]\(([^\)]+)\)')
    for node in old_nodes:
        if node.text_type != TextType.PLAIN:
            new_nodes.append(node)
            continue
        text = node.text
        last_end = 0
        for m in image_pattern.finditer(text):
            # preceding text
            if m.start() > last_end:
                new_nodes.append(TextNode(text[last_end:m.start()], TextType.PLAIN))
            alt, url = m.groups()
            new_nodes.append(TextNode(alt, TextType.IMAGE, url))
            last_end = m.end()
        # tail text
        if last_end < len(text):
            new_nodes.append(TextNode(text[last_end:], TextType.PLAIN))
    return new_nodes


def split_nodes_link(old_nodes):
    """
    Split plain TextNode objects around markdown link syntax into Text and Link nodes.
    """
    new_nodes = []
    link_pattern = re.compile(r'(?<!!)\[([^\]]+)\]\(([^\)]+)\)')
    for node in old_nodes:
        if node.text_type != TextType.PLAIN:
            new_nodes.append(node)
            continue
        text = node.text
        last_end = 0
        for m in link_pattern.finditer(text):
            if m.start() > last_end:
                new_nodes.append(TextNode(text[last_end:m.start()], TextType.PLAIN))
            anchor, url = m.groups()
            new_nodes.append(TextNode(anchor, TextType.LINK, url))
            last_end = m.end()
        if last_end < len(text):
            new_nodes.append(TextNode(text[last_end:], TextType.PLAIN))
    return new_nodes


def text_to_textnodes(text: str):
    """
    Convert a raw markdown string into a list of TextNode objects, handling images, links, code, bold, and italic inline.
    """
    nodes = [TextNode(text, TextType.PLAIN)]
    # handle images first
    nodes = split_nodes_image(nodes)
    # then links
    nodes = split_nodes_link(nodes)
    # then code spans
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    # then bold (**) before italic
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    # then italic (_)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    return nodes

def markdown_to_blocks(markdown: str) -> List[str]:
    """
    Split a raw markdown document into block strings separated by blank lines.
    """
    blocks = markdown.split("\n\n")
    stripped = [block.strip() for block in blocks]
    return [block for block in stripped if block]

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


def block_to_block_type(block: str) -> BlockType:
    # Heading: starts with 1-6 '#' + space
    if re.match(r'^#{1,6} ', block):
        return BlockType.HEADING
    # Code block: starts and ends with triple backticks
    if block.startswith("```") and block.strip().endswith("```"):
        return BlockType.CODE
    # Quote block: every line starts with '>'
    lines = block.split('\n')
    if all(line.startswith('>') for line in lines):
        return BlockType.QUOTE
    # Unordered list: every line starts with '- '
    if all(re.match(r'^- ', line) for line in lines):
        return BlockType.UNORDERED_LIST
    # Ordered list: lines start at 1.,2.,... increment
    nums = []
    for line in lines:
        m = re.match(r'^(\d+)\. ', line)
        if not m:
            nums = []
            break
        nums.append(int(m.group(1)))
    if nums and nums == list(range(1, len(nums)+1)):
        return BlockType.ORDERED_LIST
    # Default paragraph
    return BlockType.PARAGRAPH

def markdown_to_html_node(markdown: str) -> ParentNode:
    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        btype = block_to_block_type(block)
        if btype == BlockType.HEADING:
            m = re.match(r'^(#{1,6}) +(.*)', block)
            level = len(m.group(1))
            text = m.group(2)
            inline = text_to_textnodes(text)
            html_children = [text_node_to_html_node(n) for n in inline]
            children.append(ParentNode(f'h{level}', html_children))
        elif btype == BlockType.CODE:
            lines = block.split('\n')
            content = "\n".join(lines[1:-1])
            dedented = textwrap.dedent(content)
            code_text = dedented + '\n'
            code_node = LeafNode('code', code_text)
            children.append(ParentNode('pre', [code_node]))
        elif btype == BlockType.QUOTE:
            lines = [line.lstrip('> ').rstrip() for line in block.split('\n')]
            text = '\n'.join(lines)
            inline = text_to_textnodes(text)
            html_children = [text_node_to_html_node(n) for n in inline]
            children.append(ParentNode('blockquote', html_children))
        elif btype == BlockType.UNORDERED_LIST:
            items = []
            for line in block.split('\n'):
                item_text = line[2:]
                inline = text_to_textnodes(item_text)
                html_children = [text_node_to_html_node(n) for n in inline]
                items.append(ParentNode('li', html_children))
            children.append(ParentNode('ul', items))
        elif btype == BlockType.ORDERED_LIST:
            items = []
            for line in block.split('\n'):
                m = re.match(r'^([0-9]+)[.] +(.*)', line)
                item_text = m.group(2)
                inline = text_to_textnodes(item_text)
                html_children = [text_node_to_html_node(n) for n in inline]
                items.append(ParentNode('li', html_children))
            children.append(ParentNode('ol', items))
        else:
            paragraph_text = re.sub(r'\s+', ' ', block.strip())
            inline = text_to_textnodes(paragraph_text)
            html_children = [text_node_to_html_node(n) for n in inline]
            children.append(ParentNode('p', html_children))
    return ParentNode('div', children)


def extract_title(markdown: str) -> str:
    """
    Find the first H1 line (“# Title”) and return its text.
    Raises ValueError if no H1 is present.
    """
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    raise ValueError("No H1 title found in markdown")

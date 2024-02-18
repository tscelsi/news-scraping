import re

from bs4 import BeautifulSoup, Tag

UNINTERESTING_TAGS = [
    "noscript",
    "script",
    "style",
    "iframe",
    "footer",
    "header",
    "nav",
    "aside",
]

INTERESTING_TAGS = [
    "body",
    "html",
    "div",
    "ul",
    "ol",
    "li",
    "p",
    "a",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "span",
    "article",
    "section",
    "main",
]

AnchorTag = Tag


def find_all_anchor_tags(soup: BeautifulSoup) -> str:
    anchors = soup.find_all("a")
    text_parts = []
    for anchor in anchors:
        anchor_text = anchor.text.replace("\n", " ")
        anchor_text = re.sub(" +", " ", anchor_text)
        anchor_text = anchor_text.strip()
        href = anchor.get("href")
        if not href or not anchor_text:
            continue
        text_parts.append(f"{anchor_text} ({href})")
    return " ".join(text_parts)


def remove_uninteresting_paths(tag: Tag):
    """Remove uninteresting paths from the HTML."""
    children = tag.contents.copy()
    for child in children:
        if isinstance(child, Tag):
            if child.name in UNINTERESTING_TAGS:
                child.decompose()
            else:
                remove_uninteresting_paths(child)


def keep_only_interesting_paths(tag: Tag) -> bool:
    """We only retain paths that a) contain interesting tags and b) contain at least one
    <a> tag."""
    some_child_contains_a_tag = False
    children = tag.contents.copy()
    for child in children:
        if isinstance(child, Tag):
            if child.name not in INTERESTING_TAGS:
                child.decompose()
                continue
            child_contains_a_tag = keep_only_interesting_paths(child)
            # switch flag to true if any child contains <a> tag
            some_child_contains_a_tag = (
                some_child_contains_a_tag or child_contains_a_tag
            )
            # if child does not contain <a> tag, we can prune it
            if not child_contains_a_tag:
                child.decompose()
    return tag.name == "a" or some_child_contains_a_tag


def create_soup_for_article_link_retrieval(html_page: str) -> BeautifulSoup:
    """Create a BeautifulSoup object from the HTML page.

    Args:
        html_page (str): The HTML page to parse.

    Returns:
        BeautifulSoup: The parsed HTML page.
    """
    soup = BeautifulSoup(html_page, "html.parser")
    keep_only_interesting_paths(soup)
    body = soup.find("body")
    body_soup = BeautifulSoup(str(body), "html.parser")
    return body_soup


def create_soup(html_page: str) -> BeautifulSoup:
    soup = BeautifulSoup(html_page, "html.parser")
    remove_uninteresting_paths(soup)
    return soup

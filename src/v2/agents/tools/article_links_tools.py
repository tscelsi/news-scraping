import re

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import tool

from v2.heuristic import a_inside_tag, check_upward_keyword_in_tag
from v2.soup_helpers import create_soup, find_all_anchor_tags
from v2.text_helpers import asciify

article_and_href_pattern = re.compile(r"(\S.*?) \((.*?)\)")


class ListArticleInput(BaseModel):
    html_str: str = Field(description="The html string to be parsed")


@tool("ListAnchors")
def list_anchor_tag_info(html_str: str) -> str:
    """List the textual content and href of all the anchor tags within the html string.
    Example return value:
        ASX climbs on tech rally; Altium soars, BHP slumps (/business/markets/asx-set-to-rise-as-wall-street-steadies-a-rises-20240215-p5f52t.html)
    Where the title is followed by the href in parentheses."""
    soup = create_soup(html_str)
    anchors = find_all_anchor_tags(soup)
    return anchors


@tool("GatherAnchorMetadata")
def extract_anchor_information(html_str: str, anchors_str: str) -> list[tuple]:
    """Extracts information about the anchor tags in the html string.

    Returns:
        A list of tuples containing the
        anchor text, href, whether the anchor is nested inside an <article> tag, whether
        the anchor is nested inside an <li> tag and whether the href ends with .html.
    """
    soup = create_soup(html_str)
    anchors: list[tuple[str, str]] = re.findall(article_and_href_pattern, anchors_str)
    anchor_list = []
    for anchor_text, anchor_href in anchors:
        a_tag = soup.find("a", text=anchor_text, href=anchor_href)
        if not a_tag:
            a_tag = soup.find("a", href=anchor_href)
        if not a_tag:
            continue
        # use these heuristics as extra metadata to help inform LLM model and assist
        # with isolating only article links
        has_title_in_attrs = check_upward_keyword_in_tag(a_tag, "title", max_depth=2)
        is_inside_article_tag = a_inside_tag(a_tag, "article", max_depth=5)
        is_inside_li_tag = a_inside_tag(a_tag, "li", max_depth=5)
        ends_with_dot_html = anchor_href.endswith(".html")
        anchor_list.append(
            (
                asciify(anchor_text),
                asciify(anchor_href),
                has_title_in_attrs,
                is_inside_article_tag,
                is_inside_li_tag,
                ends_with_dot_html,
            )
        )
    return anchor_list

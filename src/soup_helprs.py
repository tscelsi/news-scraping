from bs4 import Tag, BeautifulSoup

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


def keep_only_interesting_paths(tag: Tag) -> bool:
    """We only retain paths that a) contain interesting tags and b) contain at
    least one <a> tag."""
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


def keyword_in_tag_attributes(tag: Tag, keyword: str) -> bool:
    """Checks if a tag has a keyword in any of its attributes."""
    for attribute in tag.attrs.values():
        if keyword in attribute:
            return True
    return False


def check_upward_keyword_in_tag(
    tag: Tag,
    keyword: str,
    max_depth: int = 0,
) -> bool:
    """Heuristic 2: check if any of the parent tags contain 'article' in their
    attributes."""
    curr_depth = 0
    tag = tag
    while tag and curr_depth <= max_depth:
        if keyword_in_tag_attributes(tag, keyword):
            return True
        tag = tag.parent
        curr_depth += 1
    return False


def a_inside_tag(
    anchor: Tag,
    target_tag_name: str,
    max_depth: int = 1,
) -> bool:
    """Heuristic 3: check if <a> tag is inside some other tag."""
    curr_depth = 0
    curr_tag = anchor
    while curr_tag and curr_depth <= max_depth:
        if curr_tag.name == target_tag_name:
            return True
        curr_tag = curr_tag.parent
        curr_depth += 1
    return False


def has_neighbouring_heading_tag(anchor: Tag) -> bool:
    """Check to see if the tag has a neighbouring heading tag
    in either the child or parent direction. Downwards, the heading
    tag must be directly below the tag. Upwards, the heading tag
    can be some level of nesting above."""
    children = anchor.contents
    for child in children:
        if isinstance(child, Tag):
            if child.name.startswith("h"):
                return True
    if (
        a_inside_tag(anchor, "h5", max_depth=2)
        or a_inside_tag(anchor, "h4", max_depth=2)
        or a_inside_tag(anchor, "h3", max_depth=2)
        or a_inside_tag(anchor, "h2", max_depth=2)
    ):
        return True
    return False


def heuristic_article_in_attributes(soup: BeautifulSoup) -> list[AnchorTag]:
    """Heuristic function that checks to see if there is some mention of
    'article' in the <a> tag attributes, or in the attributes of any of
    its parents (up to a certain depth)."""
    body = soup.body
    keep_only_interesting_paths(body)
    a_tags = body.find_all("a")
    article_links = []
    for a in a_tags:
        if check_upward_keyword_in_tag(a, "article", max_depth=1):
            article_links.append(a)
    return article_links


def heuristic_anchor_inside_article_tag(
    soup: BeautifulSoup,
) -> list[AnchorTag]:
    """A heuristic that checks to see if the <a> tag is a child inside an
    <article> tag. As long as the <a> tag is not too deep inside the <article>.
    """
    body = soup.body
    keep_only_interesting_paths(body)
    a_tags = body.find_all("a")
    article_links = []
    for a in a_tags:
        if a_inside_tag(a, "article", max_depth=5):
            article_links.append(a)
    return article_links


def heuristic_anchor_inside_list_tag(soup: BeautifulSoup) -> list[AnchorTag]:
    """A heuristic that checks to see if the <a> tag is a child inside an
    <li> tag. As long as the <a> tag is not too deep inside the <li>.
    """
    body = soup.body
    keep_only_interesting_paths(body)
    a_tags = body.find_all("a")
    article_links = []
    for a in a_tags:
        if a_inside_tag(a, "li", max_depth=5):
            article_links.append(a)
    return article_links


def heuristic_has_neighbouring_heading(
    soup: BeautifulSoup,
) -> list[AnchorTag]:
    """Heuristic that returns all <a> tags that are inside an <article> tag
    (up to depth 5) and have a neighbouring <h*> tag."""
    body = soup.body
    keep_only_interesting_paths(body)
    a_tags = body.find_all("a")
    article_links = []
    for a in a_tags:
        if has_neighbouring_heading_tag(a):
            article_links.append(a)
    return article_links


def heuristic_dot_html(soup: BeautifulSoup) -> list[AnchorTag]:
    """A heuristic that checks to see if the <a> tag has a .html link.
    Returns the link if it does."""
    body = soup.body
    keep_only_interesting_paths(body)
    a_tags = body.find_all("a")
    article_links = []
    for a in a_tags:
        if a["href"].endswith(".html"):
            article_links.append(a)
    return article_links


class Runner:
    """TODO: This will eventually be a langchain agent"""
    def run_heuristics(self):
        pass

    def run_filters(self):
        """Make call to openai or whatever and filter out bad links."""
        pass

    def find_paths(self):
        """Find the paths to our candidate links from the root of the soup"""
        pass

    def run(self):
        self.run_heuristics()
        self.run_filters()
        self.find_paths()

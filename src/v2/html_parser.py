from hashlib import sha256

from bs4 import BeautifulSoup, Tag


def get_unique_anchor_traces(
    article_links: list[str], html: BeautifulSoup
) -> list[list[str]]:
    """TODO: DOCS"""
    anchor_paths = []
    existing_path_hashes = []
    for link in article_links:
        anchor = html.find("a", href=link)
        anchor_trace = _trace_anchor_to_root(anchor)
        hash = sha256(str(anchor_trace).encode("utf-8")).hexdigest()
        if hash not in existing_path_hashes:
            anchor_paths.append(anchor_trace[::-1])
            existing_path_hashes.append(hash)
    return anchor_paths


def _trace_anchor_to_root(anchor: BeautifulSoup) -> list[tuple[str, dict]]:
    """Traces a tag to the root of the BeautifulSoup.

    Args:
        tag: The tag to trace.
        filters: A list of dictionaries that contain the tag name and attributes to filter
            the trace by.

    Returns:
        A list of tags that trace from the tag to the root of the HTML.
    """
    current_anchor = anchor
    trace = []
    while current_anchor:
        trace.append(current_anchor.name)
        if current_anchor.parent.parent is None:
            break
        current_anchor = current_anchor.parent
    return trace


def find_tags_from_traces(root: Tag, traces: list[list[str]]) -> list[Tag]:
    """Finds the tags that match the anchor traces.

    Args:
        soup: The HTML to search.
        anchor_traces: The anchor traces to match.

    Returns:
        A list of anchor tags that match the anchor traces.
    """
    anchor_tags = []
    for trace in traces:
        anchor_tags.extend(_find_anchor_tags_from_trace(root, trace))
    return anchor_tags


def _find_anchor_tags_from_trace(root_tag: Tag, trace: list[str]):
    """Finds the anchor tags that match the traces.
    An anchor trace may look like ["body", "div", "a"].
    A trace should end with an anchor tag ("a").

    Args:
        soup (BeautifulSoup): The HTML to search.
        trace (list[str]): The anchor traces to match.
    """
    if len(trace) == 1 and trace[0] != "a":
        raise ValueError("The trace must start with an anchor tag.")
    elif len(trace) == 1:
        return root_tag.find_all("a", recursive=False)
    tags = []
    current_tag, *trace = trace
    candidates = root_tag.find_all(current_tag, recursive=False)
    for c in candidates:
        result = _find_anchor_tags_from_trace(c, trace)
        tags.extend(result)
    return tags

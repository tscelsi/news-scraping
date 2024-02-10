from bs4 import BeautifulSoup


def get_h1_text_content(soup: BeautifulSoup) -> bool:
    """Assumes there is only h1 in a doc. If there are more, doesn't look"""
    h1_tag = soup.find("h1")
    if h1_tag:
        return h1_tag.get_text()
    return None

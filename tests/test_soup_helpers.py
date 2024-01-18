from src.soup_helprs import keep_only_interesting_paths
from bs4 import BeautifulSoup
import pytest
from src.consts import TEST_DIR


def test_keep_only_interesting_paths():
    soup = BeautifulSoup(
        '<div><p><a href="foo">foo</a></p><p><a href="bar">bar</a></p></div>',
        "html.parser",
    )
    keep_only_interesting_paths(soup)
    assert soup.contents[0].name == "div"
    assert soup.div.p.a["href"] == "foo"


def test_keep_only_interesting_paths_no_paths_kept(soup):
    soup = BeautifulSoup(
        "<div><p>hi</p></div>",
        "html.parser",
    )
    keep_only_interesting_paths(soup)
    assert soup.contents == []


def test_keep_only_interesting_paths_remove_path_with_no_link(soup):
    soup = BeautifulSoup(
        '<div><p><a href="foo">foo</a></p><p>hi</p></div><iframe></iframe>',
        "html.parser",
    )
    keep_only_interesting_paths(soup)
    assert soup.contents[0].name == "div"
    # removes the <p> tag with no <a> tag
    assert len(soup.find_all("p")) == 1
    # assert iframe removed
    assert len(soup.find_all("iframe")) == 0


def test_keyword_in_tag_attributes():
    from src.soup_helprs import keyword_in_tag_attributes

    soup = BeautifulSoup(
        '<a href="foo">foo</a>',
        "html.parser",
    )
    assert not keyword_in_tag_attributes(soup.a)
    soup = BeautifulSoup(
        '<a test-id="article-link" href="foo">foo</a>',
        "html.parser",
    )
    assert keyword_in_tag_attributes(soup.a)


def test_check_upward_keyword_in_tag():
    from src.soup_helprs import check_upward_keyword_in_tag

    soup = BeautifulSoup(
        '<div><a href="foo">foo</a><div>',
        "html.parser",
    )
    a_tag = soup.a
    assert not check_upward_keyword_in_tag(a_tag, "article")
    soup = BeautifulSoup(
        '<div test-id="article-link"><a href="foo">foo</a><div>',
        "html.parser",
    )
    a_tag = soup.a
    # checks only the a tag
    assert not check_upward_keyword_in_tag(a_tag, "article", max_depth=0)
    # checks the a tag and its parent
    assert check_upward_keyword_in_tag(a_tag, "article", max_depth=1)


def test_a_inside_tag():
    from src.soup_helprs import a_inside_tag

    soup = BeautifulSoup(
        '<h3><a href="foo">foo</a></h3>',
        "html.parser",
    )
    a_tag = soup.a
    assert a_inside_tag(a_tag, "h3")
    soup = BeautifulSoup(
        '<h3><div><a href="foo">foo</a></div></h3>',
        "html.parser",
    )
    assert not a_inside_tag(soup.a, "h3")
    assert a_inside_tag(soup.a, "h3", max_depth=2)


@pytest.fixture
def soup():
    with open(TEST_DIR / "fixtures" / "theage.html") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    yield soup


def test_article_keyword_heuristic(soup):
    from src.soup_helprs import article_keyword_heuristic

    article_links = article_keyword_heuristic(soup)
    print("HI")


def test_has_neighbouring_heading_tag():
    from src.soup_helprs import has_neighbouring_heading_tag
    # when h3 wraps a directly, is true
    soup = BeautifulSoup(
        '<h3><a href="foo">foo</a></h3>',
        "html.parser",
    )
    assert has_neighbouring_heading_tag(soup.a)
    # when h3 wraps a with some level of nesting, is true
    soup = BeautifulSoup(
        '<h3><div><a href="foo">foo</a></div></h3>',
        "html.parser",
    )
    assert has_neighbouring_heading_tag(soup.a)
    # when h3 is not direct child of <a>, is false
    soup = BeautifulSoup(
        '<a href="foo"><p><h3>test</h3></p></a>',
        "html.parser",
    )
    assert not has_neighbouring_heading_tag(soup.a)
    # when h3 is direct child of <a>, is true
    soup = BeautifulSoup(
        '<a href="foo"><h3>test</h3></a>',
        "html.parser",
    )
    assert has_neighbouring_heading_tag(soup.a)

from pathlib import Path

import pytest
from bs4 import BeautifulSoup

TEST_DIR = Path(__file__).parent
PKG_DIR = TEST_DIR.parent / "ai_play"


@pytest.fixture
def soup():
    html = """
    <body>
    <a href="/link-1">Link 1</a>
    <a href="/link-2">Link 2</a>
    <div><a href="/link-3">Link 3</a></div>
    </body>
    """
    soup_ = BeautifulSoup(html, "html.parser")
    return soup_


@pytest.fixture
def theage():
    html = open(PKG_DIR / "theage.html").read()
    soup_ = BeautifulSoup(html, "html.parser")
    return soup_


def test_trace_anchor_to_root(soup: BeautifulSoup):
    from v2.html_parser import _trace_anchor_to_root

    tag = soup.find("a")
    trace = _trace_anchor_to_root(tag)
    assert trace == [
        "a",
        "body",
    ]


def test_get_unique_anchor_traces(soup):
    from v2.html_parser import get_unique_anchor_traces

    article_links = ["/link-1", "/link-2"]
    link_traces = get_unique_anchor_traces(article_links, soup)
    assert len(link_traces) == 1
    assert link_traces == [
        [
            "body",
            "a",
        ]
    ]

    # article links with different traces
    article_links = ["/link-1", "/link-2", "/link-3"]
    link_traces = get_unique_anchor_traces(article_links, soup)
    assert len(link_traces) == 2
    assert link_traces == [
        [
            "body",
            "a",
        ],
        [
            "body",
            "div",
            "a",
        ],
    ]


def test_find_anchor_tags_from_traces(soup):
    from v2.html_parser import find_anchor_tags_from_traces

    anchor_traces = [["body", "a"], ["body", "div", "a"]]
    tags = find_anchor_tags_from_traces(soup, anchor_traces)
    assert len(tags) == 3
    assert tags[0].attrs["href"] == "/link-1"
    assert tags[1].attrs["href"] == "/link-2"
    assert tags[2].attrs["href"] == "/link-3"


def test_find_anchor_tags_from_trace(soup):
    from v2.html_parser import _find_anchor_tags_from_trace

    result = _find_anchor_tags_from_trace(soup.body, ["a"])
    assert len(result) == 2
    result = _find_anchor_tags_from_trace(soup, ["body", "a"])
    assert len(result) == 2
    result = _find_anchor_tags_from_trace(soup, ["body", "div", "a"])
    assert len(result) == 1


def test_e2e(theage):
    from v2.html_parser import find_anchor_tags_from_traces, get_unique_anchor_traces

    article_links = [
        "/business/companies/tesla-and-elon-musk-face-a-bumpy-road-ahead-20240123-p5ezcc.html",
        "/business/markets/asx-set-to-dip-despite-wall-street-gains-20240123-p5ezag.html",
        "/business/banking-and-finance/future-fund-chair-says-it-is-far-too-early-to-expect-rate-cuts-20240123-p5ezcq.html",
        "/business/banking-and-finance/heat-fading-from-mortgage-war-as-banks-protect-margins-20240122-p5ez4u.html",
        "/business/companies/retail-rainmaker-mark-mcinnes-seals-deal-with-a-different-self-made-billionaire-20240122-p5ez4e.html",
        "/business/companies/abhorrent-and-incorrect-ita-buttrose-rejects-staff-attack-on-management-20240123-p5eziz.html",
        "/business/companies/australia-is-right-in-the-thick-of-a-critical-minerals-problem-20240123-p5ezd2.html",
        "/business/companies/tesla-and-elon-musk-face-a-bumpy-road-ahead-20240123-p5ezcc.html",
        "/business/companies/senior-journalist-lashes-abc-management-as-staff-vote-no-confidence-in-managing-director-20240122-p5ez4h.html",
        "/business/companies/forrest-the-next-to-close-wa-nickel-mines-as-price-slumps-20240122-p5ez5f.html",
        "/business/markets/asx-set-to-dip-despite-wall-street-gains-20240123-p5ezag.html",
        "/business/markets/asx-set-to-rise-as-wall-street-rallies-to-record-high-20240122-p5ez0j.html",
        "/business/markets/sharemarkets-are-booming-here-s-why-it-may-not-last-20240122-p5ez1c.html",
        "/business/the-economy/china-s-ridiculed-plane-has-an-unexpected-chance-to-paint-the-skies-red-20240116-p5exjv.html",
        "/business/the-economy/it-s-hard-to-get-people-back-into-the-office-good-20240116-p5exmg.html",
        "/business/the-economy/the-west-has-to-stop-giving-china-a-free-ride-20240117-p5exua.html",
        "/business/companies/abhorrent-and-incorrect-ita-buttrose-rejects-staff-attack-on-management-20240123-p5eziz.html",
        "/business/companies/former-afr-columnist-to-write-book-on-alan-joyce-s-final-years-at-qantas-20240122-p5ez4i.html",
        "/business/companies/luke-mcilveen-appointed-executive-editor-of-nine-s-metro-mastheads-20240122-p5ez21.html",
        "/business/workplace/more-pay-not-free-yoga-workplace-wellness-programs-have-little-benefit-20240118-p5eyai.html",
        "/business/workplace/boasting-equity-at-work-while-laying-off-hundreds-pull-the-other-one-20240118-p5eybu.html",
        "/business/workplace/why-we-need-to-stop-asking-what-do-you-do-for-work-20240118-p5eyaq.html",
        "/business/companies/vogue-house-sold-to-billionaire-israeli-shipping-mogul-for-142-million-20240109-p5evyt.html",
        "/business/companies/construction-costs-stabilising-but-a-rocky-road-lies-ahead-20231219-p5esf9.html",
        "/business/companies/stockland-inks-1-3b-deal-as-it-bets-on-a-housing-rebound-20231215-p5eruo.html",
        "/business/companies/forrest-the-next-to-close-wa-nickel-mines-as-price-slumps-20240122-p5ez5f.html",
        "/business/companies/rio-tinto-delivers-another-bumper-iron-ore-year-20240116-p5exo8.html",
        "/business/companies/mining-giant-charges-dropped-over-harassment-documents-20231218-p5esb2.html",
    ]
    traces = get_unique_anchor_traces(article_links, html=theage)
    a_tags = find_anchor_tags_from_traces(theage, traces)
    for tag in a_tags:
        assert tag.attrs["href"].startswith("/business")

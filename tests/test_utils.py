from src.utils import normalise_tag

def test_normalise_tag():
    assert normalise_tag("Hello World") == "hello-world"
    assert normalise_tag("Hello World!") == "hello-world"
    assert normalise_tag("Hello World!!") == "hello-world"
    assert normalise_tag("Hello  World!") == "hello-world"
    assert normalise_tag("Hello's  World!") == "hello-s-world"
    assert normalise_tag("  Hello's  World!  ") == "hello-s-world"

import string
from bs4 import BeautifulSoup
import json


def normalise_tag(tag: str):
    """We want to:
    1. lowercase
    2. remove all punctuation and replace with a space
    3. remove all excess whitespace
    4. replace all spaces with hyphen
    """
    normalised_tag = tag.lower().translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation)))
    normalised_tag = ' '.join(normalised_tag.strip().split())
    normalised_tag = normalised_tag.replace(' ', '-')
    return normalised_tag


def normalise_tags(*tags: str):
    return [normalise_tag(tag) for tag in tags]

## Some scraping tools
def find_json_objects(text: str, decoder=json.JSONDecoder()):
    """Find JSON objects in text, and generate decoded JSON data"""
    pos = 0
    while True:
        match = text.find("{", pos)
        if match == -1:
            break
        try:
            result, index = decoder.raw_decode(text[match:])
            yield result
            pos = match + index
        except ValueError:
            pos = match + 1


def find_objects(soup: BeautifulSoup):
    """Find JSON objects in script tags"""
    objs = []
    for script_tag in soup.findAll('script'):
        try:
            objs.extend([obj for obj in find_json_objects(script_tag.text)])
        except:
            continue
    return [x for x in objs if x != {}]

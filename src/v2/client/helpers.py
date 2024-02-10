from urllib.parse import urlparse


def get_url_stem(url: str):
    parsed_url = urlparse(url)
    url_path_parts = parsed_url.path.rsplit("/", 1)
    if len(url_path_parts) > 1:
        return parsed_url.netloc + parsed_url.path.rsplit("/", 1)[0]
    elif len(url_path_parts) == 1:
        return parsed_url.netloc
    return parsed_url.netloc


def get_domain(url: str):
    parsed_url = urlparse(url)
    return parsed_url.netloc

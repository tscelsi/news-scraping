import os
from pathlib import Path

# allows to locate root dir of project easily
SRC_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
SCRAPER_DIR = SRC_DIR / 'scrapers'
ROOT_DIR = SRC_DIR.parent
TEST_DIR = Path(ROOT_DIR) / 'tests'

HEADERS = {
    "user-agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1",
    "content-type": "application/json",
    "accept": "*/*",
    "sec-fetch-site": "same-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "accept-language": "en-US,en;q=0.9",
}
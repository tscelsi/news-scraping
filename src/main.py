import sys
from typing import Awaitable
import argparse
import asyncio
import logging
import functools
import itertools
import traceback

from confection import registry, Config
import aiometer

from consts import ROOT_DIR
from models import Article
import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



async def _wrapper(engine):
    try:
        articles = await engine.run()
        return articles
    except Exception as e:
        logger.error(traceback.print_tb(e.__traceback__))
        logger.error(f'Engine {engine._name} failed with error {e}')


async def run_from_config(config: dict):    
    results = await aiometer.run_all([functools.partial(_wrapper, engine) for engine in config.values()])
    results = filter(None, results)
    return list(itertools.chain.from_iterable(results))


async def run_from_list(config: list):
    """From list of config dicts.
    [{
        module: "bbc",
        path: "news/science-environment-56837908",
        max_at_once: 4,
        max_per_second: 4,
        db_uri: null,
        db_must_connect: false,
        debug: false,
    },
    ...,
    ]
    """
    engines = [engine._factory(**engine_config) for engine_config in config]
    results = await aiometer.run_all([functools.partial(_wrapper, engine) for engine in engines])
    results = filter(None, results)
    return list(itertools.chain.from_iterable(results))


async def main(config_path: str) -> Awaitable[list[Article]]:
    config = Config().from_disk(ROOT_DIR / config_path)
    resolved = registry.resolve(config)
    results = await run_from_config(resolved)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Run a bite-sized news outlet scraper.')
    parser.add_argument(
        'config', type=str, help='path to config file. This path should be relative to the root directory. For examples, see the templates/ folder.')
    args = parser.parse_args()
    asyncio.run(main(args.config))

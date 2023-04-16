# pileof.news Scraping Engine

**The pileof.news frontend repository can be found [here](https://github.com/tscelsi/news-frontend).**

- [pileof.news Scraping Engine](#pileofnews-scraping-engine)
  - [Sources](#sources)
  - [Strategy](#strategy)
  - [Using the scraping engine](#using-the-scraping-engine)
    - [Installation](#installation)
    - [Configuration](#configuration)
    - [Running](#running)
  - [Writing your own scraper](#writing-your-own-scraper)
  - [API](#api)


The [pileof.news](https://news-frontend-kappa.vercel.app/) scraping engine can be used to scrape news articles from different sources.

The goals of this repository are to:
1. Create a flexible framework for scraping news websites able to be used by any developer for any news site (or, realistically, any listing website).
2. Create a historical database of news articles that may be used for research purposes.

## Sources

✅ = ready || ⏱ = in progress || ❌ = not yet

**Source** | **Module** | **Status** | **Version**
--- | --- | --- | ---
BBC | bbc | ✅ | v1
The Guardian | guardian | ✅ | v1
Al Jazeera | aljazeera | ✅ | v1
The New York Times | nytimes | ✅ | v1
NPR | npr | ❌ | -
[medium.com](https://medium.com/) | medium | ✅ | v1
**Australian News Outlets**
The Age | theage | ✅ | v1
News.com.au | newscomau | ✅ | v1
Australian Financial Review | afr | ✅ | v1
ABC | abc | ❌ | -


## Strategy
All news listing websites follow a similar pattern:
1. List a section of articles on an index-type page. These pages are usually sectioned into categories such as business, climate, politics etc. or they could be pages that list blog posts on similar topics.
2. From the listing page, a user can navigate to the contents of an article/blog/whatever

To scrape articles from these sorts of websites is rather straightforward:
1. Find a page of a website that lists content that interests you. These could be listing pages that may list news articles about business, climate etc. or they could be pages that list blog posts.
2. From that page, find the navigable links to each article/blog
3. Retrieve the textual content and metadata of each article/blog

## Using the scraping engine

### Installation

Install pipenv and run the following command from the root directory of the project:

```bash
pipenv sync
```

### Configuration

Explosion's [confection](https://github.com/explosion/confection) is used for configuring the scraping engine. Example configuration files can be found in the [/templates](src/templates/) directory. Let's take the [Australian Financial Review](templates/afr.cfg) configuration file as an example:

```bash
1 [afr]
2 @engine = "engine.v1"
3 module="afr"
4 path="politics/federal"
5 max_at_once=4
6 max_per_second=4
7 db_uri=null
8 db_must_connect=false
9 debug=false
```

**Line 1:** You can define an arbitrary name for this configuration block. This name will be used to identify the configuration block when running the scraping engine.

**Line 2:** The `@engine` directive is used to specify the version of the scraping engine to use. The current version is `engine.v1`. The lines that follow this one are specific to the version of the engine that you are using.

**Line 3:** The `module` directive is used to specify the module that will be used to scrape the website. The module name is the name of the python module that is located in the [/modules](src/scrapers/) directory. In this case, the module name is `afr`. You can use the table at the top of this file as a reference for the module names.

**Line 4:** The `path` directive is used to specify the path to the listing page that you want to scrape. In this case, the path is `politics/federal`. This path will be appended to the base URL of the website to form the full URL of the listing page. For example, the full URL of the listing page for the Australian Financial Review is `https://www.afr.com/politics/federal`.

**Line 5:** Under the hood, the scraping engine uses [aiometer](https://github.com/florimondmanca/aiometer) to limit the rate at which articles are scraped. The `max_at_once` directive is used to specify the maximum number of articles that can be scraped at once. This is useful for websites that have rate limiting in place. If you set this value to 4, then the scraping engine will only scrape 4 articles at a time.

**Line 6:** The `max_per_second` directive is used to specify the maximum number of articles that can be scraped per second. This is useful for websites that have rate limiting in place. If you set this value to 4, then the scraping engine will only scrape 4 articles per second.

**Line 7:** The `db_uri` directive is used to specify the URI of the database that you want to use to store the scraped articles. If you set this value to `null`, then the scraped articles are not stored. If you set this value to a valid URI, then the scraped articles will be stored in the database specified by the URI. The database must be a MongoDB database.

**Line 8:** The `db_must_connect` directive is used to specify whether the scraping engine should fail if it cannot connect to the database. If you set this value to `false`, then the scraping engine will continue to scrape articles even if it cannot connect to the database.

**Line 9:** Sets logging level of DEBUG for the scraping engine.

### Running

Once you have created a configuration file (or choose one of the [templates](src/templates/)), you can run the scraping engine in the pipenv environment.

```bash
# from within a pipenv shell instance
$(venv) python main.py <path to config file>

# from outside the pipenv environment
$ pipenv run python main.py <path to config file>

# e.g.
$ pipenv run python main.py templates/afr.cfg
```

## Writing your own scraper

This is still a new project and I opted for speed over extensibility in some cases. It is reasonably easy to write your own scraper but there is definitely room for abstraction into a base class/subclass structure. If you are interested in contributing, please feel free to open an issue or submit a pull request.

You need to add a folder to the `src/scrapers` directory with the name of the module you want to create. The folder should contain a `__init__.py` file and a file containing the contents of your scraper. Your scraper file should contain two functions:

`list_articles` - This function should return a list of URLs to articles that you want to scrape. The function should accept a single argument, which is the URL of the listing page.

`get_article` - This function should return an Article object. The function should accept two arguments: the first is the URL of the article that you want to scrape and the second is the suffix of the URL of the listing page.


You will also need to add your module name to the `outlet` field in the `Article` model in the `src/models/article.py` file. In order to be able to call your scraper in a configuration file.

## API

The scraping engine exposes a very basic API that can be used to manage scraped articles. The API is built using [FastAPI](https://fastapi.tiangolo.com/). This may not be very useful, but can be run using:

```bash
pipenv run python src/app.py
```

You may need to set some environment variables, see [.env.template](.env.template) for more information. You can see the endpoints that are exposed by the API by running the above command to start the API and visiting the `/docs` endpoint (should be [localhost:5000/docs](localhost:5000/docs)).
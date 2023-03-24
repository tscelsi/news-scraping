# Bite-sized News

- [Bite-sized News](#bite-sized-news)
  - [Newspapers](#newspapers)
  - [Philosophy/Motivation (TODO)](#philosophymotivation-todo)
  - [Strategy](#strategy)
    - [1. Finding a page of articles](#1-finding-a-page-of-articles)
    - [Getting an article's contents](#getting-an-articles-contents)
  - [Using the scraping engine](#using-the-scraping-engine)
    - [Installation](#installation)
    - [Configuration](#configuration)
      - [globals](#globals)
      - [lister\_args](#lister_args)
    - [engine.py](#enginepy)
  - [Writing your own scraper](#writing-your-own-scraper)

**NOTE**: This project should be used at own risk and not for commercial purposes. I am not responsible for any legal issues that may arise from using this project.

The bite-sized news project is an engine that can be used to scrape news articles from different news outlets.

The goals of this project are:
1. Create a flexible framework for scraping news websites able to be used by any developer for any news site (or, realistically, any listing website).
2. Create a historical database of news articles that can be used for research purposes.

## Newspapers

✅ = ready || ⏱ = in progress || ❌ = not yet

**Newspaper** | **Module** | **Status** | **Version**
--- | --- | --- | ---
BBC | bbc | ✅ | v1
The Guardian | guardian | ✅ | v1
Al Jazeera | aljazeera | ✅ | v1
The New York Times | nytimes | ✅ | v1
NPR | npr | ❌ | -
**Australian News Outlets**
The Age | theage | ✅ | v1
News.com.au | newscomau | ✅ | v1
Australian Financial Review | afr | ✅ | v1
ABC | abc | ❌ | -

## Philosophy/Motivation (TODO)
## Strategy
When reading news, there are two steps involved:
1. Finding the articles you want to read
2. Reading the contents of the articles you like

This can be translated to the following steps when scraping news articles:
1. Finding a page of a news site that lists articles that interest you. These are broad listing pages that may list articles about business, climate, world news etc.
2. Finding navigable links from a page to each article
3. Retrieving the textual content and metadata of an article

### 1. Finding a page of articles

Any news website generally has two types of pages. A page that contains a list of articles that may interest you, and a page that contains the contents of an article. 

### Getting an article's contents

## Using the scraping engine

### Installation

Install pipenv and run:

```bash
pipenv install --dev
```

### Configuration

Explosion's [confection](https://github.com/explosion/confection) is used for configuring the scraping engine. Example configuration files can be found in the [/templates](src/templates/) directory and an example [base configuration file (*base.cfg*)](base.cfg) is found in the root directory.

```bash
[globals]
module=str
max_at_once=int
max_per_second=int

[lister_args]
...args
```

#### globals

**module**: The module to use for scraping. This should be the name of a module in the [/src/scrapers](src/scrapers/) directory. For a reference of available modules see the [Newspaper](#newspapers) table above.

Under the hood [aiometer](https://github.com/florimondmanca/aiometer) is responsible for implementing a rate-limiting architecture so that we don't overload any news sites with requests. The following configuration options are available:

**max_at_once**: The maximum number of articles to scrape at once. This is used to prevent overloading the server.

**max_per_second**: The number of articles to scrape per second. This is used to prevent overloading the server.

#### lister_args

Under lister_args can be any arguments that are needed to run the list_articles function of a scraper module. This allows the list_articles function for each scraper to differ from others for maximum flexibility.

### engine.py

Once you have created a configuration file (or choose one of the [templates](src/templates/)), you can run the scraping engine in the pipenv environment.

```bash
# from within a pipenv shell instance
$(venv) python engine.py <path to config file>

# from outside the pipenv environment
$ pipenv run python engine.py <path to config file>
```

## Writing your own scraper

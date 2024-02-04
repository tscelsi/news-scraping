# V2 News Scraping Engine (V2NSE)

V2NSE implements an LLM-powered scraping solution to retrieve news article links from
news websites. Given the expensive nature of using LLM's as a information retrieval
tool (i.e. asking an LLM to retrieve all the news article links) instead the LLM is tasked
with identifying (once) the article links on a web page. Each article link is then traced through the HTML parse-tree to create a `trace` of the article link.

This `trace` can then be used on subsequent requests to the web page to locate the article links. This is a much cheaper
strategy to employ to scraping and requires much less interaction with the LLM.

There may be multiple `traces` per-page. This is cool because the one web page may not be limited to finding article links structured in one specific way instead able to locate all the links on the page.
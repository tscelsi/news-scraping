/nlp
POST /nlp/subset - creates a subset index of articles

GET /nlp/subset/:id/embed - generates embeddings for a set of articles in a subset
GET /nlp/subset/:id/tokenize - preprocesses all articles in subset

/strategy
POST /strategy - create a new strategy
    BODY
```json
    {
    "name": "morning",
    "outlets": [{
        "module": "theage",
        "path": "/business/technology"
    }, {
        "module": "theage",
        "path": "/business/markets"
    }],
}
```

GET /strategy - list strategies
GET /strategy/:id - get a strategy by id
POST /strategy/:name - update a strategy
DELETE /strategy/:name - delete a strategy

/run
POST /run?strategy='morning' - run a scrape with the 'strategy' configuration settings
    behind the scenes, creates a new run obj:
```json
   {
    "id": "xxxx",
    "timestamp": "2015-01-01T00:00:00.000Z",
    "strategy": {}, // expanded/frozen strategy object (because strategy might change in future)
    "articles": [
        "xx-yy-zz-id",
        "xx-yy-zz-id",
        ...
    ]
   }
```
    RETURNS id: str - the id of the run
GET /run - lists the runs available

GET /run/:id
    RETURNS a list of articles from the run
DELETE /run/:id - delete a run
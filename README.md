## PizzaIndex

Visit [here](https://aveygo.github.io/PizzaIndex/)

## What is the PizzaIndex
The Pizza Index refers to the sudden, trackable increase of takeout food orders (in this case pizza) made from government offices, particularly the Pentagon and the White House in the United States, before major international events unfold. 

## How is this number calculated?
This site scrapes the live "Popularity" data from google maps from over 30 pizza locations near Washington, D.C., calculates the difference between the expected and observed load, and finds the average. This number is then normalized to a range between zero and one hundred using a cumulative distribution function.

## Why did you make this script?
This is a weekend project that I had on my mind during my finals at uni - nice and quick; but for some reason doesn't exist already.

## Build instructions

PizzaIndex was not really meant to be run by individuals, so I would recommend most people to simply directly connect to the database itself:
```bash
curl -X GET "https://olibvrexvuhsaknckltd.supabase.co/rest/v1/main?select=value&key=eq.latest" -H "apikey: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9saWJ2cmV4dnVoc2FrbmNrbHRkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk4NjczNjMsImV4cCI6MjA2NTQ0MzM2M30.5zmEniAajYqFnMmqcVr5iSMgRBqZ7zNj9E4EDs7wPqY"
```

But if for some reason you just want to run PizzaIndex for yourself:

```bash
sudo docker build -t pizzaindex . --no-cache
sudo docker run -d --restart=always -v .:/app pizzaindex:latest 
```

make sure to also include the ```.env``` file:

```bash
SUPABASE_URL = "https://.../rest/v1/main"
SUPABASE_API_KEY = "123...456"
```


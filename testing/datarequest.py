import requests
import json
import math
import time
from bs4 import BeautifulSoup

def nytimes():
    for i in range(2001, 2002):
        year = str(i)
        link = 'https://api.nytimes.com/svc/search/v2/articlesearch.json?q=Bangladesh&q=flood&fq=pub_year:' + year +'&api-key=ICM207hTShMeUkRbW3PZAyqm3WSPX6L3&page=0'
        r = requests.get(link)
        res = r.json()["response"]["docs"]
        hits = r.json()["response"]["meta"]["hits"]
        pages = math.ceil(hits/10)
        time.sleep(6)
        for j in range(1,pages):
            link = 'https://api.nytimes.com/svc/search/v2/articlesearch.json?q=Bangladesh&q=flood&fq=pub_year:' + year + '&api-key=ICM207hTShMeUkRbW3PZAyqm3WSPX6L3&page='+str(j)
            r = requests.get(link)
            res += r.json()["response"]["docs"]
            time.sleep(6)

        path = 'nytimes/' + str(i) + ".json"
        with open(path, 'w') as outfile:
            json.dump(res, outfile, indent=2)

nytimes()

def extract_article():
    r = requests.get("https://www.nytimes.com/2010/01/04/world/asia/04migrants.html")
    path = "2010_flood1.html"
    open(path, 'w').write(r.text)


# extract_article()

# def twitter():
#     for i in range(2009, 2019):
#         year = str(i)
#         link = 'https://api.nytimes.com/svc/search/v2/articlesearch.json?q=Bangladesh&q=flood&fq=pub_year:' + year +'&api-key=ICM207hTShMeUkRbW3PZAyqm3WSPX6L3'
#         r = requests.get(link)
#         path = 'nytimes/' + str(i) +".json"
#         with open(path, 'w') as outfile:
#             json.dump(r.json(), outfile)
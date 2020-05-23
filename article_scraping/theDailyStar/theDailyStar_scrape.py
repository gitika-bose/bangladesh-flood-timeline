import requests
from datetime import datetime
from bs4 import BeautifulSoup
import json
import os
import shutil
import uuid
from unidecode import unidecode

paper_folder = 'theDailyStar'
paper_folder_data = 'data/'

def parse_date(date_obj):
    if not date_obj: return None
    sp = date_obj.split('T')
    year, month, day = sp[0].split('-')
    return datetime(int(year), int(month), int(day))

def get_content(soup_obj):
    if not soup_obj: return None
    return soup_obj.get('content')

def scrape(sites_i, debug=True, sites=None):
    query_info = None
    if not sites:
        sites = sites_i['sites']
        query_info = {"query": sites_i['query'], "paper": sites_i['paper'], "date_range": sites_i['date_range']}
    site_data = []
    for i,site in enumerate(sites):
        try:
            page = requests.get(site)
            soup = BeautifulSoup(page.text, 'html.parser')

            description = get_content(soup.find('meta', attrs={'name':'description'}))

            abstract = get_content(soup.find('meta', attrs={'name':'abstract'}))
            keywords = get_content(soup.find('meta', attrs={'name':'keywords'}))
            if keywords: keywords = [s.strip() for s in keywords.split(',')]
            news_keywords = get_content(soup.find('meta', attrs={'name':'news_keywords'}))
            datePublished = get_content(soup.find('meta', property='article:published_time'))
            if datePublished: datePublished = parse_date(datePublished)
            dateModified = get_content(soup.find('meta', property='article:modified_time'))
            if dateModified: dateModified = parse_date(dateModified)

            headline = soup.find('h1', itemprop='headline')
            if headline: headline = headline.text
            authors = soup.find('div', itemprop='author')
            if authors:
                authors2 = authors.find('span', itemprop='name')
                if authors2:
                    authors3 = authors.find_all('a')
                    if authors3: authors = [a.text for a in authors3]
                    else: authors = authors.text
            text = soup.find('article', role='article')
            if text:
                textp = text.find_all('p')
                if textp: text = ' '.join([p.text for p in textp])

            if abstract: abstract = unidecode(abstract)
            if description: description = unidecode(description)
            if datePublished: datePublished = str(datePublished)
            if dateModified: dateModified = str(dateModified)
            if headline: headline = unidecode(headline)
            if text: text = unidecode(text)

            data = {
                'meta': {
                    'link': site,
                    'abstract': abstract,
                    'description': description,
                    'keywords': keywords,
                    'news_keywords': news_keywords,
                    'datePublished': datePublished,
                    'dateModified': dateModified,
                    'query_info': query_info
                },
                'article': {
                    'headline': headline,
                    'authors': authors,
                    'text': text
                },
                'id': str(uuid.uuid4())
            }
            site_data.append(data)
        except Exception as e:
            print(e)
            print(site)
            continue
    if debug:
        debug_date = [s.replace('/','-') for s in sites_i['date_range']]
        print('Date Range: {}-{}. Sites scraped: {}'.format(debug_date[0], debug_date[1], len(site_data)))
        save_file = open(paper_folder_data + 'data_{}-{}.json'.format(debug_date[0], debug_date[1]), 'w')
        json.dump(site_data, save_file, indent=2)
        save_file.close()
    return site_data

if __name__ == "__main__":
    if os.path.isdir('./data'): shutil.rmtree('./data')
    os.mkdir('./data')
    load_file = open(paper_folder + '_sites.json')
    sites_i = json.load(load_file)
    scrapped = []
    for s in sites_i:
        scrapped.extend(scrape(s))
    print('Total Sites scrapped: {}'.format(len(scrapped)))
    save_file = open('theDailyStar_data2.json', 'w')
    json.dump(scrapped, save_file, indent=2)
    save_file.close()
    load_file.close()



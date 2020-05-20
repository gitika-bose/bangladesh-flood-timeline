import requests
from datetime import datetime
from bs4 import BeautifulSoup
import json
from unidecode import unidecode

paper_folder = 'theDailyStar/'
paper_folder_data = 'theDailyStar/data/'

def parse_date(date_obj):
    if not date_obj: return None
    sp = date_obj.split('T')
    year, month, day = sp[0].split('-')
    return datetime(int(year), int(month), int(day))

def get_content(soup_obj):
    if not soup_obj: return None
    return soup_obj.get('content')

def scrape(sites, debug=10):
    site_data, debug_data = [], []
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

            data = {
                'meta': {
                    'link': site,
                    'abstract': unidecode(abstract),
                    'description': unidecode(description),
                    'keywords': keywords,
                    'news_keywords': news_keywords,
                    'datePublished': str(datePublished),
                    'dateModified': str(dateModified)
                },
                'article': {
                    'headline': unidecode(headline),
                    'authors': authors,
                    'text': unidecode(text)
                }
            }
            site_data.append(data)
            debug_data.append(data)
        except Exception as e:
            print(e)
            print(site)
            continue
        if i and debug and i%debug==0:
            print('Sites Completed: {}'.format(i+150))
            save_file = open(paper_folder_data + 'data{}.json'.format(i+150), 'w')
            json.dump(debug_data, save_file, indent=2)
            debug_data = []
            save_file.close()
    return site_data

if __name__ == "__main__":
    load_file = open(paper_folder + 'all_sites.json')
    sites = json.load(load_file)[150:]
    scrapped = scrape(sites)

    save_file = open(paper_folder_data + 'theDailyStar_data.json', 'w')
    json.dump(scrapped, save_file, indent=2)
    save_file.close()
    load_file.close()



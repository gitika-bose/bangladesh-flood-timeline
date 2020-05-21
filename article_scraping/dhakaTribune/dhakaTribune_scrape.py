import requests
from datetime import datetime
from bs4 import BeautifulSoup
import json
import os
from unidecode import unidecode

paper_folder = 'dhakaTribune'
paper_folder_data = 'data/'

def parse_date(date_obj):
    if not date_obj: return None
    sp = date_obj.split('T')
    year, month, day = sp[0].split('-')
    return datetime(int(year), int(month), int(day))

def get_content(soup_obj):
    if not soup_obj: return None
    return soup_obj.get('content')

def scrape(sites_i=None, debug=True, sites=None):
    query_info = None
    if not sites:
        sites = sites_i['sites']
        query_info = {"query": sites_i['query'], "paper": sites_i['paper'], "date_range": sites_i['date_range']}
    site_data = []
    for i,site in enumerate(sites):
        try:
            page = requests.get(site)
            soup = BeautifulSoup(page.text, 'html.parser')
            # print(soup)

            description = get_content(soup.find('meta', attrs={'name': 'description'}))

            keywords = get_content(soup.find('meta', attrs={'name': 'keywords'}))
            if keywords: keywords = [s.strip() for s in keywords.split(',')]
            datePublished = get_content(soup.find('meta', property='article:published_time'))
            if datePublished: datePublished = parse_date(datePublished)
            dateModified = get_content(soup.find('meta', property='article:modified_time'))
            if dateModified: dateModified = parse_date(dateModified)

            main_div = soup.find('div', class_='report-mainhead')

            headline = main_div.find('h1')
            if headline: headline = headline.text.strip()
            authors = main_div.find('div', class_='author-bg')
            if authors: authors = authors.text.strip()
            text = main_div.find('div', class_='report-content')
            if text:
                textp = text.find_all('p')
                if textp: text = ' '.join([p.text for p in textp])
            if not text: text = main_div.text
            if type(text)!=str: text=None

            if description: description = unidecode(description)
            if datePublished: datePublished = str(datePublished)
            if dateModified: dateModified = str(dateModified)
            if headline: headline = unidecode(headline)
            if text: text = unidecode(text)

            data = {
                'meta': {
                    'link': site,
                    'description': description,
                    'keywords': keywords,
                    'datePublished': datePublished,
                    'dateModified': dateModified,
                    'query_info': query_info
                },
                'article': {
                    'headline': headline,
                    'authors': authors,
                    'text': text
                }
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
    # print(scrape(sites=['https://www.dhakatribune.com/world/south-asia/2017/09/21/midwives-come-aid-pregnant-rohingya-women-bangladesh-camps/'],
    #              debug=False))
    load_file = open(paper_folder + '_sites.json')
    sites_i = json.load(load_file)
    scrapped = []
    for s in sites_i[6:]:
        scrapped.extend(scrape(s))
    print('Total Sites scrapped: {}'.format(len(scrapped)))
    save_file = open(paper_folder + '_data.json', 'w')
    json.dump(scrapped, save_file, indent=2)
    save_file.close()
    load_file.close()

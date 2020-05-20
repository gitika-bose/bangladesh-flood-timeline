import requests
from datetime import datetime
from bs4 import BeautifulSoup
import json
import os
from unidecode import unidecode

paper_folder = 'dhakaTribune'
paper_folder_data = 'data'

def parse_date(date_obj):
    if not date_obj: return None
    sp = date_obj.split('T')
    year, month, day = sp[0].split('-')
    return datetime(int(year), int(month), int(day))

def get_content(soup_obj):
    if not soup_obj: return None
    return soup_obj.get('content')

def scrape(sites, debug=10, offset=0):
    site_data, debug_data = [], []
    for i,site in enumerate(sites):
        try:
            page = requests.get(site)
            soup = BeautifulSoup(page.text, 'html.parser')

            description = get_content(soup.find('meta', attrs={'name':'description'}))

            keywords = get_content(soup.find('meta', attrs={'name':'keywords'}))
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

            data = {
                'meta': {
                    'link': site,
                    'description': unidecode(description),
                    'keywords': keywords,
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
            print('Sites Completed: {}'.format(i+offset))
            save_file = open(os.path.join(paper_folder_data, 'data{}.json'.format(i+offset)), 'w')
            json.dump(debug_data, save_file, indent=2)
            debug_data = []
            save_file.close()
    return site_data

if __name__ == "__main__":
    load_file = open(os.path.join(paper_folder + '_sites.json'))
    sites = json.load(load_file)
    scrapped = scrape(sites)

    # sites = ['https://www.dhakatribune.com/bangladesh/government-affairs/2020/04/22/govt-hurries-boro-harvesting-with-fears-of-flash-floods',
    #          'https://www.dhakatribune.com/bangladesh/nation/2020/05/05/moulvibazar-farmers-bring-home-95-of-district-s-boro-paddy',
    #          'https://www.dhakatribune.com/opinion/op-ed/2020/05/14/what-happened-to-the-hippocratic-oath',
    #          'https://www.dhakatribune.com/bangladesh/nation/2020/04/21/farmers-happy-with-boro-crop-yield-but-worried-about-labour-shortages',
    #          'https://www.dhakatribune.com/bangladesh/nation/2020/04/25/farmers-harvest-half-ripe-paddy-as-rain-upstream-waters-inundate-croplands-in-sunamganj']
    # scrapped = scrape(sites, debug=0)

    save_file = open(os.path.join(paper_folder + '_data.json'.format(paper_folder)), 'w')
    json.dump(scrapped, save_file, indent=2)
    save_file.close()
    load_file.close()



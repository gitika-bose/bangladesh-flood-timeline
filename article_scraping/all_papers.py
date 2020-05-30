import os
from shutil import copyfile
import json
import shutil
from unidecode import unidecode
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from uuid import uuid4
import re
from urllib.parse import urlparse

# from dhakaTribune.dhakaTribune_scrape import dhakaTribuneScrape
# from theDailyStar.theDailyStar_scrape import theDailyStarScrape

# func_dict={
#     'dhakaTribune':dhakaTribuneScrape,
#     'theDailyStar': theDailyStarScrape
# }
func_dict = {'dhakaTribune':None}

def parse_merged_file_num(paper_name, merged_file_num='auto'):
    if type(merged_file_num) == str and merged_file_num == 'auto':
        files = [f.split('_')[0] for f in os.listdir(paper_name) if '_sites.json' in f]
        nums = []
        for f in files:
            r = re.findall(r'\d+', f)
            if r and len(r) > 0:
                nums.append(int(r[-1]))
            else:
                nums.append(0)
        merged_file_num = sorted(nums, reverse=True)[0] + 1
    return str(merged_file_num)

def parse_paper_name(paper_name):
    save_paper_index_file = 'paper_index.json'
    file = json.load(open(save_paper_index_file))
    file2 = {int(k):v['paper_name'] for k,v in file.items()}
    if type(paper_name)==int: return file2[paper_name]
    else: return paper_name

def get_all_paper_data():
    save_folder = 'all_paper_data'
    folders = [f for f in os.listdir('./') if os.path.isdir(f)]
    folders.remove(save_folder)
    folders.remove('__pycache__')

    for f in folders:
        file_name = f+'1_data.json'
        data_file = os.path.join(f,file_name)
        save_file = os.path.join(save_folder,file_name)
        if os.path.exists(data_file): copyfile(data_file, save_file)

def merge_paper_sites(paper_name, merged_file_num='auto', delete_rest=True):
    merged_file_num = parse_merged_file_num(paper_name, merged_file_num)
    paper_name = parse_paper_name(paper_name)
    folder = '{}/'.format(paper_name)
    sites_files = [f for f in os.listdir(folder) if 'sites' in f]
    all_data = []
    for site_file in sites_files:
        data = json.load(open(folder+site_file))
        if not all_data: all_data = data
        else:
            for d in data:
                check=True
                for i,d2 in enumerate(all_data):
                    if d['query']==d2['query'] and \
                    (d['date_range'][0]==d2['date_range'][0] and d['date_range'][1]==d2['date_range'][1]) and \
                    d['paper']==d2['paper']:
                        all_data[i]['sites'] = list(set(all_data[i]['sites']+d['sites']))
                        check=False
                        break
                if check:
                    all_data.append(d)
    total_site_count = sum([len(d['sites']) for d in all_data])
    print('Total Sites:',total_site_count)
    save_file = folder+paper_name+merged_file_num+'_sites.json'
    json.dump(all_data, open(save_file,'w'),indent=2)
    if delete_rest:
        if paper_name+merged_file_num+'_sites.json' in sites_files:
            sites_files.remove(paper_name+merged_file_num+'_sites.json')
        for s in sites_files: os.remove(folder+s)

def merge_data(paper_name, merged_file_num='auto', delete_rest=False):
    merged_file_num = parse_merged_file_num(paper_name, merged_file_num)
    paper_name = parse_paper_name(paper_name)
    folder = '{}/'.format(paper_name)
    data_files = [f for f in os.listdir(folder) if '_data' in f]
    all_data, all_sites = [],set()
    for data_file in data_files:
        data = json.load(open(folder + data_file))
        if not all_data:
            all_data = data
            all_sites = set([d['meta']['link'] for d in data])
        else:
            for d in data:
                if d['meta']['link'] not in all_sites:
                    all_data.append(d)
                    all_sites.add(d['meta']['link'])
    print('Total Sites:', len(all_data))
    save_file = folder + paper_name + merged_file_num + '_data.json'
    json.dump(all_data, open(save_file, 'w'), indent=2)
    if delete_rest:
        if paper_name + merged_file_num + '_data.json' in data_files:
            data_files.remove(paper_name + merged_file_num + '_data.json')
        for s in data_files: os.remove(folder + s)

def count_sites(paper_name, site_file_num='1'):
    site_file_num = parse_merged_file_num(paper_name, site_file_num)
    paper_name = parse_paper_name(paper_name)
    site_file = '{}/{}{}_sites.json'.format(paper_name, paper_name, site_file_num)
    all_data = json.load(open(site_file))
    total_site_count = sum([len(d['sites']) for d in all_data])
    return total_site_count

def count_sites_all_paper(bangla=False, english=False, site_file_num='1'):
    save_paper_index_file = 'paper_index.json'
    file = json.load(open(save_paper_index_file))
    papers = [f['paper_name'] for f in file.values()]
    s = []
    for paper in papers:
        if not bangla:
            if '-bangla' not in paper:
                s.append(count_sites(paper, site_file_num))
        elif not english:
            if '-bangla' in paper:
                s.append(count_sites(paper, site_file_num))
        else: s.append(count_sites(paper, site_file_num))
    return sum(s)


def get_paper_site(paper_name):
    paper_name = parse_paper_name(paper_name)
    site_file = os.path.join(paper_name, paper_name + '1_sites.json')
    if os.path.exists(site_file):
        site_data = json.load(open(site_file))
        for s in site_data:
            if s['sites'] and len(s['sites'])>0:
                return urlparse(s['sites'][0]).hostname
    return None


def get_date_range(paper_name):
    paper_name = parse_paper_name(paper_name)
    site_file = os.path.join(paper_name, paper_name + '1_sites.json')
    if os.path.exists(site_file):
        site_data = json.load(open(site_file))
        dmin, dmax = float('inf'), 0
        for s in site_data:
            year = int(s['date_range'][0].split('/')[-1])
            dmin = min(year, dmin)
            dmax = max(year, dmax)
        return dmin, dmax
    return None, None


def generate_paper_index():
    save_paper_index_file = 'paper_index.json'
    remove_folders = ['__pycache__', 'all_paper_data']
    papers = [f for f in os.listdir('./') if os.path.isdir(f)]
    bangla_papers = [f for f in papers if '-bangla' in f]
    remove_folders += bangla_papers
    for remove_paper in remove_folders:
        if remove_paper in papers: papers.remove(remove_paper)
    papers = sorted(papers) + sorted(bangla_papers)
    d = {}
    for i, name in enumerate(papers):
        dmin, dmax = get_date_range(name)
        d[i+1] = {
            'paper_name': name,
            'site': get_paper_site(name),
            'no_sites': count_sites(name),
            'date_range': '{}-{}'.format(dmin, dmax)
        }
    json.dump(d, open(save_paper_index_file, 'w'), indent=2)

def parse_date(date_obj):
    if not date_obj: return None
    sp = date_obj.split('T')
    year, month, day = sp[0].split('-')
    return datetime(int(year), int(month), int(day))

def get_content(soup_obj):
    if not soup_obj: return None
    return soup_obj.get('content')

def get_meta(soup):
    description = get_content(soup.find('meta', attrs={'name': 'description'}))

    abstract = get_content(soup.find('meta', attrs={'name': 'abstract'}))
    keywords = get_content(soup.find('meta', attrs={'name': 'keywords'}))
    if keywords: keywords = [s.strip() for s in keywords.split(',')]
    news_keywords = get_content(soup.find('meta', attrs={'name': 'news_keywords'}))

    datePublished = get_content(soup.find('meta', property='article:published_time'))
    if datePublished: datePublished = parse_date(datePublished)
    dateModified = get_content(soup.find('meta', property='article:modified_time'))
    if dateModified: dateModified = parse_date(dateModified)

    if abstract: abstract = unidecode(abstract)
    if description: description = unidecode(description)
    if datePublished: datePublished = str(datePublished)
    if dateModified: dateModified = str(dateModified)

    return {
        'abstract': abstract,
        'news_keywords':news_keywords,
        'description': description,
        'keywords': keywords,
        'datePublished': datePublished,
        'dateModified': dateModified,
    }

def get_soup(site):
    page = requests.get(site)
    soup = BeautifulSoup(page.text, 'html.parser')
    return soup

def scrape_inner(paper_name, sites_i=None, debug=True, sites=None, main_data_sites=None):
    paper_func = func_dict[paper_name]
    data_folder = os.path.join(paper_name,'data')
    query_info = None
    if not sites:
        sites = sites_i['sites']
        if main_data_sites: sites = list(set(sites)-main_data_sites)
        query_info = {"query": sites_i['query'], "paper": sites_i['paper'], "date_range": sites_i['date_range']}

    site_data = []
    for i, site in enumerate(sites):
        try:
            soup = get_soup(site)
            meta = get_meta(soup)
            meta['site'], meta['query_info'] = site, query_info
            article = paper_func(soup, meta)
            data = {
                'meta': meta,
                'article': article,
                'id': str(uuid4())
            }
            site_data.append(data)
        except Exception as e:
            print(e)
            print(site)
            continue
    if debug:
        debug_date = [s.replace('/','-') for s in sites_i['date_range']]
        print('Date Range: {}-{}. Sites scraped: {}'.format(debug_date[0], debug_date[1], len(site_data)))
        save_file = open(os.path.join(data_folder, 'data_{}-{}.json'.format(debug_date[0], debug_date[1])), 'w')
        json.dump(site_data, save_file, indent=2)
        save_file.close()
    return site_data

def scrape_main(paper_name, data_file_num='auto', site=None, debug=True, site_file_num=1):
    if paper_name not in func_dict: raise Exception('Please add a function for paper',paper_name)
    paper_name = parse_paper_name(paper_name)
    data_file_num = parse_merged_file_num(paper_name, data_file_num)
    data_folder_path = os.path.join(paper_name,'data')
    sites_file_path = os.path.join(paper_name, paper_name + str(site_file_num) + '_sites.json')
    date_file_path = os.path.join(paper_name, paper_name + data_file_num + '_data.json')
    main_data_file_path = os.path.join(paper_name, paper_name + '_data.json')
    main_data_sites = None
    if os.path.exists(main_data_file_path):
        main_data_file = json.load(open(main_data_file_path))
        main_data_sites = set([i['meta']['link'] for i in main_data_file])

    if os.path.isdir(data_folder_path): shutil.rmtree(data_folder_path)
    os.mkdir(data_folder_path)

    site_file = open(sites_file_path)
    sites_i = json.load(site_file)
    scrapped = []
    for s in sites_i[:2]:
        scrapped.extend(scrape_inner(paper_name, s, debug, site, main_data_sites))
    print('Total Sites scrapped: {}'.format(len(scrapped)))
    save_file = open(date_file_path, 'w')
    json.dump(scrapped, save_file, indent=2)
    save_file.close()
    site_file.close()

# scrape_main('dhakaTribune')

# print('Bangla Sites:',count_sites_all_paper(bangla=True)
#       , 'English Sites:', count_sites_all_paper(english=True))
# get_all_paper_data()
# merge_data('dhakaTribune',0,True)
generate_paper_index()


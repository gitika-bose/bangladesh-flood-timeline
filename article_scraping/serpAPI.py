import json
import os
import re
from serpapi.google_search_results import GoogleSearchResults
from dotenv import load_dotenv
load_dotenv()

def make_params(query="bangladesh floods", site="www.thedailystar.net", date_start='1/1/2020',
                date_end='1/1/2021', num_results=100, paper='theDailyStar'):
    query_r = {
        'query': query,
        'paper': paper,
        'date_range': [date_start, date_end]
    }
    params = {
        "engine": "google",
        "q": "{} site:{}".format(query, site),
        "google_domain": "google.com",
        "gl": "bd",
        "hl": "en",
        "tbm": "nws",
        'filter':'0',
        "num": num_results,
        "tbs": "cdr:1,cd_min:{},cd_max:{}".format(date_start, date_end),
        "api_key": os.getenv('SERPAPI_KEY')
    }
    return query_r, params

def make_dates(year_start=2020, year_end=2021, month_increment=0):
    y = year_start
    dates = []
    while y!=year_end:
        if month_increment:
            m = 1
            while m<=12:
                end_month = m+month_increment if m+month_increment<=12 else 12
                end_date = 1 if m+month_increment<=12 else 31
                date = ['{}/1/{}'.format(m, y), '{}/{}/{}'.format(end_month, end_date, y)]
                if m == 12: date = ['12/1/{}'.format(y), '12/31/{}'.format(y)]
                m+=month_increment
                dates.append(date)
        else:
            date = ['1/1/{}'.format(y), '12/31/{}'.format(y)]
            dates.append(date)
        y+=1
    return dates

def query_serp(query, site, dates, num_results, paper_name):
    all_sites = []
    total_sites_count = 0

    for d in dates:
        try:
            query_r, params = make_params(query=query, site=site, date_start=d[0], date_end=d[1],
                                          num_results=num_results, paper=paper_name)
            client = GoogleSearchResults(params)
            results = client.get_dict()
            news_results = results['news_results']

            count = 0
            sites_date = []
            while (news_results and len(news_results)>0) or ('error' not in results):
                sites = [news['link'] for news in news_results]
                sites_date.extend(sites)
                count+=len(sites)

                params['start'] = count
                client = GoogleSearchResults(params)
                results = client.get_dict()
                news_results = results['news_results']

            print('Date Range: {}-{}\tTotal Sites: {}'.format(d[0],d[1],len(sites_date)))

            query_r['sites'] = sites_date
            all_sites.append(query_r)
            total_sites_count += len(sites_date)
        except Exception as e:
            print(e)
            print(d)
            continue
    print('Total Sites: {}'.format(total_sites_count))
    return all_sites

def generate_site_file_num(paper_name, file_num='auto', ):
    if type(file_num)==str and file_num=='auto':
        files = [f.split('_')[0] for f in os.listdir(paper_name) if '_sites.json' in f]
        nums = [0]
        for f in files:
            r = re.findall(r'\d+', f)
            if r and len(r)>0: nums.append(int(r[-1]))
            else: nums.append(0)
        file_num = sorted(nums, reverse=True)[0]+1
    return str(file_num)

def SERP(year_start, year_end, query, site, paper_name, num_results=100, file_num='auto'):
    dates = make_dates(year_start=year_start, year_end=year_end)
    if not os.path.isdir(paper_name): os.mkdir(paper_name)
    file_num = generate_site_file_num(paper_name, file_num)
    print('Paper: {}\tQuery: {}'.format(paper_name, query))
    all_sites = query_serp(query=query, site=site, num_results=num_results, paper_name=paper_name, dates=dates)
    add_to_file = 'w'
    save_file_path = os.path.join(paper_name, '{}{}_sites.json'.format(paper_name, file_num))
    if add_to_file == 'a':
        if not os.path.exists(save_file_path): add_to_file = 'w'
    save_file = open(save_file_path, add_to_file)
    json.dump(all_sites, save_file, indent=2)
    save_file.close()


query_terms, isBangla = ['floods', 'flooding', 'flooded', 'cyclone', 'inundation', 'inundations', 'innundated'], False
queries = ['bangladesh {}'.format(term) for term in query_terms] + \
          ['bangladesh "{}"'.format(term) for term in query_terms] + ['bangladesh "flood"']
num_results = 100

save_paper_index_file = 'paper_index.json'
file = json.load(open(save_paper_index_file))
for k,paper_entity in file.items():
    if int(k)<=10: continue
    paper_name, site, date_range = paper_entity['paper_name'], paper_entity['site'], paper_entity['date_range']
    year_start = int(date_range.split('-')[0])
    year_end = int(date_range.split('-')[1])
    isBangla = True if '-bangla' in paper_name else False
    for query in queries:
        SERP(year_start, year_end, query, site, paper_name, num_results)

# year_start = 2019
# year_end = 2020
#
#
# query, isBangla = "bangladesh \"floods\"", False
# # query, isBangla = "বাংলাদেশ বন্যা", True
# site = "www.thedailystar.net"
# paper_name = 'thedailystar'
# num_results = 100
# if isBangla: paper_name += '-bangla'
#
# SERP(year_start, year_end, query, site, paper_name, num_results)
import json
import os
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

year_start = 2007
year_end = 2021
dates = make_dates(year_start=year_start, year_end=year_end)

query = "bangladesh floods"
site = "www.dhakatribune.com"
num_results=100
paper_name='dhakaTribune'

all_sites = []
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
    except Exception as e:
        print(e)
        print(d)
        continue

print('Total Sites: {}'.format(len(all_sites)))
add_to_file = 'w'
if add_to_file=='a':
    if not os.path.exists(os.path.join(paper_name,'{}_sites.json'.format(paper_name))):
        add_to_file = 'w'
save_file = open(os.path.join(paper_name,'{}_sites.json'.format(paper_name)),add_to_file)
json.dump(all_sites,save_file,indent=2)
save_file.close()
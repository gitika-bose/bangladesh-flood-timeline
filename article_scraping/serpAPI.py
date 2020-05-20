import json
import os
from serpapi.google_search_results import GoogleSearchResults
from dotenv import load_dotenv
load_dotenv()

params = {
    "engine": "google",
    "q": "bangladesh floods site:www.dhakatribune.com",
    "google_domain": "google.com",
    "gl": "bd",
    "hl": "en",
    "tbm": "nws",
    "num": "100",
    "api_key": os.getenv('SERPAPI_KEY')
}

client = GoogleSearchResults(params)
results = client.get_dict()


news_results = results['news_results']
count = 0
all_sites = []
while (news_results and len(news_results)>0) or ('error' not in results):
    sites = [news['link'] for news in news_results]
    all_sites.extend(sites)
    count+=len(sites)
    print('Results:{}'.format(count))

    params['start'] = count
    client = GoogleSearchResults(params)
    results = client.get_dict()
    news_results = results['news_results']

print('Total Sites: {}'.format(len(all_sites)))

paper_name = 'dhakaTribune'
save_file = open(os.path.join(paper_name,'{}_sites.json'.format(paper_name)),'w')
json.dump(all_sites,save_file,indent=2)
save_file.close()

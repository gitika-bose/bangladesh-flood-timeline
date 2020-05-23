import os
from shutil import copyfile
import json

def parse_merged_file_num(merged_file_num=0):
    if not merged_file_num: merged_file_num=''
    else: merged_file_num = str(merged_file_num)
    return merged_file_num

def parse_paper_name(paper_name):
    save_paper_index_file = 'paper_index.json'
    file = json.load(open(save_paper_index_file))
    file = {int(k):v for k,v in file.items()}
    if type(paper_name)==int: return file[paper_name]
    else: return paper_name

def get_all_paper_data():
    save_folder = 'all_paper_data'
    folders = [f for f in os.listdir('./') if os.path.isdir(f)]
    folders.remove(save_folder)
    folders.remove('__pycache__')

    for f in folders:
        file_name = f+'_data.json'
        data_file = os.path.join(f,file_name)
        save_file = os.path.join(save_folder,file_name)
        if os.path.exists(data_file): copyfile(data_file, save_file)

def merge_paper_sites(paper_name, merged_file_num=0, delete_rest=True):
    merged_file_num = parse_merged_file_num(merged_file_num)
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

def merge_data(paper_name, merged_file_num=0, delete_rest=False):
    merged_file_num = parse_merged_file_num(merged_file_num)
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

def count_sites(paper_name, site_file_num=0):
    site_file_num = parse_merged_file_num(site_file_num)
    paper_name = parse_paper_name(paper_name)
    site_file = '{}/{}{}_sites.json'.format(paper_name, paper_name, site_file_num)
    all_data = json.load(open(site_file))
    total_site_count = sum([len(d['sites']) for d in all_data])
    return total_site_count

def count_sites_all_paper(bangla=True, english=True):
    save_paper_index_file = 'paper_index.json'
    file = json.load(open(save_paper_index_file))
    papers = file.values()
    s = []
    for paper in papers:
        if not bangla:
            if '-bangla' not in paper:
                s.append(count_sites(paper))
        elif not english:
            if '-bangla' in paper:
                s.append(count_sites(paper))
        else: s.append(count_sites(paper))
    return sum(s)

def generate_paper_index():
    save_paper_index_file = 'paper_index.json'
    remove_folders = ['__pycache__', 'all_paper_data']
    papers = [f for f in os.listdir('./') if os.path.isdir(f)]
    for remove_paper in remove_folders:
        if remove_paper in papers: papers.remove(remove_paper)
    papers.sort()
    d = {i+1:k for i,k in enumerate(papers)}
    json.dump(d, open(save_paper_index_file, 'w'), indent=2)

# print(count_sites_all_paper(english=False))
get_all_paper_data()

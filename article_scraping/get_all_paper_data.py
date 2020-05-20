import os
from shutil import copyfile

save_folder = 'all_paper_data'
folders = [f for f in os.listdir('./') if os.path.isdir(f)]
folders.remove(save_folder)
folders.remove('__pycache__')

for f in folders:
    file_name = f+'_data.json'
    data_file = os.path.join(f,file_name)
    save_file = os.path.join(save_folder,file_name)
    copyfile(data_file, save_file)

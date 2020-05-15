Installation
============

* Install Python 3.8
* pip install -r requirements.txt
* cp config_sample.yaml config.yaml
* Edit config.yaml


Examples
========

* Load documents from file '1981.json' into folder 'pool/articles':

    ./tagtog_load_json.py config.yaml 1981.json pool/articles >1981.output

* Delete all documents from folder 'pool/foo' with the file name that matches '1984_*.txt':

    ./tagtog_delete.py config.py 'folder:pool/articles AND filename:1981_*.txt'

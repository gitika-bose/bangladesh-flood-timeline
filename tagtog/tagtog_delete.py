#!/usr/bin/env python
from typing import Dict, Any
import sys
import requests
import pyaconf


def tagtog_delete(config: Dict[str, Any], search_criterion: str) -> int:
    auth = requests.auth.HTTPBasicAuth(
        username=config["user"], password=config["password"]
    )
    params = dict(
        project=config["project"], owner=config["owner"], search=search_criterion
    )
    resp = requests.delete(config["apiurl"], params=params, auth=auth)
    return int(resp.text)


if len(sys.argv) < 3:
    print(
        f"""\
Usage:

    {sys.argv[0]} CONFIG SEARCH_CRITERION

Example:

    {sys.argv[0]} config.yaml 'folder:pool/articles AND filename:1984_*.txt'

""",
        file=sys.stderr,
    )
    sys.exit(1)

config_name = sys.argv[1]
search_criterion = sys.argv[2]

config = pyaconf.load(config_name, format="yaml")

result = tagtog_delete(config, search_criterion)

print(f"Deleted {result} documents.")

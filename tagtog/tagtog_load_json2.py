#!/usr/bin/env python
from typing import Dict, Any
import sys
import json
import os
import zipfile
import hashlib
import pathlib
import requests
import pyaconf


def sha1(s: str) -> str:
    m = hashlib.sha1()
    m.update(s.encode("utf-8"))
    return m.hexdigest()


def post(
    config: Dict[str, Any], folder: str, file_name: str, text: str
) -> Dict[str, Any]:
    auth = requests.auth.HTTPBasicAuth(
        username=config["user"], password=config["password"]
    )
    params = dict(
        owner=config["owner"],
        project=config["project"],
        folder=folder,
        format="verbatim",
        output="null",
        filename=file_name,
        distributeToMembers=config["distribute_to_members"],
    )
    payload = dict(text=text)
    resp = requests.post(config["apiurl"], params=params, auth=auth, data=payload)
    print(resp.text, file=sys.stderr)
    res = json.loads(resp.text)
    if res["ok"] != 1 or res["errors"] != 0:
        raise Exception(f"post error ", res['errors'])
    return res


# if len(sys.argv) < 4:
#     print(
#         f"""\
# Usage:
#
#     {sys.argv[0]} CONFIG INPUT FOLDER >OUTPUT
#
# Example:
#
#     {sys.argv[0]} config.yaml 1981.json pool/articles >1981.output
#
# """,
#         file=sys.stderr,
#     )
#     sys.exit(1)

# config_name = sys.argv[1]

files = [os.path.join('../all_articles',f) for f in os.listdir('../all_articles') if '.json' in f]
for fileP in files:
    file_path = pathlib.Path(fileP)
    folder = 'pool/articles'

    config = pyaconf.load("config.yaml")

    count_documents = 0
    count_characters = 0
    count_paragraphs = 0

    results = {}
    all_text = {}

    name = file_path.stem
    ext = file_path.suffix
    with open(file_path, "r") as f:
        data = json.load(f)
        docs = len(data)
        # print(f"{file_path=!r}, {docs=}", file=sys.stderr)
        for index, doc in enumerate(data):
            code = doc["id"]
            text = doc["article"]["text"]
            if text is None:
                text = ""
            code2 = sha1(text)
            if text != "" and code2 not in results:
                count_documents += 1
                characters = len(text)
                count_characters += characters
                paragraphs = text.count("\n") + (
                    0 if characters > 0 and text[-1] == "\n" else 1
                )
                count_paragraphs += paragraphs
                all_text["{}_{}".format(name, code)] = text
                # res = post(config, folder, f"{name}_{code}", text)
                # results[code2] = dict(
                #     res=res,
                #     file_path=str(file_path),
                #     index=index,
                #     code=code,
                #     characters=characters,
                #     paragraphs=paragraphs,
                # )
                # print(
                #     f"    LOADED:  {index=}, {code2=}, {code=}, {characters=}, {paragraphs=}",
                #     file=sys.stderr,
                # )
            else:
                # print(f"    SKIPPED: {index=}, {code2=}, {code=}", file=sys.stderr)
                print()

    print(
        f"Loaded {count_documents}, {count_paragraphs}, {count_characters}",
        file=sys.stderr,
    )

    json.dump(
        dict(
            count_documents=count_documents,
            count_paragraphs=count_paragraphs,
            count_characters=count_characters,
            results=results,
        ),
        sys.stdout,
    )

    json.dump(all_text, open('all_output/text-{}.json'.format(name), 'w'), indent=2)

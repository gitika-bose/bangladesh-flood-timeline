#!/usr/bin/env python
import os
import sys
from pathlib import Path
import json

# import yaml
import csv
from typing import Tuple, Dict, List, Any, Optional
import datetime
import re
from html.parser import HTMLParser

root_path = Path("/Users/ikh/Downloads/bangladesh_floods_20200820")
ann_path = Path(root_path, "ann.json")
article_path = Path(root_path, "plain.html")
master_ann_path = Path(ann_path, "master")
members_ann_path = Path(ann_path, "members")
ann_legend_path = Path(root_path, "annotations-legend.json")

with open(ann_legend_path, "r") as f:
    legend = json.load(f)

regex_abra_cadabra = r"^[@#]*$"


class ContentParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.is_content = 0
        self.content = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        if tag == "div":
            self.is_content += 1

    def handle_endtag(self, tag: str):
        if tag == "div":
            self.is_content -= 1

    def handle_data(self, content: str):
        if self.is_content != 0:
            self.content += [
                y
                for y in (x.strip() for x in content.strip().split("\n"))
                if re.match(regex_abra_cadabra, y) is None
            ]


drop_list = [
    "Date",
    "Division1",
    "Division2",
    "Division3",
    "District1",
    "District2",
    "District3",
    "District4",
    "District5",
]


def empty_entry(legend: Dict[str, str]) -> Dict[str, Any]:
    rs: Dict[str, Any] = {}
    for k in legend.keys():
        if k[0] == "m":
            rs[legend[k]] = None
    rs["__anncomplete"] = False
    return rs


def drop_fields(d: Dict[str, Any], drop_list: List[str]) -> Dict[str, Any]:
    return {k: v for k, v in d.items() if k not in drop_list}


date_regex_articles = re.compile(r"^(\d\d\d\d-\d\d-\d\d).*$")
date_regex_dhaka = re.compile(r"^Date Published:\s*(\d\d\d\d-\d\d-\d\d).*$")


def parse_article(
    article_id: str, folder: str, content: str
) -> Tuple[str, Optional[datetime.date]]:
    parser = ContentParser()
    parser.feed(content)
    dt = None

    for i, s in enumerate(parser.content):
        m = re.match(
            date_regex_articles if folder == "/pool/articles" else date_regex_dhaka, s
        )
        if m is not None:
            dt = datetime.datetime.strptime(m.group(1), "%Y-%m-%d").date()
            parser.content.pop(i)
            break

    return (parser.content, dt)


def traverse_annotations(output: Dict[str, Any], root_path: Path, path: Path) -> None:
    for x in os.scandir(path):
        if x.is_dir():
            traverse_annotations(output, root_path, Path(x.path))
        else:
            folder = str(Path(x.path).parent)[len(str(root_path)) :]
            article_id = Path(x.path).with_suffix("").stem
            with open(x.path, "r") as f:
                annotations = json.load(f)
            anncomplete = annotations["anncomplete"]
            metas = annotations["metas"]
            output[article_id] = dict(
                __article_id=article_id,
                __folder=folder,
                __anncomplete=anncomplete,
                **{legend[k]: v["value"] for k, v in metas.items()}
            )


def traverse_articles(output: Dict[str, Any], root_path: Path, path: Path) -> None:
    for x in os.scandir(path):
        if x.is_dir():
            traverse_articles(output, root_path, Path(x.path))
        else:
            folder = str(Path(x.path).parent)[len(str(root_path)) :]
            article_id = Path(x.path).with_suffix("").stem
            with open(x.path, "r") as f:
                article = f.read()
            content, dt = parse_article(article_id, folder, article)
            lines = len(content)
            length = len(content)
            output[article_id] = dict(
                __article_id=article_id,
                __folder=folder,
                __content="\n".join(content),
                __date=dt,
            )


articles: Dict[str, Any] = {}
traverse_articles(articles, article_path, article_path)

annotations: Dict[str, Any] = {}
traverse_annotations(annotations, master_ann_path, master_ann_path)


if len(articles) != 0:
    keys = list(
        set(empty_entry(legend).keys())
        | set(annotations[next(iter(annotations))].keys())
        | set(articles[next(iter(articles))].keys())
    )

    keys = [
        "__article_id",
        "__date",
        "__anncomplete",
        "__folder",
        "is_flood",
        "is_Bangladesh",
        "type",
        "flood_related",
        "flood-climatechange",
        "newspaper",
        "anomaly_issue",
        "__content",
    ]

    w = csv.DictWriter(sys.stdout, keys, lineterminator="\n")
    w.writeheader()
    for k in sorted(articles.keys()):
        r = empty_entry(legend)
        if k in annotations:
            r.update(annotations[k])
        r.update(articles[k])
        r = drop_fields(r, drop_list)
        w.writerow(r)

# yaml.dump(rs, sys.stdout, default_flow_style=False, width=120, allow_unicode=True)
# json.dump(rs, sys.stdout, sort_keys=True, indent=3)

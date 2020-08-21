#!/usr/bin/env python
import os
import sys
from pathlib import Path
import json

# import yaml
import csv
from typing import Dict, Any

root_path = Path("/Users/ikh/Downloads/bangladesh_floods_20200820")
ann_path = Path(root_path, "ann.json")
article_path = Path(root_path, "plain.html")
master_ann_path = Path(ann_path, "master")
members_ann_path = Path(ann_path, "members")
ann_legend_path = Path(root_path, "annotations-legend.json")

with open(ann_legend_path, "r") as f:
    legend = json.load(f)


def empty_entry(legend: Dict[str, str]) -> Dict[str, Any]:
    rs: Dict[str, Any] = {}
    for k in legend.keys():
        if k[0] == "m":
            rs[legend[k]] = None
    rs["__anncomplete"] = False
    return rs


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
            length = len(article)
            output[article_id] = dict(
                __article_id=article_id,
                __folder=folder,
                __content=article,
                __length=length,
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
    w = csv.DictWriter(sys.stdout, keys)
    w.writeheader()
    for k in sorted(articles.keys()):
        r = empty_entry(legend)
        if k in annotations:
            r.update(annotations[k])
        r.update(articles[k])
        w.writerow(r)

# yaml.dump(rs, sys.stdout, default_flow_style=False, width=120, allow_unicode=True)
# json.dump(rs, sys.stdout, sort_keys=True, indent=3)

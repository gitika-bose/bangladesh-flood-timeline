#!/usr/bin/env python
import os
import sys
from pathlib import Path
import json
#import yaml
import csv
from typing import Dict, Any

root_path = Path("/Users/ikh/Downloads/bangladesh_floods_20200820")
ann_path = Path(root_path, "ann.json")
master_ann_path = Path(ann_path, "master")
members_ann_path = Path(ann_path, "members")
ann_legend_path = Path(root_path, "annotations-legend.json")

with open(ann_legend_path, "r") as f:
    legend = json.load(f)


def traverse(output: Dict[str, Any], root_path: Path, path: Path) -> None:
    for x in os.scandir(path):
        if x.is_dir():
            traverse(output, root_path, Path(x.path))
        else:
            folder = str(Path(x.path).parent)[len(str(root_path)) :]
            article_id = Path(x.path).with_suffix("").stem
            with open(x.path, "r") as f:
                annotations = json.load(f)
            anncomplete = annotations["anncomplete"]
            metas = annotations["metas"]
            metas_converted = {legend[k]: v["value"] for k, v in metas.items()}
            for k in legend.keys():
                if k[0] == "m" and k not in metas:
                    metas_converted[legend[k]] = None
            output.append(
                dict(
                    __article_id=article_id,
                    __folder=folder,
                    __anncomplete=anncomplete,
                    **metas_converted
                )
            )


rs = []
traverse(rs, master_ann_path, master_ann_path)

if len(rs) != 0:
    w = csv.DictWriter(sys.stdout, rs[0].keys())
    w.writeheader()
    for r in rs:
        w.writerow(r)

# yaml.dump(rs, sys.stdout, default_flow_style=False, width=120, allow_unicode=True)
# json.dump(rs, sys.stdout, sort_keys=True, indent=3)

#!/usr/bin/env python
# -*- coding:utf-8 -*-
from typing import List, Dict
import os
import json
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

OUTPUT_JSONL = 'output.jsonl'
GMAP_KEY_FNAME = 'google_maps_api_key.txt'


def read_gmap_api_key() -> str:
    if not os.path.exists(GMAP_KEY_FNAME):
        raise SystemError(
            'get Google Maps API Key (Maps JavaScript API)'
            f' and write it to "{GMAP_KEY_FNAME}"'
        )
    with open(GMAP_KEY_FNAME, 'rt') as rf:
        api_key = rf.read().strip()
    return api_key


def load_stocks() -> List[Dict[str, str]]:
    if not os.path.exists(OUTPUT_JSONL):
        raise SystemError('do scrape.py')
    stocks = list()
    with open(OUTPUT_JSONL, 'rt') as rf:
        row = rf.readline()
        while row:
            stock = json.loads(row.strip())
            stocks.append(stock)
            row = rf.readline()
    return stocks


app = FastAPI()
templates = Jinja2Templates(directory='templates')


@app.get('/')
async def load_map(request: Request) -> None:
    api_key = read_gmap_api_key()
    stocks = load_stocks()
    return templates.TemplateResponse(
        'index.html',
        context={
            'request': request,
            'api_key': api_key,
            'stocks': stocks,
        }
    )

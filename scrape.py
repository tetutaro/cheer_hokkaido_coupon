#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''ほっかいどう認証店応援キャンペーンのサイトから
PDFをダウンロードして、そこから郵便局毎のクーポン在庫を抽出する
'''
from typing import Dict
import os
import time
import json
import requests
import camelot
from googlemaps.client import Client
from googlemaps.exceptions import ApiError
from retry import retry

PDF_URL = 'https://hkd2022ninsho.jp/pdf/zaiko.pdf'
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


def download_pdf() -> None:
    '''在庫状況が記載されたPDFをダウンロードする
    '''
    fname = os.path.basename(PDF_URL)
    if os.path.exists(fname):
        return
    content = requests.get(PDF_URL).content
    with open(fname, 'wb') as wf:
        wf.write(content)
    return


@retry(exceptions=ApiError, tries=3, delay=1)
def get_latlng(gmaps: Client, address: str) -> Dict[str, float]:
    '''住所から緯度経度を取得する関数

    Args:
        gmaps (Client): Google Maps API のクライアント
        address (str): 住所（「北海道」が省略されたもの）

    Returns:
        dict: "lat"に緯度、"lng"に経度が記載された辞書
    '''
    res = gmaps.geocode('北海道' + address)
    return res[0]['geometry']['location']


def extract_pdf(api_key: str) -> None:
    '''PDFを読み取って郵便局一覧および在庫を取得する
    そして住所から Google Maps API を使って緯度経度を取得する
    データは OUTPUT_JSONL ファイルに出力する

    Args:
        api_key (str): Google Maps API Key の文字列
    '''
    # PDF がダウンロード済みかチェック
    fname = os.path.basename(PDF_URL)
    if not os.path.exists(fname):
        raise SystemError('download PDF!')
    # Google Maps インスタンスの作成
    gmaps = Client(key=api_key)
    # PDFの全てのページを読み、pandas.DataFrameの形で得る
    tables = camelot.read_pdf(fname, pages='1-end')
    stocks = list()
    for table in tables:
        for ix, row in table.df.iterrows():
            if ix == 0:
                # skip the header of the table
                continue
            # 情報を貯めるリスト
            info = list()
            # ほとんどの行がきちんと整形して出力されるが
            # 一部の行で空の列が存在したり、
            # １列目・２列目、５列目・６列目が一緒くたになる
            # そこで自前でパースする
            for dat in row:
                dat = dat.strip()
                if len(dat) == 0:
                    continue
                info.extend([
                    x.strip().replace(',', '') for x in dat.split(' ')
                ])
            if len(dat) < 5:
                continue
            stock = {
                'post_office': info[2],
                'address': info[3],
                'stock': int(info[4]),
            }
            # Google Maps API を使って緯度経度を取得する
            try:
                time.sleep(0.5)
                latlng = get_latlng(gmaps=gmaps, address=stock['address'])
                stock['lat'] = latlng['lat']
                stock['lng'] = latlng['lng']
            except Exception:
                print(
                    f'cant get laglng: {stock["post_office"]}'
                )
                continue
            stocks.append(stock)
    with open(OUTPUT_JSONL, 'wt') as wf:
        for stock in stocks:
            wf.write(json.dumps(stock, ensure_ascii=False) + '\n')
    return


if __name__ == '__main__':
    api_key = read_gmap_api_key()
    download_pdf()
    extract_pdf(api_key=api_key)

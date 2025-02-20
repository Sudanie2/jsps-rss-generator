#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Flaskを利用して https://www.jsps.go.jp/include/news/inform_ja.json のJSONデータから
RSSフィードを生成するアプリケーションです。

各RSSアイテムでは、タイトル部分がハイパーリンクになっており、URLが正しく設定されます。

使い方:
1. 必要なライブラリをインストール:
   pip install flask requests feedgen pytz
2. このファイルを app.py として保存し、実行:
   python app.py
3. ブラウザで http://127.0.0.1:5000/json2rss にアクセスしてRSSフィードが表示されるか確認
4. サーバーにデプロイ後、公開URLをFeedlyに登録してください。
"""

from flask import Flask, Response
import requests
from feedgen.feed import FeedGenerator
from datetime import datetime
import pytz

app = Flask(__name__)

@app.route('/')
def index():
    return (
        '<h1>JSPS inform_ja RSS Feed Generator</h1>'
        '<p>/json2rss にアクセスするとRSSフィードが生成されます。</p>'
    )

@app.route('/json2rss')
def json2rss():
    json_url = 'https://www.jsps.go.jp/include/news/inform_ja.json'
    try:
        resp = requests.get(json_url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return Response(f'JSONの取得に失敗: {e}', status=500)

    fg = FeedGenerator()
    fg.title('JSPS inform_ja Feed')
    fg.link(href='https://www.jsps.go.jp/', rel='alternate')
    fg.description('Generated from inform_ja.json by Flask app')

    for entry in data:
        fe = fg.add_entry()
        fe.id(str(entry.get('client_news_id', '')))
        fe.title(entry.get('title', 'No Title'))

        # URLの設定（cms_fileフィールドがリストの場合、最初の要素を利用）
        raw_link = entry.get('cms_file', '')
        if isinstance(raw_link, list):
            raw_link = raw_link[0] if raw_link else ''
        if raw_link and raw_link.startswith('/'):
            link = 'https://www.jsps.go.jp' + raw_link
        else:
            link = entry.get('message', '')
        fe.link(href=link)

        # 公開日時（timeフィールド）の設定
        raw_time = entry.get('time')
        if raw_time:
            try:
                dt = datetime.strptime(raw_time, "%Y/%m/%d %H:%M:%S")
                jst = pytz.timezone('Asia/Tokyo')
                dt_jst = jst.localize(dt)
                dt_utc = dt_jst.astimezone(pytz.utc)
                fe.pubDate(dt_utc)
            except ValueError:
                pass

        # 説明文の生成：tagsが辞書の場合は"name"キーを使い、なければ文字列化する
        tags = entry.get('tags', [])
        if isinstance(tags, list):
            desc = ' / '.join(
                tag.get('name', str(tag)) if isinstance(tag, dict) else str(tag)
                for tag in tags
            )
        else:
            desc = ''
        message = entry.get('message', '')
        if message:
            desc += f"\nMessage: {message}"
        fe.description(desc.strip())

    rss_str = fg.rss_str(pretty=True)
    response = Response(rss_str, mimetype='application/rss+xml; charset=UTF-8')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)

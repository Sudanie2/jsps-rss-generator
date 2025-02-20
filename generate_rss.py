#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from feedgen.feed import FeedGenerator
from datetime import datetime

def generate_rss():
    # JSONデータを取得するURL（日本学術振興会の新着情報）
    json_url = 'https://www.jsps.go.jp/include/news/inform_ja.json'
    
    try:
        # JSONを取得
        response = requests.get(json_url)
        response.raise_for_status()  # HTTPエラーがあれば例外を発生させる
    except Exception as e:
        print(f"JSONの取得に失敗しました: {e}")
        return

    try:
        data = response.json()  # JSONデータをパース（リスト形式を想定）
    except Exception as e:
        print(f"JSONのパースに失敗しました: {e}")
        return

    # RSSフィードの基本設定
    fg = FeedGenerator()
    fg.id(json_url)
    fg.title('日本学術振興会 - 新着情報')
    fg.link(href='https://www.jsps.go.jp/', rel='alternate')
    fg.description('日本学術振興会の新着情報を自動生成したRSSフィードです。')

    # JSONの各項目からRSSエントリを追加
    for item in data:
        fe = fg.add_entry()
        
        # タイトル情報の取得。キーが存在しなければ "No Title" とする
        title = item.get("title", "No Title")
        fe.title(title)
        
        # リンク情報の取得。キーが "news_url" と仮定し、相対パスの場合は公式サイトのURLを付加
        news_url = item.get("news_url", "")
        if news_url and not news_url.startswith("http"):
            news_url = "https://www.jsps.go.jp" + news_url
        fe.link(href=news_url, rel='alternate')
        
        # 公開日の設定。キー "news_date" のフォーマットが "YYYY/MM/DD HH:MM:SS" を想定
        news_date = item.get("news_date", "")
        if news_date:
            try:
                pub_date = datetime.strptime(news_date, "%Y/%m/%d %H:%M:%S")
                fe.pubDate(pub_date)
            except Exception as e:
                print(f"日付の変換に失敗しました（{news_date}）：{e}")

    # RSSフィードを XML 形式に変換（整形済み）
    try:
        rss_str = fg.rss_str(pretty=True)
        # rss.xml として書き出し（バイナリモードで書き込む）
        with open("rss.xml", "wb") as f:
            f.write(rss_str)
        print("rss.xml を生成しました。")
    except Exception as e:
        print(f"RSSの生成または書き出しに失敗しました: {e}")

if __name__ == '__main__':
    generate_rss()

# encoding :utf-8
import sys, json, __twitter_key
from requests_oauthlib import OAuth1Session
from datetime import datetime

CK = __twitter_key.CONSUMER_KEY
CS = __twitter_key.CONSUMER_SECRET
AT = __twitter_key.ACCESS_TOKEN
ATS = __twitter_key.ACCESS_TOKEN_SECRET
twitter = OAuth1Session(CK, CS, AT, ATS)

# TwitterAPIエンドポイントの取得
url = "https://api.twitter.com/1.1/statuses/update.json"

def tweet(returncode): # returncode: subprocess.runの終了コード
	if returncode == 0:
		enc_result = 'エンコード完了むぅ'
	else: # エラー終了した場合は0にならない(はず)
		enc_result = 'エンコード失敗むぅ'

	# ツイート本文(定型文 + エンコード結果 + 投稿日時)
	tweet = "('ω'`)自動ツイートむぅ\n" + \
			"('ω'`)" + datetime.now().strftime('%Y.%m.%d %H:%M:%S') + '頃に' + enc_result
	
	params = {"status" : tweet}
	req = twitter.post(url, params = params)

	# ツイートする
	if req.status_code == 200:
		print('Tweet Succeed.')
	else:
		print("ERROR: %d" % req.status_code)
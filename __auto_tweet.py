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

def tweet(returncode, err_str): # returncode: subprocess.runの終了コード
	if returncode == 0:
		enc_result = 'process succeeded.'
	else: # エラー終了した場合は0にならない(はず)
		enc_result = 'process failed.'
	
	# 現在日時の取得
	now_time =  datetime.now().strftime('%Y.%m.%d %H:%M:%S')

	# ツイート本文(定型文 + エンコード結果 + 投稿日時 + エラーログの内容)
	tweet = now_time + ' ' + enc_result + '\n' + \
			err_str + ' ' + ' #auto_tweet'
	
	params = {"status" : tweet}
	req = twitter.post(url, params = params)

	# ツイートする
	if req.status_code == 200:
		print('Tweet Succeed.')
	else:
		print("ERROR: %d" % req.status_code)
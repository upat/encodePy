# encoding :utf-8
import sys, json
from twitter_key import *
from requests_oauthlib import OAuth1Session
from datetime import datetime

CK = CONSUMER_KEY
CS = CONSUMER_SECRET
AT = ACCESS_TOKEN
ATS = ACCESS_TOKEN_SECRET
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
			err_str + ' ' + '#auto_tweet'
	
	params = {"status" : tweet}
	req = twitter.post(url, params = params)

	# ツイートする
	if req.status_code == 200:
		print('Tweet Succeed.')
	else:
		print("ERROR: %d" % req.status_code)

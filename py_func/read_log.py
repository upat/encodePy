# encoding: utf-8
from pathlib import Path
import shutil

# ログファイルにエラーの記載があれば出力ファイルと共にコピー
def read_log( input, output, filename ):
	logfile_src = Path( input, filename + '.txt' )   # ログファイル(コピー元)
	logfile_copy = Path( output, filename + '.txt' ) # ログファイル(コピー先)

	if logfile_src.exists() and Path( logfile_copy.parent ).exists():
		try:
			readfile = open( logfile_src, 'r' )
			# 1行ごとにリスト化
			readfile_data = readfile.readlines()
			# 1行目の文字の有無を確認
			if readfile_data[0] != '\n': # 改行のみか
				shutil.copy2( logfile_src, logfile_copy )
		except:
			return

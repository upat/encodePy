# encoding :utf-8
import sys, subprocess, shutil
from pathlib import Path
from py_func.def_const import DefineConst
from py_func.read_log import *

dc = DefineConst( sys.argv[1] )

# 最終出力先のディレクトリを作成
if not Path( dc.outfile_path ).exists():
	Path( dc.outfile_path ).mkdir( parents=True )
# エラーログの内容確認
read_log( dc.srcfile_path, dc.outfile_path, dc.srcfile_filename )

# エンコード(内部で映像サイズ判定) ※subprocess.runだと処理中の標準出力が見えないためPopenで実装
enc_res = subprocess.Popen( dc.enc_cmd(), encoding='utf8', stdout=subprocess.PIPE )
# subprocess.Popenの処理終了まで待ち
enc_res.wait()
# エラー終了した場合は強制終了
if enc_res.returncode != 0:
	print( 'Failed Encode Process.' )
	sys.exit()

# ローカルサーバー稼働中 and 出力済みファイル有
if Path( dc.media_server ).exists() and Path( dc.outfile_fullpath ).exists(): # 
	# # ローカルサーバーへコピー
	if not Path( dc.copyfile_path ).exists():
		Path( dc.copyfile_path ).mkdir( parents=True )
	shutil.copy2( dc.outfile_fullpath, dc.copyfile_fullpath )

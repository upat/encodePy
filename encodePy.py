# encoding :utf-8
import sys, subprocess, shutil
from pathlib import Path
from py_func.def_var import *
from py_func.read_log import *

if not Path( sys.argv[1] ).exists() or sys.argv[1] == '': # if not ～ orはnot直後の条件にのみ有効
	sys.exit() # 入力ファイルが存在しない場合強制終了
elif not Path( sav_dir[0:3] ).exists():
	sys.exit() # 出力先ストレージが存在しない場合強制終了

src_fpath = sys.argv[1]                # フルパス取得
src_path  = Path( src_fpath ).parent   # フルパスからファイル名無しパスを取得
src_fname = Path( src_fpath ).stem     # フルパスから拡張子無しファイル名を取得
out_dname = Path( src_path ).name      # ファイル名無しパスの末尾のフォルダ名を取得
mp4_path  = Path( sav_dir, out_dname ) # 出力パス(ファイル名なし)を作成
copy_path = Path( media_server, out_dname ) # バックアップコピー先のパス(ファイル名なし)を作成
# 最終出力先のディレクトリを作成
if not Path( mp4_path ).exists():
	Path( mp4_path ).mkdir( parents=True )
# エラーログの内容確認
read_log( src_path, mp4_path, src_fname )
mp4_path = Path( mp4_path, src_fname + '.mp4' ) # 出力パスを作成

# rffフラグの判定(文字列検索)
rff_check = False # rffフラグの判定に使う変数
for i in rff_str:
	if src_fname.find( i ) != -1:
		rff_check = True # rffフラグが見つかった場合

# エンコード(内部で映像サイズ判定) ※subprocess.runだと処理中の標準出力が見えないためPopenで実装
enc_res = subprocess.Popen( video_enc_cmd( src_fpath, str( mp4_path ), rff_check ), encoding='utf8', stdout=subprocess.PIPE )
# subprocess.Popenの処理終了まで待ち
enc_res.wait()
# エラー終了した場合は強制終了
if enc_res.returncode != 0:
	sys.exit()

# ローカルサーバーへコピー
if Path( media_server ).exists(): # ローカルサーバー稼働の確認 
	if Path( mp4_path ).exists(): # 出力済みファイルの確認
		# ファイルコピー
		if not Path( copy_path ).exists():
			Path( copy_path ).mkdir()
		copy_path = Path( copy_path, src_fname + '.mp4' ) # バックアップコピー先のパスを作成
		shutil.copy2( mp4_path, copy_path )

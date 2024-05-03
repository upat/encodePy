# encoding :utf-8
import sys, subprocess, shutil
from pathlib import Path
from py_func.def_const import DefineConst
from py_func.read_log import *

# 強制終了時にコールする
def force_exit():
	subprocess.run( 'pause', shell=True ) # pauseコマンド
	sys.exit()

dc = DefineConst( sys.argv[1] )
if not dc.init_result:
	force_exit()

# 最終出力先のディレクトリを作成
if not Path( dc.outfile_path ).exists():
	Path( dc.outfile_path ).mkdir( parents=True )
# エラーログの内容確認
read_log( dc.srcfile_path, dc.outfile_path, dc.srcfile_filename )

# ffprobeで入力ファイル情報取得
probe_res = subprocess.run( dc.ffprobe_cmd(), encoding='utf8', stdout=subprocess.PIPE, stderr=subprocess.PIPE )
if probe_res.returncode != 0:
	# エラー終了した場合終了
	print( 'Failed ffprobe Process.' )
	force_exit()

# ffprobe出力解析
dc.read_ffprobe_log( probe_res.stdout, probe_res.stderr )

# オーディオ読み込みエラーフラグ確認
if dc.audio_err_flag:
	# エラー有り時
	# shell=Trueでゴリ押しする苦肉の策(Popenを2つ立ち上げてパイプすると非同期のせいかffmpegがNVEncを置き去りにして勝手に終了するため)
	enc_res = subprocess.Popen( ' '.join( dc.enc_cmd( True ) ), encoding='utf8', stdout=subprocess.PIPE, shell=True )
	enc_res.wait() # 待ち
	# ffmpegでパイプ入力した場合は空ファイル作成
	Path( dc.outfile_path, dc.srcfile_filename + '_aac_error.txt' ).touch()
else:
	# エラー無し時
	# エンコード(内部で映像サイズ判定) ※subprocess.runだと処理中の標準出力が見えないためPopenで実装
	enc_res = subprocess.Popen( dc.enc_cmd(), encoding='utf8', stdout=subprocess.PIPE )
	# subprocess.Popenの処理終了まで待ち
	enc_res.wait()

if enc_res.returncode != 0:
	# エラー終了した場合終了
	print( 'Failed Encode Process.' )
	force_exit()

if dc.rff_flag:
	# rff有りの場合は空ファイル作成
	Path( dc.outfile_path, dc.srcfile_filename + '_find_rff.txt' ).touch()

# ローカルサーバー稼働中 and 出力済みファイル有
if Path( dc.media_server ).exists() and Path( dc.outfile_fullpath ).exists(): # 
	# # ローカルサーバーへコピー
	if not Path( dc.copyfile_path ).exists():
		Path( dc.copyfile_path ).mkdir( parents=True )
	print( 'Start Backup Copy...' )
	shutil.copy2( dc.outfile_fullpath, dc.copyfile_fullpath ) # 上書きコピー
	print( 'Complete Backup Copy.' )

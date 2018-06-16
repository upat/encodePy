# encoding :utf-8
import sys, subprocess, os.path, re, os, glob, shutil
sys.path.append(os.environ.get('py_func'))
from auto_tweet import tweet
from read_log import read_log
from get_video_res import get_video_res
from def_var import *

# subproc_resultが0以外の時、ツイートを行った後強制終了
subproc_result = 0
def subproc_rc(errcode):
	global subproc_result # 最後に使うのでグローバル化
	subproc_result += errcode
	if subproc_result != 0:
		tweet(subproc_result, 'any errors')
		sys.exit()

# フォルダ内の任意の拡張子を持ったファイル名の検索用(.から始まるファイル対応版)
def find_ext(file_dir, ext):
    name_list = os.listdir(file_dir) # パスは含まれていない
    # 取得したディレクトリ内のファイル名一覧に目的の拡張子があるか検索
    for fn in name_list:
        if fn.find(ext) > -1:
            return fn
    subproc_rc(1) # 無かった場合はエラー終了させる

# 作業フォルダの選択
if os.path.isfile(sys.argv[1]) == False:
	sys.exit() # 入力ファイルが存在しない場合強制終了
elif os.path.isdir(hdd_dir[0:2]) == False:
	sys.exit() # 代替作業兼保存ストレージが存在しない場合強制終了
elif os.path.isdir(ram_dir[0:2]) == True:
	required_size = 6442450944 # 必要なディスク容量 (6GB)
	max_file_size = 4831838208 # 最大ファイルサイズ (4.5GB)

	# 作業フォルダの空き容量を取得
	diskfree = shutil.disk_usage(ram_dir[0:2]).free

	# (RAMDiskの空き容量 < 必要な容量) or (最大ファイルサイズ < ファイルの実サイズ)
	if (diskfree < required_size) or \
		(max_file_size < os.path.getsize(sys.argv[1])):
		temp_dir = hdd_dir # hdd_dirを設定する
	else:
		temp_dir = ram_dir # ram_dirを設定する
else:
	temp_dir = hdd_dir # 代替ストレージが存在し、RAMDiskが無い場合

# 作業フォルダが存在しない場合、作成
if os.path.isdir(temp_dir) == False:
	os.makedirs(temp_dir)

# ファイル名に存在するウムラウト文字をアルファベット、半角記号を全角記号に変換
src_fpath = sys.argv[1].translate(str.maketrans('äöü', 'aou'))
src_path = os.path.dirname(src_fpath) # 入力ファイル名を除いたパス
src_fname = re.sub('.ts', "", os.path.basename(src_fpath)) # 拡張子を除いた入力ファイル名
out_dname = os.path.basename(src_path) #入力ファイルの最下層のフォルダ名
if sys.argv[1] != src_fpath:
	os.rename(sys.argv[1], src_path + '\\' + src_fname + '.ts') # リネーム
# 最終出力先のディレクトリを作成
if os.path.isdir(sav_dir + '\\' + out_dname) == False:
	os.makedirs(sav_dir + '\\' + out_dname)

# rffフラグの判定(文字列検索)
rff_str = rff_str.split(',') # 1文字ずつリスト化されているのでカンマで区切って単語リスト化
rff_check = 0 # rffフラグの判定に使う変数
for i in rff_str:
	if src_fname.find(i) != -1:
		rff_check = 1 # rffフラグが見つかった場合1

# VapourSynthスクリプトの中身の準備
vpy_script = '''import vapoursynth as vs
core = vs.get_core()
name = r''' + '"' + temp_dir + '\\' + src_fname + '.demuxed.m2v' + '"' + '''
name = name.encode('cp932')
c = core.lsmas.LWLibavSource(name, fpsden=0, repeat=1, dominance=1)
c = core.std.SetFrameProp(clip=c, prop="_FieldBased", intval=2)
c.set_output()'''
# VapourSynthスクリプトをutf-8で生成
f = open(temp_dir + '\\' + src_fname + '.vpy', 'w', encoding='utf-8')
f.write(vpy_script)
f.flush()
f.close()

# 動画を映像と音声に分離
subproc_rc(subprocess.run(video_demux_cmd(src_path, src_fname, temp_dir), shell=True).returncode)

# 音声のdelay除去処理のためのエンコード
subproc_rc(subprocess.run(aac_delay_fix_enc_cmd(temp_dir, find_ext(temp_dir, '.aac')), shell=True).returncode)
# delay除去された音声のデコード
subproc_rc(subprocess.run(aac_delay_fix_dec_cmd(temp_dir, find_ext(temp_dir, '.wav'), src_fname), shell=True).returncode)
# l-smashで音声mux
subproc_rc(subprocess.run(audio_ls_muxer_cmd(temp_dir, src_fname), shell=True).returncode)
# aacエンコード
subproc_rc(subprocess.run(aac_enc_cmd(temp_dir, src_fname), shell=True).returncode)

# エンコードに使用する動画の解像度を取得
video_res = get_video_res(temp_dir + '\\' + src_fname + '.demuxed.m2v')
# 映像エンコード(rff_checkの値により分岐)
if rff_check == 1:
	subproc_rc(subprocess.run(video_enc_rff_cmd(temp_dir, src_fname, video_res), shell=True).returncode)
else:
	subproc_rc(subprocess.run(video_enc_cmd(temp_dir, src_fname, video_res), shell=True).returncode)

# l-smashで映像mux
subproc_rc(subprocess.run(video_ls_muxer_cmd(temp_dir, src_fname), shell=True).returncode)
# l-smashで音声・映像の結合、保存先へ出力
subproc_rc(subprocess.run(ls_remuxer_cmd(temp_dir, src_fname, sav_dir, out_dname), shell=True).returncode)

# エンコード結果をツイート
tweet(subproc_result, read_log(re.sub('.ts', "", sys.argv[1]) + '.txt'))

# 作業フォルダ内とlogファイルの削除
for rm_file in os.listdir(temp_dir):
	os.remove(temp_dir + '\\' + rm_file)
os.remove(src_path + '\\' + src_fname + '.log')


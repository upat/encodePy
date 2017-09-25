# encoding :utf-8
import sys, subprocess, os.path, re, os, glob
import __auto_tweet
import __read_log

# subproc_resultが0以外の時、ツイートを行った後強制終了
subproc_result = 0
def subproc_rc(errcode):
	global subproc_result # 最後に使うのでグローバル化
	subproc_result += errcode
	if subproc_result != 0:
		__autotweet.tweet(subproc_result)
		sys.exit()

# 作業フォルダの選択
if os.path.isfile(sys.argv[1]) == False:
	sys.exit() # 入力ファイルが存在しない場合強制終了
elif os.path.isdir(os.environ.get('hdd_dir')[0:2]) == False:
	sys.exit() # 代替作業兼保存ストレージが存在しない場合強制終了
elif os.path.isdir(os.environ.get('ram_dir')[0:2]) == True:
	required_size = 6442450944 # 必要なディスク容量 (6GB)
	max_file_size = 4831838208 # 最大ファイルサイズ (4.5GB)
	# fsutil volume diskfreeでRAMDiskの空き容量を取得、バイト文字列にして返す
	diskfree = subprocess.check_output('fsutil volume diskfree ' + \
				os.environ.get('ram_dir')[0:2], shell=True)
	# バイト文字列をデコードした後、行ごとにリストへ格納
	diskfree = diskfree.decode('cp932').split('\n')
	# 最終行から特定の文字列を除く(win8.1の場合の出力)
	diskfree = re.sub('利用可能な空きバイト総数     : ',"", diskfree[2])
	diskfree = int(diskfree)
	# (RAMDiskの空き容量 < 必要な容量) or (最大ファイルサイズ < ファイルの実サイズ)
	if (diskfree < required_size) or \
		(max_file_size < os.path.getsize(sys.argv[1])):
		temp_dir = os.environ.get('hdd_dir') # hdd_dirを設定する
	else:
		temp_dir = os.environ.get('ram_dir') # ram_dirを設定する
else:
	temp_dir = os.environ.get('hdd_dir') # 代替ストレージが存在し、RAMDiskが無い場合

# 作業フォルダが存在しない場合、作成
if os.path.isdir(temp_dir) == False:
	os.makedirs(temp_dir)

# ファイル名に存在するウムラウト文字をアルファベット、半角記号を全角記号に変換
src_fpath = sys.argv[1].translate(str.maketrans('äöü&%^', 'aou＆％＾'))
src_path = os.path.dirname(src_fpath) # 入力ファイル名を除いたパス
src_fname = re.sub('.ts', "", os.path.basename(src_fpath)) # 拡張子を除いた入力ファイル名
out_dname = os.path.basename(src_path) #入力ファイルの最下層のフォルダ名
if sys.argv[1] != src_fpath:
	os.rename(sys.argv[1], src_path + '\\' + src_fname + '.ts') # リネーム
# 最終出力先のディレクトリを作成
sav_dir = os.environ.get('sav_dir')
if os.path.isdir(sav_dir + '\\' + out_dname) == False:
	os.makedirs(sav_dir + '\\' + out_dname)

# rffフラグの判定(文字列検索)
rff_str = os.environ.get('rff_str') # rffフラグの判定に使う変数その1
rff_str = rff_str.split(',') # 1文字ずつリスト化されているのでカンマで区切って単語リスト化
rff_check = 0 # rffフラグの判定に使う変数その2
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

# DGIndexによる分離処理
dgindex_cmd = '%DGIndex% -i' + ' "' + src_path + '\\' + src_fname + '.ts' + '" ' + \
		'-od' + ' "' + temp_dir + '\\' + src_fname + '" ' + '%DGIndex_option%'
subproc_rc(subprocess.run(dgindex_cmd, shell=True).returncode)

# delay除去処理
aac_file = glob.glob(temp_dir + '\\*.aac')
fawcl_cmd1 = '%fawcl%' + ' "' + aac_file[0] + '"'
subproc_rc(subprocess.run(fawcl_cmd1, shell=True).returncode)
# aacへ再変換
wav_file = glob.glob(temp_dir + '\\*.wav')
fawcl_cmd2 = '%fawcl%' + ' "' + wav_file[0] + '" "' + \
		temp_dir + '\\' + src_fname + '_nodelay.aac' +'"'
subproc_rc(subprocess.run(fawcl_cmd2, shell=True).returncode)

# l-smashで音声mux
lmuxera_cmd = '%muxer% -i' + ' "' + temp_dir + '\\' + src_fname + '_nodelay.aac' + '" ' + \
		'-o' + ' "' + temp_dir + '\\' + src_fname + '.aac' + '"'
subproc_rc(subprocess.run(lmuxera_cmd, shell=True).returncode)

# qaacエンコード
qaac_cmd = '%qaac% %qaac_option%' + ' "' + temp_dir + '\\' + src_fname + '.aac' + '" ' + \
		'-o' + ' "' + temp_dir + '\\' + src_fname + '.m4a' + '"'
subproc_rc(subprocess.run(qaac_cmd, shell=True).returncode)

# qsvenccエンコード(rff_check == 1の時はvapoursynthで読み込み)
qsv_cmd = '%QSVEncC% --avqsv %QSVEncC_option% -i' + \
		' "' + temp_dir + '\\' + src_fname + '.demuxed.m2v' + '" ' + \
		'-o' + ' "' +temp_dir + '\\' + src_fname + '.264' + '"'
qsv_rff = '%QSVEncC% --vpy-mt %QSVEncC_option% -i' + \
		' "' + temp_dir + '\\' + src_fname + '.vpy' + '" ' + \
		'-o' + ' "' +temp_dir + '\\' + src_fname + '.264' + '"'
if rff_check == 1:
	subproc_rc(subprocess.run(qsv_rff, shell=True).returncode)
else:
	subproc_rc(subprocess.run(qsv_cmd, shell=True).returncode)

# l-smashで映像mux
lmuxerv_cmd = '%muxer% -i' + ' "' + temp_dir + '\\' + src_fname + '.264' + '" ' + \
		'-o' + ' "' + temp_dir + '\\' + src_fname + '.mp4' + '"'
subproc_rc(subprocess.run(lmuxerv_cmd, shell=True).returncode)

# l-smashで音声・映像の結合、保存先へ出力
lremuxer_cmd = '%remuxer% -i' + ' "' + temp_dir + '\\' + src_fname + '.mp4' + '" ' + \
		'-i' + ' "' + temp_dir + '\\' + src_fname + '.m4a' + '" ' + \
		'-o' + ' "' + sav_dir + '\\' + out_dname + '\\' + src_fname + '.mp4' + '"'
subproc_rc(subprocess.run(lremuxer_cmd, shell=True).returncode)

# エンコード結果をツイート
__auto_tweet.tweet(subproc_result, __read_log.read_log(re.sub('.ts', "", sys.argv[1]) + '.txt'))

# 作業フォルダ内とlogファイルの削除
for rm_file in glob.glob(temp_dir + '\\*'):
	os.remove(rm_file)
os.remove(src_path + '\\' + src_fname + '.log')

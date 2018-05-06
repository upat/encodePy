# encoding: utf-8
# 各種実行ファイルのパス
aac_enc =
aac_delay_fix =
video_enc =
video_enc_nv =
video_demux =
ls_muxer =
ls_remuxer =

# 処理に使用するパス・文字列
ram_dir =
hdd_dir =
sav_dir =
rff_str =

# 各種実行ファイルのオプション生成関数
# sp  : source path(no file name)
# sfn : source file name
# td  : temporary directory
# fn  : file name(no extension)
# sd  : save directory
# odn : output directory name
def video_demux_cmd(sp, sfn, td):
	cmd_str = video_demux + ' -i' + ' ' + '"' + sp + '\\' + sfn + '.ts' + '"' + ' ' + \
			'-od' + ' ' + '"' + td + '\\' + sfn + '"' + ' ' + \
			'-ia 4 -fo 0 -yr 1 -om 2 -hide -exit'
	return cmd_str

def aac_delay_fix_enc_cmd(td, fn):
	cmd_str = aac_delay_fix + ' ' + '"' + td + '\\' + fn + '"'
	return cmd_str

def aac_delay_fix_dec_cmd(td, fn, sfn):
	cmd_str = aac_delay_fix + ' ' + '"' + td + '\\' + fn + '"' + ' ' + \
			'"' + td + '\\' + sfn + '_nodelay.aac' + '"'
	return cmd_str

def audio_ls_muxer_cmd(td, sfn):
	cmd_str = ls_muxer + ' ' + '-i' + ' ' + '"' + td + '\\' + sfn + '_nodelay.aac' + '"' + ' ' + \
			'-o' + ' ' + '"' + td + '\\' + sfn + '.aac' + '"'
	return cmd_str

def aac_enc_cmd(td, sfn):
	cmd_str = aac_enc + ' ' + '-V 45 -q 2' + ' ' + '"' + td + '\\' + sfn + '.aac' + '"' + ' ' + \
			'-o' + ' ' + '"' + td + '\\' + sfn + '.m4a' + '"'
	return cmd_str

def video_enc_cmd(td, sfn, size):
	cmd_str = video_enc + ' ' + \
			'--avqsv --tff --vpp-deinterlace normal --codec h264 --cqp 22:25:27 --quality best --gop-len 300' + ' ' + size + ' ' + \
			'-i' + ' ' + '"' + td + '\\' + sfn + '.demuxed.m2v' + '"' + ' ' + \
			'-o' + ' ' + '"' + td + '\\' + sfn + '.264' + '"'
	return cmd_str

def video_enc_rff_cmd(td, sfn, size):
	cmd_str = video_enc + ' ' + \
			'--vpy-mt --tff --vpp-deinterlace normal --codec h264 --cqp 22:25:27 --quality best --gop-len 300' + ' ' + size + ' ' + \
			'-i' + ' ' + '"' + td + '\\' + sfn + '.vpy' + '"' + ' ' + \
			'-o' + ' ' + '"' + td + '\\' + sfn + '.264' + '"'
	return cmd_str

def video_enc_nv_cmd(td, sfn, size):
	cmd_str = video_enc_nv + ' ' + \
			'--avcuvid --interlace tff --vpp-deinterlace normal --codec h264 --cqp 23:25:27 --preset quality --aq --aq-strength 0 --aq-temporal --mv-precision Q-pel --lookahead 16 --weightp --gop-len 300 --vpp-resize spline36' + ' ' + size + ' ' + \
			'-i' + ' ' + '"' + td + '\\' + sfn + '.demuxed.m2v' + '"' + ' ' + \
			'-o' + ' ' + '"' + td + '\\' + sfn + '.264' + '"'
	return cmd_str

def video_enc_nv_rff_cmd(td, sfn, size):
	cmd_str = video_enc_nv + ' ' + \
			'--vpy-mt --interlace tff --vpp-deinterlace normal --codec h264 --cqp 23:25:27 --preset quality --aq --aq-strength 0 --aq-temporal --mv-precision Q-pel --lookahead 16 --weightp --gop-len 300 --vpp-resize spline36' + ' ' + size + ' ' + \
			'-i' + ' ' + '"' + td + '\\' + sfn + '.vpy' + '"' + ' ' + \
			'-o' + ' ' + '"' + td + '\\' + sfn + '.264' + '"'
	return cmd_str

def video_ls_muxer_cmd(td, sfn):
	cmd_str = ls_muxer + ' ' + '-i' + ' ' + '"' + td + '\\' + sfn + '.264' + '"' + ' ' + \
			'-o' + ' ' + '"' + td + '\\' + sfn + '.mp4' + '"'
	return cmd_str

def ls_remuxer_cmd(td, sfn, sd, odn):
	cmd_str = ls_remuxer + ' ' + '-i' + ' ' + '"' + td + '\\' + sfn + '.mp4' + '"' + ' ' + \
			'-i' + ' ' + '"' + td + '\\' + sfn + '.m4a' + '"' + ' ' + \
			'-o' + ' ' + '"' + sd + '\\' + odn + '\\' + sfn + '.mp4' + '"'
	return cmd_str


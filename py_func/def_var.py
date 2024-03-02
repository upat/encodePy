# encoding: utf-8
import cv2

# NVEncエンコーダー
video_enc_nv = r''
# ファイル保存先(この後に入力ファイルの階層が続く)
sav_dir = r''
# rff処理を行う入力ファイル文字列
rff_str = [ '' ]
# バックアップコピー保存場所
media_server = r''

# エンコーダーで使用するオプション文字列リストの生成
def video_enc_cmd( input, output, flag ):
	# python-opencvで映像サイズ読み出し
	video_cap = cv2.VideoCapture( input )
	video_height = video_cap.get( cv2.CAP_PROP_FRAME_HEIGHT )
	video_width = video_cap.get( cv2.CAP_PROP_FRAME_WIDTH )
	video_height = int( video_height ) # floatになっているのでint変換
	video_width = int( video_width )   # floatになっているのでint変換
	
	# fHD(1080)以上ならHD(720)にリサイズ
	if( 1080 <= video_height ):
		size = '1280x720'
	else:
		# fHD(1080)未満ならとりあえずそのまま
		size = str( video_width ) + 'x' + str( video_height )
	
	if flag:
		# rffフラグあり
		cmd_str = [ video_enc_nv,
					'--avhw',
					'--audio-copy',
					'--interlace', 'tff',
					'--vpp-afs', 'preset=anime,rff=true',
					'--codec', 'hevc',
					'--vbrhq', '0',
					'--vbr-quality', '27',
					'--preset', 'quality',
					'--lookahead', '32',
					'--gop-len', '300',
					'--bref-mode', 'each',
					'--videoformat', 'ntsc',
					'--vpp-resize', 'spline64',
					'--output-res', size,
					'-i', input,
					'-o', output ]
	else:
		# rffフラグなし
		cmd_str = [ video_enc_nv,
					'--avhw',
					'--audio-copy',
					'--interlace', 'tff',
					'--vpp-deinterlace', 'normal',
					'--codec', 'hevc',
					'--vbrhq', '0',
					'--vbr-quality', '27',
					'--preset', 'quality',
					'--lookahead', '32',
					'--gop-len', '300',
					'--bref-mode', 'each',
					'--videoformat', 'ntsc',
					'--vpp-resize', 'spline64',
					'--output-res', size,
					'--log-framelist', 'debug_framelist.csv', # デバッグ出力(repeatに2以上の値があればrff)
					'-i', input,
					'-o', output ]

	return cmd_str

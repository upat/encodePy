# encoding: utf-8
import cv2
from pathlib import Path

# エンコードに必要な入出力ファイルパス、コマンドオプションなどの定数管理を行うクラス
class DefineConst:
	# NVEncエンコーダー
	_nvencoder = r''
	# ffmpeg
	_ffmpeg = r''
	# rff処理を行う入力ファイル文字列
	_rffstr = [ '' ]
	# ファイル保存先(この後に入力ファイルの階層が続く)
	_sav_dir = r''
	# バックアップコピー保存場所
	media_server = r''
	# init処理結果
	init_result = True

	# 初期化
	def __init__( self, input_filepath ):
		# パスが絶対パスではない(空の文字列含む)場合
		if not Path( input_filepath ).is_absolute():
			print( 'Not Absolute Path.' )
			DefineConst.init_result = False
		# 入力ファイルが存在しない場合
		elif not Path( input_filepath ).exists():
			print( 'Not Found Input File.' )
			DefineConst.init_result = False
		# 出力先ストレージが存在しない場合
		elif not Path( DefineConst._sav_dir[0:3] ).exists():
			print( 'Not Found Output Directory.' )
			DefineConst.init_result = False

		if DefineConst.init_result:
			self.srcfile_fullpath = input_filepath                       # フルパス取得
			self.srcfile_path     = Path( self.srcfile_fullpath ).parent # フルパスからファイル名無しパスを取得
			self.srcfile_filename = Path( self.srcfile_fullpath ).stem   # フルパスから拡張子無しファイル名を取得
			self.outfile_dirname  = Path( self.srcfile_path ).name       # ファイル名無しパスの末尾のフォルダ名を取得
			
			self.outfile_path  = Path( DefineConst._sav_dir, self.outfile_dirname )     # 出力パス(ファイル名なし)を作成
			self.copyfile_path = Path( DefineConst.media_server, self.outfile_dirname ) # バックアップコピー先のパス(ファイル名なし)を作成
			
			self.outfile_fullpath  = Path( self.outfile_path, self.srcfile_filename + '.mp4' )  # 出力パスを作成
			self.copyfile_fullpath = Path( self.copyfile_path, self.srcfile_filename + '.mp4' ) # バックアップコピー先のパスを作成
		
	# エンコーダーで使用するオプション文字列リストの生成
	def enc_cmd( self, _retry = False ):
		# python-opencvで映像サイズ読み出し
		_video_capture = cv2.VideoCapture( self.srcfile_fullpath )
		_video_height = _video_capture.get( cv2.CAP_PROP_FRAME_HEIGHT )
		_video_width = _video_capture.get( cv2.CAP_PROP_FRAME_WIDTH )
		_video_height = int( _video_height ) # floatになっているのでint変換
		_video_width = int( _video_width )   # floatになっているのでint変換
		
		# fHD(1080)以上ならHD(720)にリサイズ
		if( 1080 <= _video_height ):
			_video_size = '1280x720'
		else:
			# fHD(1080)未満ならとりあえずそのまま
			_video_size = str( _video_width ) + 'x' + str( _video_height )
		
		# コマンドオプション用リスト
		cmd_str = [ DefineConst._nvencoder,
					'--avhw',
					'--audio-copy',
					'--interlace', 'tff',
					'--codec', 'hevc',
					'--vbrhq', '0',
					'--vbr-quality', '27',
					'--preset', 'quality',
					'--lookahead', '32',
					'--gop-len', '300',
					'--bref-mode', 'each',
					'--videoformat', 'ntsc',
					'--vpp-resize', 'spline64',
					'--output-res', _video_size ]

		# rffフラグ判定(コマンドオプション追加)
		if self._check_rff():
			# rffフラグあり用のインターレース解除
			cmd_str += [ '--vpp-afs', 'preset=anime,rff=true' ]
		else:
			# rffフラグなし(通常)用のインターレース解除+フレームログ出力
			cmd_str += [ '--vpp-deinterlace', 'normal',
						'--log-framelist', 'debug_framelist.csv' ] # デバッグ出力(repeatに2以上の値があればrff)
		
		# エンコードをリトライする判定(入出力コマンドオプション追加+ffmpegコマンド追加)
		if _retry:
			# ffmpegからのパイプ入力+出力
			cmd_str += [ '-i', '-' ,
						'-o', '"' + str( self.outfile_fullpath ) + '"' ] # ダブルクォーテーションはshell=Trueで使うため
			# ffmpegからパイプ入力するため、NVEncのコマンドを後ろにする
			cmd_str = [ DefineConst._ffmpeg,
						'-i', '"' + str( self.srcfile_fullpath ) + '"',  # ダブルクォーテーションはshell=Trueで使うため
						'-ss', '1',                                      # 先頭の映像を1sを削る
						'-c', 'copy',
						'-f', 'mpegts',
						'-', '|' ] + cmd_str
		else:
			# 通常入力+出力
			cmd_str += [ '-i', str( self.srcfile_fullpath ),
						'-o', str( self.outfile_fullpath ) ]
		return cmd_str

	# rffフラグの判定(文字列検索)
	def _check_rff( self ):
		for i in DefineConst._rffstr:
			if self.srcfile_filename.find( i ) != -1:
				return True # rffフラグが見つかった場合
		return False # rffフラグが無かった場合

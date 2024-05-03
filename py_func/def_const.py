# encoding: utf-8
import json
from pathlib import Path

# エンコードに必要な入出力ファイルパス、コマンドオプションなどの定数管理を行うクラス
class DefineConst:
	# NVEncエンコーダー
	_nvencoder = r''
	# ffmpeg
	_ffmpeg = r''
	# ffprobe
	_ffprobe = r''
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
			
			self._video_height = 720     # 動画の高さ
			self._video_width = 1280     # 動画の横幅
			self.audio_err_flag = False  # オーディオ読み込みエラーフラグ
			self.rff_flag = False       # rff判定フラグ
		
	# エンコーダーで使用するオプション文字列リストの生成
	def enc_cmd( self, _error = False ):
		# fHD(1080)以上ならHD(720)にリサイズ
		if( 1080 <= self._video_height ):
			_video_size = '1280x720'
		else:
			# fHD(1080)未満ならとりあえずそのまま
			_video_size = str( self._video_width ) + 'x' + str( self._video_height )
		
		# コマンドオプション用リスト
		_cmd_str = [ DefineConst._nvencoder,
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

		# rff判定(コマンドオプション追加)
		if self.rff_flag:
			# rffあり用のインターレース解除
			_cmd_str += [ '--vpp-afs', 'preset=anime,rff=true' ]
		else:
			# rffなし(通常)用のインターレース解除+フレームログ出力
			_cmd_str += [ '--vpp-deinterlace', 'normal',
						'--log-framelist', 'debug_framelist.csv' ] # デバッグ出力(repeatに2以上の値があればrff)
		
		# オーディオ読み込みエラーフラグ判定(入出力コマンドオプション追加+ffmpegコマンド追加)
		if self.audio_err_flag:
			# ffmpegからのパイプ入力+出力
			_cmd_str += [ '-i', '-' ,
						'-o', '"' + str( self.outfile_fullpath ) + '"' ] # ダブルクォーテーションはshell=Trueで使うため
			# ffmpegからパイプ入力するため、NVEncのコマンドを後ろにする
			_cmd_str = [ DefineConst._ffmpeg,
						'-hide_banner',                                  # コンパイルオプション等のバナー情報を非表示
						'-i', '"' + str( self.srcfile_fullpath ) + '"',  # ダブルクォーテーションはshell=Trueで使うため
						'-ss', '1',                                      # 先頭の映像を1sを削る
						'-c', 'copy',
						'-f', 'mpegts',
						'-', '|' ] + _cmd_str
			# shell=Trueで利用するため、リストを文字列化
			_cmd_str = ' '.join( _cmd_str )
		else:
			# 通常入力+出力
			_cmd_str += [ '-i', str( self.srcfile_fullpath ),
						'-o', str( self.outfile_fullpath ) ]
		return _cmd_str
	
	# ffprobe用コマンド生成
	def ffprobe_cmd( self ):
		_cmd_str = [ DefineConst._ffprobe,
					'-i', self.srcfile_fullpath,
					'-hide_banner',           # コンパイルオプション等のバナー情報を非表示
					'-v', 'error',            # デコード時のエラーのみ出力(標準エラー出力)
					'-select_streams', 'v',   # 映像ストリームのみ選択して出力
					'-show_streams',          # ファイル情報出力(標準出力)
					'-print_format', 'json',  # show_streamsをjson形式にする
					'-show_entries', 'frame=repeat_pict' ] # rff有り時はrepeat_pictが1になる？
		return _cmd_str
	
	# ffprobe出力解析
	def read_ffprobe_log( self, _stdout, _stderr ):
		# JSON形式で出力した標準出力(テキスト)をJSON化
		_stdout_json = json.loads( _stdout )
		# コーデック名でjson内を検索し、動画サイズを取得
		for _index, _value in enumerate( _stdout_json['streams'] ):
			if 'mpeg2video' == _stdout_json[ 'streams' ][ _index ][ 'codec_name' ]:
				self._video_height = _stdout_json[ 'streams' ][ _index ][ 'height' ]
				self._video_width = _stdout_json[ 'streams' ][ _index ][ 'width' ]
				break
		
		# rff判定
		# https://github.com/FFmpeg/FFmpeg/blob/master/libavcodec/mpeg12dec.c
		for _index, _value in enumerate( _stdout_json['frames'] ):
			if 0 < _stdout_json[ 'frames' ][ _index ][ 'repeat_pict' ]: # 0ではないrepeat_pictが存在した場合
				self.rff_flag = True
				break
		
		# 標準エラー出力(テキスト)が任意の文字列を含む場合、オーディオ読み込みエラーフラグをTrue
		if -1 < _stderr.find( '[aac @ ' ):
			self.audio_err_flag = True

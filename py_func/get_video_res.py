# encoding :utf-8
import os
import vapoursynth as vs

# エンコードに使用するリサイズオプションの値を入力する動画を元に設定する
def get_video_res(file_path):
	if(os.path.isfile(file_path)):
		core = vs.get_core()
		file_name = file_path.encode('cp932')

		# L-SMASH Worksで読み込み
		clip = core.lsmas.LWLibavSource(file_name, fpsden=0, repeat=1, dominance=1)
		
		# アス比16:9の720pまたは480p、解像度維持のいずれか
		if(720 < clip.height):
			return '--output-res 1280x720'
		elif(clip.height == 480):
			return '--output-res 854x480'
		else:
			return ''
	else:
		# ファイルが存在しない時(その前にどこかで止まっているだろうけど)
		return ''

# encoding: utf-8
import sys

def read_log(err_log): # txtファイルのパス
	# txtファイルのopen
	try:
		read_file = open(err_log, 'r')
	except:
		return 'err_log open failed.' # txtファイルが存在しなかった場合
	read_temp = read_file.readline()
	
	# 1行ずつ読み込み、目的の文字列があった場合は切り出していく
	while read_temp:
		if read_temp.find('PID: ') != -1 and \
			(read_temp.find('Scramble:         0') == -1 or \
						read_temp.find('Drop:        0') == -1):
			# 初回ループでerr_hexが未定義の場合用
			if 'err_hex' in locals():
				err_hex += read_temp[5:11] + ', '
			else:
				err_hex = read_temp[5:11] + ', '
		# 次の1行を読み込み
		read_temp = read_file.readline()
	# txtファイルのclose
	read_file.close
	# 1行もマッチせず未定義だった場合の対策
	if 'err_hex' in locals():
		return err_hex[0:-2]
	else:
		return 'No Error.'
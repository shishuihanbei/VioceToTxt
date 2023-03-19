import os
import json
import shutil
from moviepy.editor import VideoFileClip,AudioFileClip
from VideoAudiotoTxt import LenovoFileToTxt
import time

def getTxt(txt_path,video_file):
	# print("正在处理：",os.path.split(video_file)[-1])
	file_name,txt = LenovoFileToTxt(video_file).getTaskTxt()
	with open(os.path.join(txt_path,file_name.rsplit(".",1)[0].strip()+'.txt'),'w',encoding="utf-8") as f:
		f.write(txt)
	# print("处理完成：",os.path.split(video_file)[-1])

def mp4tomp3(path,file):
	if not file.endswith('.mp3'):
		clip = VideoFileClip(file)
		audio = clip.audio
		fpath,fname = os.path.split(file)
		fname,ftype = os.path.splitext(fname)
		print("正在进行格式转换：",fname)
		file_mp3 = os.path.join(path,fname) + '.mp3'
		audio.write_audiofile(file_mp3,logger=None)
		return file_mp3
	else:
		print('不是视频格式')

def main():
	starttime = time.time()
	path = input("请输入文件或文件夹地址：").replace('"','')
	video_type = ["mp4","m4a","mov","avi","wmv","mpeg","rmvb"]
	audio_type = ["mp3","wav","amr","aac"]
	print("*" * 100)
	if os.path.exists(path):
		if os.path.isdir(path):
			file_path = os.path.abspath(path)
			audio_path = os.path.join(os.path.dirname(file_path),os.path.split(file_path)[1]+"--音频")
			txt_path = os.path.join(os.path.dirname(file_path),os.path.split(file_path)[1]+"--文本")
			flag = False
			count = 1
			if not os.path.exists(audio_path):
				os.mkdir(audio_path)
			if not os.path.exists(txt_path):
				os.mkdir(txt_path)
			for f in os.listdir(path):
				video_file = os.path.join(path,f)
				if f.rsplit('.',1)[-1].lower() in video_type:
					mp4tomp3(audio_path,video_file)
					flag = True
				elif f.rsplit('.',1)[-1].lower() in audio_type:
					print('-' * 50)
					print('正在处理第{}个，总共有{}个。' .format(count,len(os.listdir(path))))
					count += 1
					getTxt(txt_path,video_file)
			if flag:
				for mf in os.listdir(audio_path):
					audio_file = os.path.join(audio_path,mf)
					if mf.rsplit('.',1)[-1].lower() in audio_type:
						print('-' * 50)
						print('正在处理第{}个，总共有{}个。' .format(count,len(os.listdir(audio_path))))
						count += 1
						getTxt(txt_path,audio_file)
						time.sleep(5)
		elif os.path.isfile(path):
			base_path = os.path.dirname(path)
			if path.rsplit('.',1)[-1].lower() in video_type:
				mp3_file = os.path.join(base_path,os.path.split(path)[1].rsplit(".",1)[0] + '.mp3')
				mp4tomp3(base_path,path)
				getTxt(base_path,mp3_file)
			elif path.rsplit('.',1)[-1].lower() in audio_type:
				getTxt(base_path,path)
	else:
		print("请输入正确的文件夹或文件地址")
	endtime = time.time()
	releasetime = endtime - starttime
	m,s = divmod(releasetime,60)
	h,m = divmod(m,60)
	print("耗时：{}时{}分{}秒" .format(int(h),int(m),int(s)))


if __name__ == "__main__":
	main()

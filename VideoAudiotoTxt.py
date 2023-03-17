from moviepy.editor import VideoFileClip,AudioFileClip
import os
import requests
import json
import time

class LenovoFileToTxt():
	def __init__(self,file):
		self.videoName = os.path.split(file)[1]
		self.videoSize = os.path.getsize(file)
		self.period = int(AudioFileClip(file).duration*1000)
		self.file = file
		self.url = 'https://smart.lenovo.com.cn/audioservice'
		self.headers = {
			"Tokencui":self.getCuiToken(),
			"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.41"
		}

	def getCuiToken(self):
		headers = {
			"Content-Type":"application/json",
			"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.41"
		}
		data = {
			"lenovo_id_info": {
				"realm": "api.iot.lenovomm.com",
				"ticket": ""
			},
			"client_key": "60a3327c94df8b95f0ccb7a4",
			"device_info": {
				"device_id": "1a5ee779-bd34-4374-b7bd-bb7868a6961b",
				"mac": "",
				"vendor": "UNKNOW_TYPE",
				"hw_model": "Chrome_Text_Translation",
				"client_sw_ver": '2.0.0'
			},
			"product_id": "Chrome_Text_Translation",
		}
		cui = "https://cuiauth.lenovo.com.cn:443/auth/v1/simpletoken"
		resp = requests.post(url = cui,data = json.dumps(data),headers = headers,verify = False)
		result = resp.json()
		tokencui = result['data']['access_token']
		return tokencui

	def fileupload(self):
		"""音视频文件上传"""
		upload_url = self.url + "/voice/wav2txt"
		params = {
			"language":"cn",
			"videoName":self.videoName,
			"videoSize":self.videoSize,
			"period":self.period
		}
		files = {'file':(self.videoName,open(self.file,'rb'))}
		resp = requests.post(url = upload_url,params = params,files= files,headers = self.headers,verify =False)
		taskId = resp.json()['res']['taskId']
		return taskId

	def getTaskStatus(self,taskId):
		"""获取任务状态"""
		task_status_url = self.url + "/voice/getTaskStatus"
		params = {"taskId":taskId}
		resp = requests.get(url = task_status_url, headers = self.headers, params = params, verify =False)
		result = resp.json()
		return result

	def deleteTask(self,taskId):
		"""删除任务"""
		del_url = self.url + "/voice/deleteTask"
		params = {
			"taskId":taskId
		}
		resp = requests.get(url = del_url, headers = self.headers, params = params,verify =False)
		result = resp.json()
		status = result['status']
		# if status == "Y":
		# 	print(self.videoName + "文件删除成功！")

	def getTaskTxt(self):
		"""获取完成的文件并删除任务"""
		taskId = self.fileupload()
		flag = True
		while flag:
			result = self.getTaskStatus(taskId)
			translateTime = result['res']['translateTime']
			if translateTime == "已完成":
				flag = False
				self.deleteTask(taskId)
				txt = "\n".join([i['onebest'] for i in json.loads(result["res"]["asrTxt"])])
				return self.videoName,txt
			time.sleep(1)

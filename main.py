import tkinter as tk
from tkinter import ttk,Canvas,SUNKEN, RAISED,END
from tkinter import filedialog
import os
import json
import time
import tkinter.messagebox as messagebox
from VideoAudiotoTxt import LenovoFileToTxt,mp4tomp3
import threading
from icon import Icon
import base64

class WindowGui():
	def __init__(self):
		self.file_path = ''
		self.video_type = ["mp4","m4a","mov","avi","wmv","mpeg","rmvb"]
		self.audio_type = ["mp3","wav","amr","aac"]
		self.tree = ''
		self.singleorpath = ''

	def getfiles(self):
		files = filedialog.askdirectory()
		self.inserttable(files)
		self.file_path.set(files)

	def getfile(self):
		file=tk.filedialog.askopenfilename(filetypes=[("文件类型",self.video_type + self.audio_type)])
		self.inserttable(file)
		self.file_path.set(file)

	def delButton(self):
		x = self.tree.get_children()
		for item in x:
			self.tree.delete(item)

	def inserttable(self,path):
		if os.path.exists(path):
			if os.path.isdir(path):
				self.singleorpath = "文件夹"
				count = 1
				self.delButton()
				for f in os.listdir(path):
					filename,filetype = os.path.split(f)[1].rsplit(".",1)
					if filetype.endswith(tuple(self.video_type + self.audio_type)):
						self.tree.insert('', tk.END, values=[count,filename,filetype,'否','0次','否','否'])
						count += 1
			elif os.path.isfile(path):
				self.singleorpath = "文件"
				if path.rsplit('.',1)[-1].lower() in self.video_type + self.audio_type and path.rsplit('.',1)[-1].lower().endswith(tuple(self.video_type + self.audio_type)):
					filename,filetype = os.path.split(path)[1].rsplit(".",1)
					self.delButton()
					self.tree.insert('', tk.END, values=[1,filename,filetype,'否','0次','否','否'])
		else:
			messagebox.showinfo('提示','请输入正确的文件夹或文件地址')

	@classmethod
	def writetxt(cls,path,name,content):
		file_name = name + '--文本.txt'
		file_path = os.path.join(path,file_name)
		with open(file_path, "w", encoding="utf-8") as f:
			f.write(content)

	def getMessage(self,count,line_id,txtpath,base_file,bpath,file_name):
		FileToTxt = LenovoFileToTxt(base_file)
		taskId = FileToTxt.fileupload()
		self.tree.set(line_id,column="是否上传", value="上传成功！")
		flag = True
		n = 1
		while flag:
			time.sleep(10)
			result = FileToTxt.getTaskStatus(taskId)
			translateTime = result['res']['translateTime']
			self.tree.set(line_id,column="查询次数", value="正在查询{}次" .format(n))
			n += 1
			if translateTime == "已完成":
				flag = False
				self.tree.set(line_id,column="查询次数", value="总查询{}次" .format(n))
				FileToTxt.deleteTask(taskId)
				self.tree.set(line_id,column="已传文件", value="是")
				txt = "\n".join([i['onebest'] for i in json.loads(result["res"]["asrTxt"])])
				if count == 1:
					WindowGui.writetxt(bpath,file_name,txt)
				else:
					WindowGui.writetxt(txtpath,file_name,txt)
				self.tree.set(line_id,column="是否完成", value="是")

	def startTask(self):
		self.startButton.config(state='disable',background="green",disabledforeground="#fff",text="正在处理...",relief=SUNKEN)
		self.file_button.config(state='disable',background="#99FFCC",disabledforeground="#000",text="单个文件",relief=SUNKEN)
		self.files_button.config(state='disable',background="#993300",disabledforeground="#fff",text="文件夹",relief=SUNKEN)

		base_path = self.file_path.get()
		count = len(self.tree.get_children())
		if count == 0:
			messagebox.showinfo('提示','请输入正确的文件夹或文件地址')
		if self.singleorpath == "文件":
			bpath = os.path.split(base_path)[0]
			basepath = bpath
			txtpath = ''
			audiopath = ''
		elif self.singleorpath == "文件夹":
			basepath = base_path
			bpath,bfilename = os.path.split(base_path)
			txtpath = os.path.join(bpath,bfilename+'--文本')
			audiopath = os.path.join(bpath,bfilename+'--音频')
			if not os.path.exists(txtpath):
				os.mkdir(txtpath)
			if not os.path.exists(audiopath):
				os.mkdir(audiopath)
		for line in self.tree.get_children():
			line_id = line
			values = self.tree.item(line_id)["values"]
			file_name = values[1]
			file_type = values[2]
			file = file_name + "." + file_type
			if file_type in self.video_type:
				video_file = os.path.join(basepath,file_name+ "." + file_type)
				if count == 1:
					audio_file = mp4tomp3(bpath,video_file)
				else:
					audio_file = mp4tomp3(audiopath,video_file)
				self.getMessage(count,line_id,txtpath,audio_file,bpath,file_name)
				try:
					os.remove(audio_file)
				except Exception as e:
					continue
			elif file_type in self.audio_type:
				self.tree.set(line_id,column="是否上传", value="正在上传...")
				base_file = os.path.join(basepath,file)
				self.getMessage(count,line_id,txtpath,base_file,bpath,file_name)
		self.file_button.config(state='norma',background="#99FFCC",foreground="#000",text="单个文件",relief=RAISED)
		self.files_button.config(state='norma',background="#993300",foreground="#fff",text="文件夹",relief=RAISED)
		self.startButton.config(state='norma',text='开始转换',background="red",foreground="#fff",relief=RAISED)
		b_str = messagebox.askquestion('结果', '处理完成,是否关闭？')
		self.closegui(b_str,audiopath)
		
	def closegui(self,str,path):
		if str == "yes":
			self.window.destroy()
		else:
			messagebox.showinfo('提示','将清空已完成的文件！')
			self.delButton()
			self.file_lable.delete('0', "end")


	def threadTask(self):
		t = threading.Thread(target=self.startTask)
		t.start()

	def gui(self):
		self.window = tk.Tk()
		self.window.resizable(False,False)
		self.window.title("音视频转文字")
		with open('tem.ico','wb') as tmp:
			tmp.write(base64.b64decode(Icon().img))
		self.window.iconbitmap("tem.ico")
		os.remove('tem.ico')
		window_width = 750
		window_height = 600
		screen_width = self.window.winfo_screenwidth()
		screen_height = self.window.winfo_screenheight()
		x = (screen_width - window_width - 16) // 2
		y = (screen_height - window_height - 32) // 2
		self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
		file_l = tk.Label(text = '选择文件或文件夹:')
		file_l.place(x=30,y=25)
		self.file_path = tk.StringVar()
		self.file_lable = tk.Entry(self.window,textvariable=self.file_path,bd=2,width=50,borderwidth=0.5)
		self.file_lable.place(x=150,y=25)
		self.file_button = tk.Button(self.window,text='单个文件',width=10,background="#99FFCC",command=self.getfile)
		self.file_button.place(x=530,y=20)
		self.files_button = tk.Button(self.window,text='文件夹',width=10,background="#993300",foreground="#FFFFFF",command=self.getfiles)
		self.files_button.place(x=630,y=20)

		tabel_frame = tk.Frame(self.window,width=690,height=500,background='#ccc')
		tabel_frame.place(x=30,y=70)
		xscroll = tk.Scrollbar(tabel_frame, orient=tk.HORIZONTAL)
		yscroll = tk.Scrollbar(tabel_frame, orient=tk.VERTICAL)
		
		columns = ['序号', '文件名', '文件类型', '是否上传', '查询次数', '已传文件','是否完成']
		self.tree=ttk.Treeview(master=tabel_frame,height=20,columns=columns,show='headings')
		self.tree.heading("序号",text="序号")
		self.tree.column("序号", width=50, anchor=tk.CENTER)
		self.tree.heading("文件名",text="文件名")
		self.tree.column("文件名", width=200, minwidth=200,anchor=tk.CENTER)
		self.tree.heading("文件类型",text="文件类型")
		self.tree.column("文件类型", width=80, anchor=tk.CENTER)
		self.tree.heading("是否上传",text="是否上传")
		self.tree.column("是否上传", width=80, anchor=tk.CENTER)
		self.tree.heading("查询次数",text="查询次数")
		self.tree.column("查询次数", width=80, anchor=tk.CENTER)

		self.tree.heading("已传文件",text="已传文件删除")
		self.tree.column("已传文件", width=100, anchor=tk.CENTER)

		self.tree.heading("是否完成",text="是否完成")
		self.tree.column("是否完成", width=80, anchor=tk.CENTER)
		xscroll.config(command=self.tree.xview)
		xscroll.pack(side=tk.BOTTOM, fill=tk.X)
		yscroll.config(command=self.tree.yview)
		yscroll.pack(side=tk.RIGHT, fill=tk.Y)
		self.tree.pack(fill=tk.BOTH, expand=True)
		self.startButton = tk.Button(self.window,text='开始转换',width=20,height=2,background="red",foreground="#fff",command=self.threadTask)
		self.startButton.place(x=560,y=510)

		self.window.mainloop()

def main():
	win = WindowGui()
	win.gui()
if __name__ == "__main__":
	main()

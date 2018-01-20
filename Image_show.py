#coding:utf-8#

from PyQt5.QtWidgets import *
from PyQt5 import QtCore,QtWidgets,QtGui
from PyQt5.QtGui import *
import sys
import os

pic_folder=r'D:\JM\src\Job_Manager\pics\\'

class example(QWidget):
	def __init__(self):
		super(example,self).__init__()
		self.setFixedSize(420,320)
		self.layout=QGridLayout(self)
		self.Imageshow=QLabel()
		self.Paste=QPushButton('Paste',self)
		self.next_btn=QPushButton('Next',self)
		self.pre_btn=QPushButton('Previous',self)
		self.Imageshow.setGeometry(10,10,400,300)
		self.layout.addWidget(self.Imageshow,0,0,1,2)
		self.layout.addWidget(self.Paste,1,0)
		self.layout.addWidget(self.next_btn,2,0)
		self.layout.addWidget(self.pre_btn,2,1)

	
		self.next_btn.clicked.connect(self.load_img)
		self.pre_btn.clicked.connect(self.load_img)
		self.Paste.clicked.connect(self.paste_img)
		self.pic_to_show=r'.\pics\3.gif'
		self.image_to_show=r'.\pics\3.gif'
		# self.movie=QtGui.QMovie(self.image_to_show)
		# self.movie.setCacheMode(QtGui.QMovie.CacheAll)
		# self.movie.setScaledSize(self.Imageshow.size())
		#self.movie.setScaledContents(True)
		# self.Imageshow.setMovie(self.movie)
		# self.movie.start()
		#self.Imageshow.setPixmap(QPixmap(self.pic_to_show).scaled(self.Imageshow.size(), 
		#	QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
		self.img_no=-1
	def load_img(self):
		pic_types=['jpg','png']
		#print(self.sender().text())
		if self.sender().text()=='Next':
			step=1
		else:
			step=-1
		#print(step)
		files=os.listdir(pic_folder)
		#print(files)	
		Total_pics=len(files)
		self.img_no+=step
		if self.img_no==Total_pics:
			self.img_no=0
		if self.img_no<0:
			self.img_no=Total_pics-1
		print(self.img_no)
		pic_to_show=pic_folder+files[self.img_no]
		print(files[self.img_no].split('.'))
		if files[self.img_no].split('.')[1] in pic_types:
			self.Imageshow.setPixmap(QPixmap(pic_to_show).scaled(self.Imageshow.size(), 
				QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
		elif files[self.img_no].split('.')[1]=='gif':
			self.movie=QtGui.QMovie(pic_to_show)
			self.movie.setCacheMode(QtGui.QMovie.CacheAll)
			self.movie.setScaledSize(self.Imageshow.size())
			self.Imageshow.setMovie(self.movie)
			self.movie.start()
	def paste_img(self):
		clipboard=QApplication.clipboard()
		self.Imageshow.setPixmap(clipboard.pixmap().scaled(self.Imageshow.size(),QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
		
		file=r'd:\1.jpg'

		# with open(file,'w') as w:
		# 	w.write(clipboard.pixmap())
		clipboard.pixmap().save(file,'JPG')

if __name__=='__main__':
	app=QApplication(sys.argv)
	a=example()
	a.show()
	sys.exit(app.exec_())
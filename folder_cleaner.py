#coding:utf-8#

import os

def cleaner(path):
	folder=path
	del_ext=['.sta','.sim','.prt','.msg','.dat','.com','.odb_f','.mdl','.stt','.023','.rpy','.dmp','.1','.2','.3','.4','.5']
	files=os.listdir(folder)
	count=0
	for file in files:
		if os.path.splitext(folder+'\\'+file)[1] in del_ext:
			os.remove(folder+'\\'+file)
			count+=1
	print('{count} files were deleted successfully.'.format(count=count))
if __name__=='__main__':
	folder=r'C:\Job_Manager\Project\HEX\335NGH\C_pkg\Inp_Res'
	cleaner(folder)
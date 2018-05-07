#coding:utf-8#


__version__=0.02


import logging
logging.basicConfig(level=logging.INFO)


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys
from UI_JM import Ui_MainWindow
import getpass
import os
# import xlrd
# from xlrd import open_workbook
import subprocess
import threading
import time
#import xlutils.copy
import sqlite3
import SQL
import folder_cleaner
from collections import deque
from functools import wraps


#main sub-process definition
# def read_cell(cell):
    # if cell.ctype==0:
        # return ''
    # elif cell.ctype==1:
        # return cell.value
    # elif cell.ctype==2:
        # return str(int(cell.value))
    # elif cell.ctype==3:
        # date_value=xlrd.xldate_as_tuple(cell.value,book.datemode)
        # date_tmp = date(*date_value[:3]).strftime('%Y/%m/%d')
        # return date_tmp
    # elif cell.ctype==4:
        # return 'True' if cell.value==1 else 'False'
    
def folder_creation(case,case_structure):
    global case_wd 
    os.chdir(cwd)
    tempdir=cwd
    for i in range(len(case)-1):
        if not os.path.exists(str(case[i])):
            os.mkdir(str(case[i]))
        tempdir+=str(case[i])+'\\'
        os.chdir(tempdir)
        if case[i]==case[-2]:
            for folder in case_structure:
                if not os.path.exists(folder):
                    os.mkdir(tempdir+folder)
                    
def folder_check():
    con=sqlite3.connect(JM_database)
    with con:
        cur=con.cursor()
        cur.execute('select * from %s' % JM_database_tabs[1])
        values=cur.fetchall()
        cases=[list(each) for each in values]
        for case in cases:
            case.pop(0)
            case[0]='Project'
            folder_creation(case,case_structure)

def readrow(path,tab,key):
    iteration_list=[]
    if os.path.exists(path):
        con=sqlite3.connect(path)
        with con:
            cur=con.cursor()
            try:
                cur.execute("select * from %s" % tab)
                row_datas=cur.fetchall()
                if len(row_datas)==0:
                    return 'Not found %s in %s' % (key,tab)
                else:
                    level_dict=dict()
                    for row_data in row_datas:
                        if row_data[9]==key[0] and row_data[10]==key[1]:
                            data=list(row_data)
                            data[9]=str(data[9])
                            row_data=tuple(data)
                            #print(row_data)
                            item={'level': '', 
                                  'sid': '', 
                                  'parent_ID': '', 
                                  'Job_name': '', 
                                  'Job_type':'',
                                  'des': ''}
                            if row_data[1]=='None':
                                level_dict[row_data[0]]=0
                            else:
                                level_dict[row_data[0]]=level_dict[row_data[1]]+1
                            item={'level': level_dict[row_data[0]], 
                                  'sid': row_data[0], 
                                  'parent_ID': row_data[1], 
                                  'Job_name': row_data[6], 
                                  'Job_type': row_data[5],
                                  'des': '\n' + row_data[12]}
                            iteration_list.append(item)
                            #print(item)
                return iteration_list
            except:
                print('Given Job/Tab name is invalid')
    else:
        print('Given database is invalid')

#Root info collect
user = getpass.getuser()
cpus_number = 8
path = os.path.abspath('.')
notepadpath = r"C:\Fangjie\Programs\npp\notepad++.exe"
startupfolder = path + r'\startup\\'
hmpath = startupfolder + 'hm17.lnk'
cwd = path +'\\'
JM_database = path + r'\data\Jobs_data.db'
JM_database_tabs = ['Job_list','Project_list']
JM_files_db = path + r'\data\Files_data.db'
JM_files_tabs = ['Case_info','Include_info']
case_structure = ['Inp_Res','Reports','CAD']
Machine_type_list = ['Engine','HEX','TTT','WL','MG']
Product_list = ['C_pkg','CEM','Muffler','Fan','Other']
Job_type_list = ['Gload','Mode','PreT','Lifting','Pressure']
check_exist = ['model_folder','main_file','fem_file','Ass1_file','Ass2_file','CPL_file','steps_file','result_file']

def Timer(func):
    def wrapper(self):
        start = time.time()
        string = func.__name__ + ' was called'
        func(self)
        stop = time.time()
        print('Time cost {s}s for {f}'.format(s="{:.4f}".format(stop-start),f=string))
    return wrapper

class Main(QMainWindow, Ui_MainWindow): 
    _signal_mainfile_folder=QtCore.pyqtSignal(str)
    _signal_femfile_folder=QtCore.pyqtSignal(str)
    _signal_Ass1file_folder=QtCore.pyqtSignal(str)
    _signal_Ass2file_folder=QtCore.pyqtSignal(str)
    _signal_CPLfile_folder=QtCore.pyqtSignal(str)
    _signal_stepsfile_folder=QtCore.pyqtSignal(str)
    
    _signal_mainfile_np=QtCore.pyqtSignal(str)
    _signal_femfile_np=QtCore.pyqtSignal(str)
    _signal_Ass1file_np=QtCore.pyqtSignal(str)
    _signal_Ass2file_np=QtCore.pyqtSignal(str)
    _signal_CPLfile_np=QtCore.pyqtSignal(str)
    _signal_stepsfile_np=QtCore.pyqtSignal(str)
    
    _signal_mainfile_hm=QtCore.pyqtSignal(str)
    _signal_femfile_hm=QtCore.pyqtSignal(str)
    _signal_Ass1file_hm=QtCore.pyqtSignal(str)
    _signal_Ass2file_hm=QtCore.pyqtSignal(str)
    _signal_CPLfile_hm=QtCore.pyqtSignal(str)
    _signal_stepsfile_hm=QtCore.pyqtSignal(str)  


    def __init__(self):
        QMainWindow.__init__(self)
        self.Job_edit_btn_status='edit'
        self.job_info=[]
        self.new_Job_info=[]
        self.setupUi(self) 
        self.exist_status = dict()  #file:0/1  0 for no,1 for yes
        self.iterations = dict()
        for i in check_exist:
            self.exist_status[i]=0 
            
        self._signal_mainfile_folder.connect(self.Openfolder) 
        self._signal_femfile_folder.connect(self.Openfolder)
        self._signal_Ass1file_folder.connect(self.Openfolder)
        self._signal_Ass2file_folder.connect(self.Openfolder)
        self._signal_CPLfile_folder.connect(self.Openfolder)
        self._signal_stepsfile_folder.connect(self.Openfolder)   
        
        self._signal_mainfile_np.connect(self.Opennp) 
        self._signal_femfile_np.connect(self.Opennp)
        self._signal_Ass1file_np.connect(self.Opennp)
        self._signal_Ass2file_np.connect(self.Opennp)
        self._signal_CPLfile_np.connect(self.Opennp)
        self._signal_stepsfile_np.connect(self.Opennp)  
        
        self._signal_mainfile_hm.connect(self.Openhm)
        self._signal_femfile_hm.connect(self.Openhm)
        self._signal_Ass1file_hm.connect(self.Openhm)
        self._signal_Ass2file_hm.connect(self.Openhm)
        self._signal_CPLfile_hm.connect(self.Openhm)
        self._signal_stepsfile_hm.connect(self.Openhm)  
        
        self.Job_edit_btn.clicked.connect(self.Job_edit)  
        self.Job_creation_btn.clicked.connect(self.Createcase) 
        self.Prj_info_add_btn.clicked.connect(self.AddPrjInfo)
        
        self.Machine_CB.currentIndexChanged.connect(self.Product_CB_load)
        self.Machine_type_CB.currentIndexChanged.connect(self.Machine_CB_load)
        #self.Product_CB.currentIndexChanged.connect(self.iteration_list_load)
        
        self.Product_CB.clear()
        self.Jobtype_CB.clear()
        self.Machine_CB.clear()
        self.Machine_type_CB.clear()


        self.Machine_type_CB_3.clear()
        self.Machine_type_CB_3.addItems(Machine_type_list)
        self.Product_CB_3.clear()
        self.Product_CB_3.addItems(Product_list)

        Jobtype_CB_list=Job_type_list
        #self.Product_CB.addItems(Product_CB_list)
        self.Jobtype_CB.addItems(Jobtype_CB_list)
        
        self.new_job_flag=0
        self.editable_flag=0
        
        self.Readprjs()
        self.iteration_list_load()
        self.Product_CB.currentIndexChanged.connect(self.iteration_list_load)
        
        self.model=QtGui.QStandardItemModel()
        self.iteration_list_items = ['Job_number','Job_type','Description']
        self.model.setHorizontalHeaderLabels(self.iteration_list_items)
        self.Iterations_list.setIndentation(8)
        #self.Iterations_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
    
    def importData(self, data, root=None):
        self.model.setRowCount(0)
        if root is None:
            root = self.model.invisibleRootItem()
        seen = {}
        values = deque(data)
        while values:
            value = values.popleft()
            if value['level'] == 0:
                parent = root
            else:
                pid = value['parent_ID']
                if pid not in seen:
                    values.append(value)
                    continue
                parent = seen[pid]
            dbid = value['sid']
            parent.appendRow([
                QtGui.QStandardItem(str(value['sid'])),
                QtGui.QStandardItem(value['Job_type']),
                QtGui.QStandardItem(value['des']),
                ])
            seen[dbid] = parent.child(parent.rowCount() - 1)
            
    def AddPrjInfo(self):
        plt=self.Machine_type_CB_3.currentText() 
        product=self.Product_CB_3.currentText() 
        prj=self.Add_machine.toPlainText()
        new_item=[SQL.newPrjnum(JM_database,JM_database_tabs[1]),'',plt,str(prj),product]
        dup_flag=False
        lines=SQL.readrows(JM_database,JM_database_tabs[1])
        for line in lines:
            info=[line[2],line[3],line[4]]
            if info==[plt,str(prj),product]:
                dup_flag=True
                reply = QMessageBox.warning(self, 'Warning',"The Project is already in database",QMessageBox.Ok) 
        if dup_flag==False:
            SQL.createrow(JM_database,JM_database_tabs[1],new_item)
            folder_check()
        self.Status_bar.setText("New project has been added into database")
        
    def Initialization(self):
        self.Machine_types=[]  
        self.Machines=[]
        
        _translate = QtCore.QCoreApplication.translate 
        self.MK_info.setText(_translate("MainWindow", ''))
        self.IK_info.setText(_translate("MainWindow", ''))


        self.Job_name_text.setText(_translate("MainWindow", ''))
        self.FEM_file_name.setText(_translate("MainWindow", ''))
        self.FEM_file_name_2.setText(_translate("MainWindow", ''))
        self.FEM_file_name_3.setText(_translate("MainWindow", ''))
        self.FEM_file_name_4.setText(_translate("MainWindow", ''))
        self.steps_file_name.setText(_translate("MainWindow", ''))
        self.result_file_name.setText(_translate("MainWindow", '')) 


        self.FEM_file_info.setText(_translate("MainWindow", ''))
        self.FEM_file_info_2.setText(_translate("MainWindow", ''))
        self.FEM_file_info_3.setText(_translate("MainWindow", ''))
        self.FEM_file_info_4.setText(_translate("MainWindow", ''))
        self.steps_file_info.setText(_translate("MainWindow", ''))


        self.Job_file_status.setStyleSheet("background:white;")
        self.fem_file_status.setStyleSheet("background:white;")
        self.fem_file_status_2.setStyleSheet("background:white;")
        self.fem_file_status_3.setStyleSheet("background:white;")
        self.fem_file_status_4.setStyleSheet("background:white;")
        self.steps_file_status.setStyleSheet("background:white;")
        self.result_file_status.setStyleSheet("background:white;")
        
        self.label_JNo.setText(_translate("MainWindow", ''))
        self.label_Jbase.setText(_translate("MainWindow", ''))
        self.label_Juser.setText(_translate("MainWindow", ''))
        self.label_Jcreation.setText(_translate("MainWindow", ''))
        self.label_Jedit.setText(_translate("MainWindow", ''))
        self.label_Jtype.setText(_translate("MainWindow", ''))
        self.label_Jname.setText(_translate("MainWindow", ''))
        self.label_Jmark.setText(_translate("MainWindow", ''))
        self.MK_info.setText(_translate("MainWindow", ''))
        self.IK_info.setText(_translate("MainWindow", ''))
        self.post_info_label.setText(_translate("MainWindow", "No post info record"))
        self.design_feature_label.setText(_translate("MainWindow", "No design feature record"))
        self.design_feature_nb_label.setText(_translate("MainWindow", '0/0'))
        self.post_info_nb_label.setText(_translate("MainWindow", '0/0'))
        try:
            self.CB_FEM_No.clear()
            self.CB_FEM_No_2.clear()
            self.CB_FEM_No_3.clear()
            self.CB_FEM_No_4.clear()
            self.CB_steps_No.clear()

            self.job_file_add.clicked.disconnect(self.submit_job_local)
            self.pushButton.clicked.disconnect(self.fld_clean)
            self.np_job_name.clicked.disconnect(self.mainfilenpSignal)
            self.hm_job_name.clicked.disconnect(self.mainfilehmSignal)
            self.np_fem.clicked.disconnect(self.femfilenpSignal)
            self.hm_fem.clicked.disconnect(self.femfilehmSignal)
            self.np_steps.clicked.disconnect(self.stepsfilenpSignal)
            self.hm_steps.clicked.disconnect(self.stepsfilehmSignal)
            self.job_file_folder.clicked.disconnect(self.mainfilefolderSignal)
            self.fem_file_folder.clicked.disconnect(self.femfilefolderSignal)
            self.steps_file_folder.clicked.disconnect(self.stepsfilefolderSignal)   
            self.av_result.clicked.disconnect(self.load_odb_result)
            
            self.design_feature_next_btn.clicked.disconnect(self.load_dgn_img)
            self.design_feature_bf_btn.clicked.disconnect(self.load_dgn_img)
            self.post_info_next_btn.clicked.disconnect(self.load_post_img)
            self.post_info_bf_btn.clicked.disconnect(self.load_post_img)

        except:
            pass
        
        try:
            self.Product_CB.currentIndexChanged.disconnect(self.iteration_list_load)
        except:
            pass
        
        self.Machine_type_CB.clear()
        self.Machine_CB.clear()


        #self.Readprjs()


        self.model_folder=''
        self.fem_file=''
        self.Ass1_file=''
        self.Ass2_file=''
        self.CPL_file=''
        self.steps_file=''
        
        self.img_no=-1
        self.img_no_post=-1

    def ReadIncludeCmt(self,path,tab,key):
        temp=[]
        temp=SQL.readrow_s(path,tab,key)
        return str(temp[7])

    def mainfilefolderSignal(self):
        self._signal_mainfile_folder.emit(self.model_folder+self.main_file)
    def femfilefolderSignal(self):
        self._signal_femfile_folder.emit(self.model_folder+self.fem_file)
    def Ass1filefolderSignal(self):
        self._signal_Ass1file_folder.emit(self.model_folder+self.Ass1_file)
    def Ass2filefolderSignal(self):
        self._signal_Ass2file_folder.emit(self.model_folder+self.Ass2_file)
    def CPLfilefolderSignal(self):
        self._signal_CPLfile_folder.emit(self.model_folder+self.CPL_file)
    def stepsfilefolderSignal(self):
        self._signal_stepsfile_folder.emit(self.model_folder+self.steps_file)
        
    def mainfilenpSignal(self):
        self._signal_mainfile_np.emit(self.model_folder+self.main_file)
    def femfilenpSignal(self):
        self._signal_femfile_np.emit(self.model_folder+self.fem_file)
    def Ass1filenpSignal(self):
        self._signal_Ass1file_np.emit(self.model_folder+self.Ass1_file)
    def Ass2filenpSignal(self):
        self._signal_Ass2file_np.emit(self.model_folder+self.Ass2_file)
    def CPLfilenpSignal(self):
        self._signal_CPLfile_np.emit(self.model_folder+self.CPL_file)
    def stepsfilenpSignal(self):
        self._signal_stepsfile_np.emit(self.model_folder+self.steps_file) 
        
    def mainfilehmSignal(self):
        self._signal_mainfile_hm.emit(self.model_folder+self.main_file)
    def femfilehmSignal(self):
        self._signal_femfile_hm.emit(self.model_folder+self.fem_file)
    def Ass1filehmSignal(self):
        self._signal_Ass1file_hm.emit(self.model_folder+self.Ass1_file)
    def Ass2filehmSignal(self):
        self._signal_Ass2file_hm.emit(self.model_folder+self.Ass2_file)
    def CPLfilehmSignal(self):
        self._signal_CPLfile_hm.emit(self.model_folder+self.CPL_file)
    def stepsfilehmSignal(self):
        self._signal_stepsfile_hm.emit(self.model_folder+self.steps_file) 

    def Readprjs(self):
        '''0:Gload, 1:Mode'''
        try:
            self.Product_CB.currentIndexChanged.disconnect(self.iteration_list_load)
        except:
            pass
        
        Machine_b=[]
        Machines=[]
        self.Machine_types=[]
        rows=SQL.readrows(JM_database, JM_database_tabs[1])
        for row in rows:
            Machine_temp=[row[2],row[3],row[4]]
            Machines.append(Machine_temp)
            if row[2] not in self.Machine_types:
                self.Machine_types.append(row[2])
                
        self.Machines=[]
        for i in Machines:
            if i not in self.Machines:
                self.Machines.append(i)
        self.Machine_types.insert(0,'None')
        self.Machine_type_CB.clear()
        self.Machine_type_CB.addItems(self.Machine_types)
        self.Showprjs()
     
    #@Timer
    def Showprjs(self):
        Job_types=dict()
        for index,item in enumerate(Job_type_list):
            Job_types[item]=index
        Product_types={'CEM':0,'C_pkg':1,'Muffler':2,'Other':3}
        try:
            if self.Job_info[8]!='':
                self.Machine_type_CB.setCurrentIndex(self.Machine_types.index(self.Job_info[8]))
                self.Machine_CB_load()    
            if self.Job_info[5]!='':
                self.Jobtype_CB.setCurrentIndex(Job_types[self.Job_info[5]])
            # if self.Job_info[10]!='':
            #     self.Product_CB.setCurrentIndex(Product_types[self.Job_info[10]])
        except:
            pass
       
    def Machine_CB_load(self,index=-1):
        self.Machine_CB.clear()
        if index==-1:
            current_Machine_type=self.Machine_type_CB.currentText()
        else:
            current_Machine_type=self.Machine_types[index]
        if current_Machine_type=='None':
            self.Machine_CB.clear()
        Machine=[]
        for i in self.Machines:
            if i[0]==current_Machine_type:
                if i[1] not in Machine:
                    Machine.append(str(i[1]))
        self.Machine_CB.addItems(Machine)
        try:
            if self.Job_info[9] in Machine:
                self.Machine_CB.setCurrentIndex(Machine.index(self.Job_info[9]))
        except:
            pass

    def Product_CB_load(self,index=-1):
        try:
            self.Product_CB.currentIndexChanged.disconnect(self.iteration_list_load)
        except:
            pass
        self.Product_CB.clear()
        current_Machine=self.Machine_CB.currentText()
        Product=[]
        for i in self.Machines:
            if i[1]==current_Machine:
                if i[2] not in Product:
                    Product.append(str(i[2]))
        self.Product_CB.addItems(Product)
        
        Job_number=self.Job_number_input.toPlainText()
        if Job_number == '':
            self.iteration_list_load()   
            
        try:
            if self.Job_info[10] in Product:
                self.Product_CB.setCurrentIndex(Product.index(self.Job_info[10]))
        except:
            pass
        if len(Product)==0:
            self.iteration_list_load()
        self.Product_CB.currentIndexChanged.connect(self.iteration_list_load)
           
    #@Timer
    def iteration_list_load(self):
        current_Machine=self.Machine_CB.currentText()
        current_Product=self.Product_CB.currentText()
        if current_Machine!='' and current_Product!='':
            self.Iterations_list.setModel(self.model)
            data=dict()
            data=readrow(JM_database,JM_database_tabs[0],[current_Machine,current_Product])
            self.iterations = data
            self.importData(data)
            self.Iterations_list.expandAll()
            self.Iterations_list.setAlternatingRowColors(True)
            for i in range(len(self.iteration_list_items)):
                self.Iterations_list.resizeColumnToContents(i)
    
    #def Iteration_quick_entry(self):
        
    def Job_edit(self):
        if self.Job_edit_btn_status=='edit':
            self.Editcase()
        elif self.Job_edit_btn_status=='save':
            self.Savecase()

    def Createcase(self):
        '''Create an new job number by the latest job number in the database'''
        self.njobno=SQL.newjobnum(JM_database, JM_database_tabs[0])
        '''Judge whether the case is brand new creation or an iteration'''
        Job_number=self.Job_number_input.toPlainText()
        if self.Machine_type_CB.currentText()=='None':
            reply = QMessageBox.warning(self, 'Warning',"Please select machine type first",QMessageBox.Ok)
            self.svflag=0
        else:
            if Job_number=='':
                self.new_job_flag=1
                basenumber='None'
                print('This run is new')
                '''Create basic job info in database'''
                self.new_Job_info=[self.njobno,basenumber,user,time.ctime(),time.ctime(),self.Jobtype_CB.currentText(),'','',self.Machine_type_CB.currentText(),self.Machine_CB.currentText(),self.Product_CB.currentText(),'','']
            else:
                basenumber=Job_number
                #self.Ori_ICLD_index=[self.CB_FEM_No.currentIndex(),self.CB_FEM_No_2.currentIndex(),self.CB_FEM_No_3.currentIndex(),self.CB_FEM_No_4.currentIndex(),self.CB_steps_No.currentIndex()]
                
                '''Copy base main file'''
                original_file=self.model_folder+self.main_file
                new_main_file=self.main_file.replace(str(Job_number),str(self.njobno))
                new_file=self.model_folder+new_main_file.replace(self.Job_info[5],self.Jobtype_CB.currentText())
                with open(original_file,'r') as r:
                    lines=r.readlines()
                with open(new_file,'w') as f:
                    for line in lines:
                        f.write(line)


                print('This run is based on %s' % Job_number)
                '''Create basic job info in database'''
                self.new_Job_info=[self.njobno,basenumber,user,time.ctime(),time.ctime(),self.Jobtype_CB.currentText(),self.Job_info[6],self.Job_info[7],self.Job_info[8],self.Job_info[9],self.Job_info[10],self.Job_info[11],self.Job_info[12]]




            SQL.createrow(JM_database, JM_database_tabs[0], self.new_Job_info)
            print('Info written to SQL')
            '''Put the new job number in the job_number input label'''
            self.Job_number_input.setPlainText(str(self.njobno))
            self.Job_number_input.setAlignment(QtCore.Qt.AlignCenter)
            '''Reload the jobinfo to display in main UI'''
            self.Readcase()
            print('Reread case done')


            self.editable_flag=1
            '''Basic info creation is finished,proceed on detail edit'''
            self.Editcase()
            self.Status_bar.setText('Case is created, In edit case mode')
            
    def Editcase(self):
        try:
            if self.Job_info[0]!='':
                if self.editable_flag==1:
                    _translate = QtCore.QCoreApplication.translate 
                    self.Job_edit_btn.setText(_translate("MainWindow", "Save"))
                    self.Job_edit_btn_status='save'
                    '''Activate the edit mode of comment input'''
                    self.MK_info.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextEditable|QtCore.Qt.TextSelectableByMouse)
                    self.IK_info.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextEditable|QtCore.Qt.TextSelectableByMouse)
                    self.FEM_file_info.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextEditable|QtCore.Qt.TextSelectableByMouse)
                    self.FEM_file_info_2.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextEditable|QtCore.Qt.TextSelectableByMouse)
                    self.FEM_file_info_3.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextEditable|QtCore.Qt.TextSelectableByMouse)
                    self.FEM_file_info_4.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextEditable|QtCore.Qt.TextSelectableByMouse)
                    self.steps_file_info.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextEditable|QtCore.Qt.TextSelectableByMouse)
                    
                    self.CB_FEM_No.currentIndexChanged.connect(self.CB_FEM_No_change)
                    self.CB_FEM_No_2.currentIndexChanged.connect(self.CB_Ass1_No_change)
                    self.CB_FEM_No_3.currentIndexChanged.connect(self.CB_Ass2_No_change)
                    self.CB_FEM_No_4.currentIndexChanged.connect(self.CB_CPL_No_change)
                    self.CB_steps_No.currentIndexChanged.connect(self.CB_steps_No_change)




                    '''Get project info from database and put into ComboBox'''
                    self.Readprjs()
                    self.iteration_list_load()
                    self.Product_CB.currentIndexChanged.connect(self.iteration_list_load)
                    
                    print('Project info is loaded')
                    self.Status_bar.setText('In edit case mode')


                FEM_files,Ass1_files,Ass2_files,Steps_files,CPL_files=self.Folderfiles(self.model_folder)


                self.CB_FEM_No.clear()
                self.CB_FEM_No_2.clear()
                self.CB_FEM_No_3.clear()
                self.CB_FEM_No_4.clear()
                self.CB_steps_No.clear()


                self.CB_FEM_No.addItems(FEM_files)
                if len(FEM_files)!=1:
                    for j in FEM_files:
                        if self.exist_status['fem_file']==j:
                            self.CB_FEM_No.setCurrentIndex(FEM_files.index(j))


                self.CB_FEM_No_2.addItems(Ass1_files)
                if len(Ass1_files)!=1:
                    for j in Ass1_files:
                        if self.exist_status['Ass1_file']==j:
                            self.CB_FEM_No_2.setCurrentIndex(Ass1_files.index(j))


                self.CB_FEM_No_3.addItems(Ass2_files)
                if len(Ass2_files)!=1:
                    for j in Ass2_files:
                        if self.exist_status['Ass2_file']==j:
                            self.CB_FEM_No_3.setCurrentIndex(Ass2_files.index(j))


                self.CB_FEM_No_4.addItems(CPL_files)
                if len(CPL_files)!=1:
                    for j in CPL_files:
                        if self.exist_status['CPL_file']==j:
                            self.CB_FEM_No_4.setCurrentIndex(CPL_files.index(j))


                self.CB_steps_No.addItems(Steps_files)
                if len(Steps_files)!=1:
                    for j in Steps_files:
                        if self.exist_status['steps_file']==j:
                            self.CB_steps_No.setCurrentIndex(Steps_files.index(j))


                self.fem_file_add.clicked.connect(self.Add_fem_file)
                self.fem_file_add_2.clicked.connect(self.Add_Ass1_file)
                self.fem_file_add_3.clicked.connect(self.Add_Ass2_file)
                self.fem_file_add_4.clicked.connect(self.Add_CPL_file)
                self.steps_file_add.clicked.connect(self.Add_steps_file)
        except:
            pass

    def CB_FEM_No_change(self):
        _translate = QtCore.QCoreApplication.translate
        Crt_No=self.CB_FEM_No.currentText()
        if Crt_No!='000':
            self.fem_file=self.Job_info[9]+'_'+self.Job_info[10]+'_FEM_'+Crt_No+'.inp'
            try:
                self.FEM_file_info.setText(_translate("MainWindow", self.ReadIncludeCmt(JM_files_db, JM_files_tabs[1], self.fem_file)))
            except:
                pass
        else:
            self.fem_file=''    
        self.FEM_file_name.setText(_translate("MainWindow", self.fem_file))

    def CB_Ass1_No_change(self):
        _translate = QtCore.QCoreApplication.translate
        Crt_No=self.CB_FEM_No_2.currentText()
        if Crt_No!='000':
            self.Ass1_file=self.Job_info[9]+'_'+self.Job_info[10]+'_Ass1_'+Crt_No+'.inp'
            try:
                self.FEM_file_info_2.setText(_translate("MainWindow", self.ReadIncludeCmt(JM_files_db, JM_files_tabs[1], self.Ass1_file)))
            except:
                pass
        else:
            self.Ass1_file=''
        self.FEM_file_name_2.setText(_translate("MainWindow", self.Ass1_file))

    def CB_Ass2_No_change(self):
        _translate = QtCore.QCoreApplication.translate
        Crt_No=self.CB_FEM_No_3.currentText()
        if Crt_No!='000':
            self.Ass2_file=self.Job_info[9]+'_'+self.Job_info[10]+'_Ass2_'+Crt_No+'.inp'
            try:
                self.FEM_file_info_3.setText(_translate("MainWindow", self.ReadIncludeCmt(JM_files_db, JM_files_tabs[1], self.Ass2_file)))
            except:
                pass
        else:
            self.Ass2_file=''
        self.FEM_file_name_3.setText(_translate("MainWindow", self.Ass2_file))

    def CB_CPL_No_change(self):
        _translate = QtCore.QCoreApplication.translate
        Crt_No=self.CB_FEM_No_4.currentText()
        if Crt_No!='000':
            self.CPL_file=self.Job_info[9]+'_'+self.Job_info[10]+'_CPL_'+Crt_No+'.inp'
            try:
                self.FEM_file_info_4.setText(_translate("MainWindow", self.ReadIncludeCmt(JM_files_db, JM_files_tabs[1], self.CPL_file)))
            except:
                pass
        else:
            self.CPL_file=''
        self.FEM_file_name_4.setText(_translate("MainWindow", self.CPL_file))

    def CB_steps_No_change(self):
        _translate = QtCore.QCoreApplication.translate
        Crt_No=self.CB_steps_No.currentText()
        if Crt_No!='000':
            self.steps_file=self.Job_info[9]+'_'+self.Job_info[10]+'_Steps_'+Crt_No+'.inp'
            try:
                self.steps_file_info.setText(_translate("MainWindow", self.ReadIncludeCmt(JM_files_db, JM_files_tabs[1], self.steps_file)))
            except:
                pass
        else:
            self.steps_file=''
        self.steps_file_name.setText(_translate("MainWindow", self.steps_file))
       
    def Savecase(self):
        _translate = QtCore.QCoreApplication.translate
        '''Initialization of new job info'''
        #self.new_Job_info=[]
        '''Get all input info'''
        self.Getallinput()
        '''Save all new info into database'''
        #print(self.new_Job_info)
        SQL.editrow(JM_database, JM_database_tabs[0], self.new_Job_info)
        self.job_file_recreation()
        '''if it's brand new creation, need to create the files'''
        if self.new_job_flag==1:
            self.new_job_file_creation()


        self.fem_comment=self.FEM_file_info.toPlainText()
        self.Ass1_comment=self.FEM_file_info_2.toPlainText()
        self.Ass2_comment=self.FEM_file_info_3.toPlainText()
        self.CPL_comment=self.FEM_file_info_4.toPlainText()
        self.steps_comment=self.steps_file_info.toPlainText()
        comment=[self.fem_comment,self.Ass1_comment,self.Ass2_comment,self.CPL_comment,self.steps_comment]
        files=[self.fem_file,self.Ass1_file,self.Ass2_file,self.CPL_file,self.steps_file]
        for i in range(len(files)):
            if files[i]!='':
                try:
                    self.old_data=SQL.readrow_s(JM_files_db, JM_files_tabs[1], files[i])
                    #edit_on info
                    self.old_data[5]=time.ctime()
                    #edit_by info
                    self.old_data[6]=user
                    #comment info
                    if self.old_data[7]!=str(comment[i]):
                        self.old_data[7]=str(comment[i])
                        SQL.editrow(JM_files_db,JM_files_tabs[1],self.old_data)
                except:
                    pass


        '''if anything changed between new input and exist info, save the new input'''
        if self.svflag==1:  
            self.Readcase()
            self.Job_edit_btn.setText(_translate("MainWindow", "Edit"))
            self.Job_edit_btn_status='edit'
            #Enable the textbrowser to be edited
            self.MK_info.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextSelectableByMouse)
            self.IK_info.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextSelectableByMouse)
            self.FEM_file_info.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextSelectableByMouse)
            self.FEM_file_info_2.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextSelectableByMouse)
            self.FEM_file_info_3.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextSelectableByMouse)
            self.FEM_file_info_4.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextSelectableByMouse)
            self.steps_file_info.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextSelectableByMouse)
            
            self.CB_FEM_No.currentIndexChanged.disconnect(self.CB_FEM_No_change)
            self.CB_FEM_No_2.currentIndexChanged.disconnect(self.CB_Ass1_No_change)
            self.CB_FEM_No_3.currentIndexChanged.disconnect(self.CB_Ass2_No_change)
            self.CB_FEM_No_4.currentIndexChanged.disconnect(self.CB_CPL_No_change)
            self.CB_steps_No.currentIndexChanged.disconnect(self.CB_steps_No_change)


            self.Status_bar.setText('Case is saved')


        
        self.new_Job_info=[]


        self.fem_file_add.clicked.disconnect(self.Add_fem_file)
        self.fem_file_add_2.clicked.disconnect(self.Add_Ass1_file)
        self.fem_file_add_3.clicked.disconnect(self.Add_Ass2_file)
        self.fem_file_add_4.clicked.disconnect(self.Add_CPL_file)
        self.steps_file_add.clicked.disconnect(self.Add_steps_file)

    def Getallinput(self):
        '''print exist job_info'''
        #print('self.Job_info:',self.Job_info)
        #print(len(self.new_Job_info))
        if len(self.new_Job_info)>0:
            print('It\'s create mode')
        else:
            self.new_Job_info=[int(self.Job_number_input.toPlainText()),self.Job_info[1],self.Job_info[2],self.Job_info[3],'','','','','','','','','','']
        #print(self.new_Job_info)
        #self.Machine_CB_load()
        self.New_Machine_type=self.Machine_type_CB.currentText()
        if self.New_Machine_type=='None':
            reply = QMessageBox.warning(self, 'Warning',"Please select machine type first",QMessageBox.Ok)
            self.svflag=0
        else:
            self.New_Machine=self.Machine_CB.currentText()
            if self.New_Machine=='':
                reply = QMessageBox.warning(self, 'Warning',"Please select machine",QMessageBox.Ok)
                self.svflag=0 
            else:
                self.svflag=1
                self.New_Edit_time=time.ctime()
                #print(self.New_Edit_time)
                self.new_Job_info[4]=self.New_Edit_time
                self.New_Job_type=self.Jobtype_CB.currentText()
                self.new_Job_info[5]=self.New_Job_type
                self.New_Product=self.Product_CB.currentText()
                #print(self.New_Product)
                self.New_job_name=self.Job_number_input.toPlainText()+'_'+self.New_Machine+'_'+self.New_Product+'_'+self.New_Job_type
                #print(self.New_job_name)
                self.new_Job_info[6]=self.New_job_name
                self.new_Job_info[7]=self.Job_mark_status.currentText()
                self.new_Job_info[8]=self.New_Machine_type
                self.new_Job_info[9]=self.New_Machine
                self.new_Job_info[10]=self.New_Product
                
                
                self.New_MK_info=self.MK_info.toPlainText()
                self.new_Job_info[11]=self.New_MK_info
                self.New_IK_info=self.IK_info.toPlainText()
                self.new_Job_info[12]=self.New_IK_info
                self.New_FEM_info=self.FEM_file_info.toPlainText()
                self.New_steps_info=self.steps_file_info.toPlainText()
                
    def Add_fem_file(self):
        _translate = QtCore.QCoreApplication.translate
        FEM_files,Ass1_files,Ass2_files,Steps_files,CPL_files=self.Folderfiles(self.model_folder)
        lines=['',]
        Base_No=self.CB_FEM_No.currentText()
        Base_fem_file=self.Job_info[9]+'_'+self.Job_info[10]+'_FEM_'+Base_No+'.inp'
        New_fem_file=self.Job_info[9]+'_'+self.Job_info[10]+'_FEM_'+"{:0>3d}".format(int(FEM_files[-1])+1)+'.inp'
        if Base_No!='000':
            if os.path.exists(self.model_folder+Base_fem_file)==True:
                with open(self.model_folder+Base_fem_file,'r') as f:
                    lines+=f.readlines()
        with open(self.model_folder+New_fem_file,'w') as f:
            for line in lines:
                f.write(line)


        FEM_files,Ass1_files,Ass2_files,Steps_files,CPL_files=self.Folderfiles(self.model_folder)
        self.CB_FEM_No.clear()  
        self.CB_FEM_No.addItems(FEM_files)
        self.CB_FEM_No.setCurrentIndex(len(FEM_files)-1)
        self.FEM_file_name.setText(_translate("MainWindow", New_fem_file))
        self.fem_file=New_fem_file 


        if Base_No=='000':
            Base_fem_file=''
        self.new_fem_info=[self.fem_file,'fem',user,Base_fem_file,time.ctime(),time.ctime(),user,'','']
        SQL.createrow(JM_files_db, JM_files_tabs[1], self.new_fem_info) 

    def Add_Ass1_file(self):
        _translate = QtCore.QCoreApplication.translate
        FEM_files,Ass1_files,Ass2_files,Steps_files,CPL_files=self.Folderfiles(self.model_folder)
        lines=['',]
        Base_No=self.CB_FEM_No_2.currentText()
        Base_fem_file=self.Job_info[9]+'_'+self.Job_info[10]+'_Ass1_'+Base_No+'.inp'
        New_fem_file=self.Job_info[9]+'_'+self.Job_info[10]+'_Ass1_'+"{:0>3d}".format(int(Ass1_files[-1])+1)+'.inp'
        if Base_No!='000':
            if os.path.exists(self.model_folder+Base_fem_file)==True:
                with open(self.model_folder+Base_fem_file,'r') as f:
                    lines+=f.readlines()
        with open(self.model_folder+New_fem_file,'w') as f:
            for line in lines:
                f.write(line)


        FEM_files,Ass1_files,Ass2_files,Steps_files,CPL_files=self.Folderfiles(self.model_folder)
        self.CB_FEM_No_2.clear()  
        self.CB_FEM_No_2.addItems(Ass1_files)
        self.CB_FEM_No_2.setCurrentIndex(len(Ass1_files)-1)
        self.FEM_file_name_2.setText(_translate("MainWindow", New_fem_file))
        self.Ass1_file=New_fem_file  


        if Base_No=='000':
            Base_fem_file=''
        self.new_fem_info=[self.Ass1_file,'Ass1',user,Base_fem_file,time.ctime(),time.ctime(),user,'','']
        SQL.createrow(JM_files_db, JM_files_tabs[1], self.new_fem_info) 

    def Add_Ass2_file(self):
        _translate = QtCore.QCoreApplication.translate
        FEM_files,Ass1_files,Ass2_files,Steps_files,CPL_files=self.Folderfiles(self.model_folder)
        lines=['',]
        Base_No=self.CB_FEM_No_3.currentText()
        Base_fem_file=self.Job_info[9]+'_'+self.Job_info[10]+'_Ass2_'+Base_No+'.inp'
        New_fem_file=self.Job_info[9]+'_'+self.Job_info[10]+'_Ass2_'+"{:0>3d}".format(int(Ass2_files[-1])+1)+'.inp'
        if Base_No!='000':
            if os.path.exists(self.model_folder+Base_fem_file)==True:
                with open(self.model_folder+Base_fem_file,'r') as f:
                    lines+=f.readlines()
        with open(self.model_folder+New_fem_file,'w') as f:
            for line in lines:
                f.write(line)


        FEM_files,Ass1_files,Ass2_files,Steps_files,CPL_files=self.Folderfiles(self.model_folder)
        self.CB_FEM_No_3.clear()  
        self.CB_FEM_No_3.addItems(Ass2_files)
        self.CB_FEM_No_3.setCurrentIndex(len(Ass2_files)-1)
        self.FEM_file_name_3.setText(_translate("MainWindow", New_fem_file))
        self.Ass2_file=New_fem_file  


        if Base_No=='000':
            Base_fem_file=''
        self.new_fem_info=[self.Ass2_file,'Ass2',user,Base_fem_file,time.ctime(),time.ctime(),user,'','']
        SQL.createrow(JM_files_db, JM_files_tabs[1], self.new_fem_info) 

    def Add_CPL_file(self):
        _translate = QtCore.QCoreApplication.translate
        FEM_files,Ass1_files,Ass2_files,Steps_files,CPL_files=self.Folderfiles(self.model_folder)
        lines=['',]
        Base_No=self.CB_FEM_No_4.currentText()
        Base_fem_file=self.Job_info[9]+'_'+self.Job_info[10]+'_CPL_'+Base_No+'.inp'
        New_fem_file=self.Job_info[9]+'_'+self.Job_info[10]+'_CPL_'+"{:0>3d}".format(int(CPL_files[-1])+1)+'.inp'
        if Base_No!='000':
            if os.path.exists(self.model_folder+Base_fem_file)==True:
                with open(self.model_folder+Base_fem_file,'r') as f:
                    lines+=f.readlines()
        with open(self.model_folder+New_fem_file,'w') as f:
            for line in lines:
                f.write(line)


        FEM_files,Ass1_files,Ass2_files,Steps_files,CPL_files=self.Folderfiles(self.model_folder)
        self.CB_FEM_No_4.clear()  
        self.CB_FEM_No_4.addItems(CPL_files)
        self.CB_FEM_No_4.setCurrentIndex(len(CPL_files)-1)
        self.FEM_file_name_4.setText(_translate("MainWindow", New_fem_file))
        self.CPL_file=New_fem_file  


        if Base_No=='000':
            Base_fem_file=''
        self.new_fem_info=[self.CPL_file,'CPL',user,Base_fem_file,time.ctime(),time.ctime(),user,'','']
        SQL.createrow(JM_files_db, JM_files_tabs[1], self.new_fem_info) 

    def Add_steps_file(self):
        _translate = QtCore.QCoreApplication.translate
        FEM_files,Ass1_files,Ass2_files,Steps_files,CPL_files=self.Folderfiles(self.model_folder)
        lines=['',]
        Base_No=self.CB_steps_No.currentText()
        Base_fem_file=self.Job_info[9]+'_'+self.Job_info[10]+'_Steps_'+Base_No+'.inp'
        New_fem_file=self.Job_info[9]+'_'+self.Job_info[10]+'_Steps_'+"{:0>3d}".format(int(Steps_files[-1])+1)+'.inp'
        if Base_No!='000':
            if os.path.exists(self.model_folder+Base_fem_file)==True:
                with open(self.model_folder+Base_fem_file,'r') as f:
                    lines+=f.readlines()
        with open(self.model_folder+New_fem_file,'w') as f:
            for line in lines:
                f.write(line)


        FEM_files,Ass1_files,Ass2_files,Steps_files,CPL_files=self.Folderfiles(self.model_folder)
        self.CB_steps_No.clear()  
        self.CB_steps_No.addItems(Steps_files)
        self.CB_steps_No.setCurrentIndex(len(Steps_files)-1)
        self.steps_file_name.setText(_translate("MainWindow", New_fem_file))
        self.steps_file=New_fem_file


        if Base_No=='000':
            Base_fem_file=''
        self.new_fem_info=[self.steps_file,'steps',user,Base_fem_file,time.ctime(),time.ctime(),user,'','']
        SQL.createrow(JM_files_db, JM_files_tabs[1], self.new_fem_info) 

    def job_file_recreation(self):
        MK_info_s=''
        IK_info_s=''
        MK_info=self.MK_info.toPlainText().rsplit('\n')
        for i in range(len(MK_info)):
            MK_info_s+='**'+MK_info[i]+'\n'
        MK_info_s=MK_info_s[:-1]
        IK_info=self.IK_info.toPlainText().rsplit('\n')
        for i in range(len(IK_info)):
            IK_info_s+='**'+IK_info[i]+'\n'
        IK_info_s=IK_info_s[:-1]
        placeholder='*'*40
        temp='{p}\n{MKI}\n{p}\n{IKI}\n{p}\n'.format(p=placeholder,MKI=MK_info_s,IKI=IK_info_s)
        if self.fem_file!='':
            temp+='*INCLUDE,INPUT='+self.fem_file+'\n'
        if self.Ass1_file!='':
            temp+='*INCLUDE,INPUT='+self.Ass1_file+'\n'
        if self.Ass2_file!='':
            temp+='*INCLUDE,INPUT='+self.Ass2_file+'\n'
        if self.CPL_file!='':
            temp+='*INCLUDE,INPUT='+self.CPL_file+'\n'
        if self.steps_file!='':
            temp+='*INCLUDE,INPUT='+self.steps_file
        if os.path.exists(self.model_folder+self.main_file)==False:
            with open(self.model_folder+self.main_file,'w') as f:
                f.write(temp)
        else:
            with open(self.model_folder+self.main_file,'r') as r:
                lines=r.readlines()


            original=''
            for line in lines:
                original+=line
            if temp!=original:
                with open(self.model_folder+self.main_file,'w') as f:
                    f.write(temp)
        self.Case_info_record()

    def Case_info_record(self):
        job_number=int(self.main_file[:6])
        Case_info=[job_number,self.main_file,self.fem_file,self.Ass1_file,self.Ass2_file,self.CPL_file,self.steps_file]
        l=SQL.createrow(JM_files_db,JM_files_tabs[0],Case_info)
        if l==-1:
            SQL.editrow(JM_files_db,JM_files_tabs[0],Case_info)
            print('Case_info edited')

    def new_job_file_creation(self):
        MK_info_s=''
        IK_info_s=''
        MK_info=self.New_MK_info.rsplit('\n')
        for i in range(len(MK_info)):
            MK_info_s+='**'+MK_info[i]+'\n'
        MK_info_s=MK_info_s[:-2]
        IK_info=self.New_IK_info.rsplit('\n')
        for i in range(len(IK_info)):
            IK_info_s+='**'+IK_info[i]+'\n'
        IK_info_s=IK_info_s[:-2]
        stars_holder='*'*40
        temp='{stars_holder}\n{MK_info_s}\n{stars_holder}\n{IK_info_s}\n{stars_holder}'.format(stars_holder=stars_holder,
                                                                                                                                    MK_info_s=MK_info_s,
                                                                                                                                    IK_info_s=IK_info_s) 
        #print(cwd)
        self.new_prj_folder=cwd+'Project\\'+self.New_Machine_type+'\\'+self.New_Machine+'\\'+self.New_Product+'\\'
        temp_dir=cwd+'Project\\'+self.New_Machine_type+'\\'+self.New_Machine+'\\'
        #print(temp_dir)
        os.chdir(temp_dir)
        if not os.path.exists(self.New_Product):
            os.mkdir(self.New_Product)
            os.chdir(self.new_prj_folder)
            for folder in case_structure:
                if not os.path.exists(folder):
                    os.mkdir(self.new_prj_folder+folder)
        self.new_job_folder=self.new_prj_folder+case_structure[0]+'\\'
        #print(self.new_job_folder)
        self.new_job_file=str(self.njobno)+'_'+self.New_Machine+'_'+self.New_Product+'_'+self.New_Job_type+'.inp'
        #print(self.new_job_folder+self.new_job_file)
        if os.path.exists(self.new_job_folder+self.new_job_file)==False:
            with open(self.new_job_folder+self.new_job_file,'w') as f:
                f.write(temp)
              
    def submit_job_local(self):
        job_sbm_scrp='submit_job_local.bat'
        with open(startupfolder+job_sbm_scrp,'w') as f:
            temp='cd %s\nabaqus job=%s cpus=%s int' % (self.model_folder, self.Job_info[6], cpus_number)
            f.write(temp)
        subprocess.Popen(startupfolder+job_sbm_scrp)
    
    def fld_clean(self):
        try:
            folder_cleaner.cleaner(self.model_folder)
        except:
            pass
            
    def load_odb_result(self):
        try:
            load_odb_scrp='load_odb.bat'
            with open(startupfolder+load_odb_scrp,'w') as f:
                temp='cd %s\nabaqus viewer database=%s' % (self.model_folder, self.Job_info[6])
                f.write(temp)
            subprocess.Popen(startupfolder+load_odb_scrp)
        except:
            pass
            
    def Openfolder(self,fullpath):
        subprocess.Popen(r'explorer /select,%s' % fullpath)
    
    def Opennp(self,path):
        notepadsrp='opennp_use.bat'
        try:
            with open(startupfolder+'opennp_use.bat','w') as f:
                temp='\"%s\" \"%s\"' %(notepadpath,path)
                f.write(temp)
            subprocess.Popen(startupfolder+notepadsrp)
        except:
            pass
    
    def Openhm(self,path):
        hmsrp='hm_open_model.cmf'
        
        with open(startupfolder+'openhm.bat','w') as f:
            command='-c'+startupfolder+hmsrp
            temp='\"%s\" \"%s\"' %(hmpath,command)
            f.write(temp)
        with open(startupfolder+hmsrp,'w') as f:
            temp='''*deletemodel()
        *answer(yes)
        *feinputpreserveincludefiles()
        *createstringarray(2) "Abaqus " "Standard3D "
        *feinputwithdata2("#abaqus\\abaqus", "%s",0,0,0,0,0,1,2,1,0)''' % path
            f.write(temp)
        subprocess.Popen(startupfolder+'openhm.bat')
        
    def colorfilestatus(self,path,file):
        if file=='':
            return ["background:white;",0]
        else:
            if os.path.exists(path+file)==True:
                return ["background:green;",1]
            else:
                return ["background:red;",0]
            
    def ReadComment(self,file,bkw,ekw,start_cursor,mode=0):
        #mode=1 read a line, mode=0 read lines
        comment=''
        readflag=0
        with open(file,'r') as r:
            for line in r:
                if readflag==1:
                    if ekw in line:
                        if mode==1:
                            comment=line[start_cursor:].rstrip('\n')
                        else:
                            break
                    else:
                        line=line[start_cursor:]
                        if mode==0:
                            comment+=line
                if bkw in line:
                    readflag=1       
        return comment  

    def Folderfiles(self,folder):
        FEM_files=['000',]
        Ass1_files=['000',]
        Ass2_files=['000',]
        Steps_files=['000',]
        CPL_files=['000',]


        files=os.listdir(folder)
        for file in files:
            if 'FEM' in file:
                FEM_files.append("{:0>3d}".format(int(FEM_files[-1])+1))
            elif 'Ass1' in file:
                Ass1_files.append("{:0>3d}".format(int(Ass1_files[-1])+1))
            elif 'Ass2' in file:
                Ass2_files.append("{:0>3d}".format(int(Ass2_files[-1])+1))
            elif 'Steps' in file:
                Steps_files.append("{:0>3d}".format(int(Steps_files[-1])+1)) 
            elif 'CPL' in file:
                CPL_files.append("{:0>3d}".format(int(CPL_files[-1])+1)) 
        return FEM_files,Ass1_files,Ass2_files,Steps_files,CPL_files

    def ReadInclude(self,mainfile):
        Includes=[]
        with open(mainfile,'r') as f:
            lines=f.readlines()
            for line in lines:
                line=line.rstrip()
                if '*INCLUDE,INPUT=' in line:
                    Includes.append(line[15:])
        Icl_flags=[-1,-1,-1,-1,-1,-1]
        '''check_exist=['model_folder','main_file','fem_file','Ass1_file','Ass2_file','CPL_file','steps_file','result_file']'''
        for i in Includes:
            if 'FEM' in i:
                Icl_flags[0]=Includes.index(i)
                self.exist_status['fem_file']=i[-7:-4]
            elif 'Ass1' in i:
                Icl_flags[1]=Includes.index(i)
                self.exist_status['Ass1_file']=i[-7:-4]
            elif 'Ass2' in i:
                Icl_flags[2]=Includes.index(i)
                self.exist_status['Ass2_file']=i[-7:-4]
            elif 'CPL' in i:
                Icl_flags[3]=Includes.index(i)
                self.exist_status['CPL_file']=i[-7:-4]
            elif 'Steps' in i:
                Icl_flags[4]=Includes.index(i)
                self.exist_status['steps_file']=i[-7:-4]
        return Includes,Icl_flags

    def Include_CB_load(self):
        FEM_files,Ass1_files,Ass2_files,Steps_files,CPL_files=self.Folderfiles(self.model_folder)
        FEM_files.pop(0)
        Ass1_files.pop(0)
        Ass2_files.pop(0)
        Steps_files.pop(0)
        CPL_files.pop(0)


        self.CB_FEM_No.addItems(FEM_files)
        if self.exist_status['fem_file']!=0:
            for j in FEM_files:
                if self.exist_status['fem_file']==str(j):
                    self.CB_FEM_No.setCurrentIndex(FEM_files.index(j))
        else:
            self.CB_FEM_No.clear()
            self.fem_file=''


        self.CB_FEM_No_2.addItems(Ass1_files)
        if self.exist_status['Ass1_file']!=0:
            for j in Ass1_files:
                if self.exist_status['Ass1_file']==j:
                    self.CB_FEM_No_2.setCurrentIndex(Ass1_files.index(j))
        else:
            self.CB_FEM_No_2.clear()
            self.Ass1_file=''


        self.CB_FEM_No_3.addItems(Ass2_files)
        if self.exist_status['Ass2_file']!=0:
            for j in Ass2_files:
                if self.exist_status['Ass2_file']==j:
                    self.CB_FEM_No_3.setCurrentIndex(Ass2_files.index(j))
        else:
            self.CB_FEM_No_3.clear()
            self.Ass2_file=''


        self.CB_FEM_No_4.addItems(CPL_files)
        if self.exist_status['CPL_file']!=0:
            for j in CPL_files:
                if self.exist_status['CPL_file']==j:
                    self.CB_FEM_No_4.setCurrentIndex(CPL_files.index(j))
        else:
            self.CB_FEM_No_4.clear()
            self.CPL_file=''


        self.CB_steps_No.addItems(Steps_files)
        if self.exist_status['steps_file']!=0:
            for j in Steps_files:
                if self.exist_status['steps_file']==j:
                    self.CB_steps_No.setCurrentIndex(Steps_files.index(j))
        else:
            self.CB_steps_No.clear()
            self.steps_file=''
    
    def load_dgn_img(self):
        _translate = QtCore.QCoreApplication.translate
        pic_folder=self.model_folder+'Img\\'
        pic_types=['jpg','png']
        #print(self.sender().text())
        if self.sender().text()=='>':
            step=1
        else:
            step=-1
        #print(step)
        files_raw=os.listdir(pic_folder)
        files=[]
        for img in files_raw:
            if 'pre' in img:
                if str(self.Job_info[0]) in img:
                    if os.path.splitext(pic_folder+img)[-1]!='.avi':
                        files.append(img)

        #print(files)   
        Total_pics=len(files)
        if Total_pics>0:
            self.img_no+=step
            if self.img_no==Total_pics:
                self.img_no=0
            if self.img_no<0:
                self.img_no=Total_pics-1
            #print(self.img_no)
            pic_to_show=pic_folder+files[self.img_no]
            #print(files[self.img_no].split('.'))
            if files[self.img_no].split('.')[1] in pic_types:
                self.design_feature_label.setPixmap(QPixmap(pic_to_show).scaled(self.design_feature_label.size(), 
                    QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
            elif files[self.img_no].split('.')[1]=='gif':
                self.movie=QtGui.QMovie(pic_to_show)
                self.movie.setCacheMode(QtGui.QMovie.CacheAll)
                self.movie.setScaledSize(self.design_feature_label.size())
                self.design_feature_label.setMovie(self.movie)
                self.movie.start()
            pic_number='%s/%s' % (str(self.img_no+1),len(files))
            self.design_feature_nb_label.setText(_translate("MainWindow", pic_number))
        else:
            self.design_feature_label.setText(_translate("MainWindow", "No design feature record"))
        
    def load_post_img(self):
        _translate = QtCore.QCoreApplication.translate
        pic_folder=self.model_folder+'Img\\'
        pic_types=['jpg','png']
        #print(self.sender().text())
        if self.sender().text()=='>':
            step=1
        else:
            step=-1
        #print(step)
        files_raw=os.listdir(pic_folder)
        files=[]
        for img in files_raw:
            if 'post' in img:
                if str(self.Job_info[0]) in img:
                    if os.path.splitext(pic_folder+img)[-1]!='.avi':
                        files.append(img)
        #print(files)   
        Total_pics=len(files)
        if Total_pics>0:
            self.img_no_post+=step
            if self.img_no_post==Total_pics:
                self.img_no_post=0
            if self.img_no_post<0:
                self.img_no_post=Total_pics-1
            #print(self.img_no)
            pic_to_show=pic_folder+files[self.img_no_post]
            #print(files[self.img_no].split('.'))
            if files[self.img_no_post].split('.')[1] in pic_types:
                self.post_info_label.setPixmap(QPixmap(pic_to_show).scaled(self.post_info_label.size(), 
                    QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
            elif files[self.img_no_post].split('.')[1]=='gif':
                self.movie=QtGui.QMovie(pic_to_show)
                self.movie.setCacheMode(QtGui.QMovie.CacheAll)
                self.movie.setScaledSize(self.post_info_label.size())
                self.post_info_label.setMovie(self.movie)
                self.movie.start()
            pic_number='%s/%s' % (str(self.img_no_post+1),len(files))
            self.post_info_nb_label.setText(_translate("MainWindow", pic_number))
        else:
            self.post_info_label.setText(_translate("MainWindow", "No post info record"))

    def Readcase(self):
        _translate = QtCore.QCoreApplication.translate
        self.Initialization()
            
        for i in check_exist:
            self.exist_status[i]=0
        if self.Job_edit_btn_status=='save':
           self.Job_edit_btn_status='edit' 
        self.Job_edit_btn.setText(_translate("MainWindow", "Edit"))


        Job_number=self.Job_number_input.toPlainText()
        #self.Job_info=[]
        #self.Job_info=SQL.readrow(JM_database,'Job_list',Job_number)
        try:
            self.Job_info=tuple(SQL.readrow(JM_database,'Job_list',int(Job_number)))
            #print('Job info read from database:',self.Job_info)
            print('Job info of %s read from database' % self.Job_info[0])
        except:
            self.Job_info=[]
        #Put job info into display
        if self.Job_info!=[]:
            self.label_JNo.setText(_translate("MainWindow", str(self.Job_info[0])))
            self.label_Jbase.setText(_translate("MainWindow", str(self.Job_info[1])))
            self.label_Juser.setText(_translate("MainWindow", self.Job_info[2]))
            self.label_Jcreation.setText(_translate("MainWindow", str(self.Job_info[3])))
            self.label_Jedit.setText(_translate("MainWindow", str(self.Job_info[4])))
            self.label_Jtype.setText(_translate("MainWindow", self.Job_info[5]))
            self.label_Jname.setText(_translate("MainWindow", self.Job_info[6]))
            self.label_Jmark.setText(_translate("MainWindow", self.Job_info[7]))
            Job_folder=cwd+'Project\\'+self.Job_info[8]+'\\'+self.Job_info[9]+'\\'+self.Job_info[10]+'\\'
            self.MK_info.setText(_translate("MainWindow", str(self.Job_info[11])))
            self.IK_info.setText(_translate("MainWindow", str(self.Job_info[12])))
            self.editable_flag=1
            
            #Read comment and model info
            self.model_folder=Job_folder+case_structure[0]+'\\'
            report_folder=Job_folder+case_structure[1]+'\\'
            if os.path.exists(self.model_folder)==True:
                try:
                    
                    self.load_dgn_img()
                    self.design_feature_next_btn.clicked.connect(self.load_dgn_img)
                    self.design_feature_bf_btn.clicked.connect(self.load_dgn_img)
                except:
                    pass
                
                try:

                    self.load_post_img()
                    self.post_info_next_btn.clicked.connect(self.load_post_img)
                    self.post_info_bf_btn.clicked.connect(self.load_post_img)
                except:
                    pass
                    
                try:
                    self.job_file_add.clicked.connect(self.submit_job_local)
                    self.pushButton.clicked.connect(self.fld_clean)
                    self.av_result.clicked.connect(self.load_odb_result)
                except:
                    pass

                self.exist_status['model_folder']=1
                self.main_file=Job_number+'_'+self.Job_info[9]+'_'+self.Job_info[10]+'_'+self.Job_info[5]+'.inp'
                Mcomment=''
                Icomment=''
                result_file=''
                if os.path.exists(self.model_folder+self.main_file)==True:
                    files,flags=self.ReadInclude(self.model_folder+self.main_file)
                    if flags[0]!=-1:
                       self.fem_file=files[flags[0]] 
                    if flags[1]!=-1:
                       self.Ass1_file=files[flags[1]] 
                    if flags[2]!=-1:
                       self.Ass2_file=files[flags[2]] 
                    if flags[3]!=-1:
                       self.CPL_file=files[flags[3]]
                    if flags[4]!=-1:
                       self.steps_file=files[flags[4]]


                    self.Include_CB_load()
                    #self.iteration_list_load()
                    



                    Mcomment_header='****************Master_key_Info*****************'
                    Icomment_header='***************Iteration_key_Info***************'
                    Include_header='INCLUDE File'
                    Steps_header='*INCLUDE='
                    comment_tail='**********************END***********************'
                    Mcomment=self.ReadComment(self.model_folder+self.main_file,Mcomment_header,comment_tail,2)
                    Icomment=self.ReadComment(self.model_folder+self.main_file,Icomment_header,comment_tail,2)
                    #self.fem_file=self.ReadComment(self.model_folder+self.main_file,Include_header,'FEM',9,1)
                    #self.steps_file=self.ReadComment(self.model_folder+self.main_file,Steps_header,'Steps',9,1)
                    result_file=self.main_file[:-4]+'.odb'
                else:
                    self.Status_bar.setText("Main file is invalid, please check")
                    
                self.Job_name_text.setText(_translate("MainWindow", self.main_file))
                self.FEM_file_name.setText(_translate("MainWindow", self.fem_file))
                self.FEM_file_name_2.setText(_translate("MainWindow", self.Ass1_file))
                self.FEM_file_name_3.setText(_translate("MainWindow", self.Ass2_file))
                self.FEM_file_name_4.setText(_translate("MainWindow", self.CPL_file))
                self.steps_file_name.setText(_translate("MainWindow", self.steps_file))
                self.result_file_name.setText(_translate("MainWindow", result_file))   


                try:
                    self.FEM_file_info.setText(_translate("MainWindow", self.ReadIncludeCmt(JM_files_db, JM_files_tabs[1], self.fem_file)))
                except:
                    self.FEM_file_info.setText(_translate("MainWindow", ''))
                try:
                    self.FEM_file_info_2.setText(_translate("MainWindow", self.ReadIncludeCmt(JM_files_db, JM_files_tabs[1], self.Ass1_file)))
                except:
                    self.FEM_file_info_2.setText(_translate("MainWindow", ''))
                try:
                    self.FEM_file_info_3.setText(_translate("MainWindow", self.ReadIncludeCmt(JM_files_db, JM_files_tabs[1], self.Ass2_file)))
                except:
                    self.FEM_file_info_3.setText(_translate("MainWindow", ''))
                try:
                    self.FEM_file_info_4.setText(_translate("MainWindow", self.ReadIncludeCmt(JM_files_db, JM_files_tabs[1], self.CPL_file)))
                except:
                    self.FEM_file_info_4.setText(_translate("MainWindow", ''))
                try:
                    self.steps_file_info.setText(_translate("MainWindow", self.ReadIncludeCmt(JM_files_db, JM_files_tabs[1], self.steps_file)))
                except:
                    self.steps_file_info.setText(_translate("MainWindow", ''))




                #print(self.model_folder,self.Ass1_file)   
                self.Job_file_status.setStyleSheet(self.colorfilestatus(self.model_folder,self.main_file)[0])
                if self.colorfilestatus(self.model_folder,self.main_file)[1]==1:
                    #self.exist_status['main_file']=1
                    self.np_job_name.clicked.connect(self.mainfilenpSignal)
                    self.hm_job_name.clicked.connect(self.mainfilehmSignal)
                    self.job_file_folder.clicked.connect(self.mainfilefolderSignal)
                     
                self.fem_file_status.setStyleSheet(self.colorfilestatus(self.model_folder,self.fem_file)[0])
                if self.colorfilestatus(self.model_folder,self.fem_file)[1]==1:
                    #self.exist_status['fem_file']=1
                    self.np_fem.clicked.connect(self.femfilenpSignal)
                    self.hm_fem.clicked.connect(self.femfilehmSignal)
                    self.fem_file_folder.clicked.connect(self.femfilefolderSignal)


                self.fem_file_status_2.setStyleSheet(self.colorfilestatus(self.model_folder,self.Ass1_file)[0])
                if self.colorfilestatus(self.model_folder,self.Ass1_file)[1]==1:
                    #self.exist_status['Ass1_file']=1
                    self.np_fem_2.clicked.connect(self.Ass1filenpSignal)
                    self.hm_fem_2.clicked.connect(self.Ass1filehmSignal)
                    self.fem_file_folder_2.clicked.connect(self.Ass1filefolderSignal)


                self.fem_file_status_3.setStyleSheet(self.colorfilestatus(self.model_folder,self.Ass2_file)[0])
                if self.colorfilestatus(self.model_folder,self.Ass2_file)[1]==1:
                    #self.exist_status['Ass2_file']=1
                    self.np_fem_3.clicked.connect(self.Ass2filenpSignal)
                    self.hm_fem_3.clicked.connect(self.Ass2filehmSignal)
                    self.fem_file_folder_3.clicked.connect(self.Ass2filefolderSignal)


                self.fem_file_status_4.setStyleSheet(self.colorfilestatus(self.model_folder,self.CPL_file)[0])
                if self.colorfilestatus(self.model_folder,self.CPL_file)[1]==1:
                    #self.exist_status['CPL_file']=1
                    self.np_fem_4.clicked.connect(self.CPLfilenpSignal)
                    #self.hm_fem_4.clicked.connect(self.CPLfilehmSignal)
                    self.fem_file_folder_4.clicked.connect(self.CPLfilefolderSignal)
                      
                self.steps_file_status.setStyleSheet(self.colorfilestatus(self.model_folder,self.steps_file)[0])
                if self.colorfilestatus(self.model_folder,self.steps_file)[1]==1:
                    #self.exist_status['steps_file']=1
                    self.np_steps.clicked.connect(self.stepsfilenpSignal)
                    self.hm_steps.clicked.connect(self.stepsfilehmSignal)
                    self.steps_file_folder.clicked.connect(self.stepsfilefolderSignal)
                      
                self.result_file_status.setStyleSheet(self.colorfilestatus(self.model_folder,result_file)[0])
                if self.colorfilestatus(self.model_folder,result_file)[1]==1:
                    self.exist_status['result_file']=1
                #print(self.exist_status)
                self.Status_bar.setText("Job is loaded")
                  
                
            else:
                self.Status_bar.setText("Job folder is invalid, please check")
                
            self.Readprjs()
            self.iteration_list_load()
            self.Product_CB.currentIndexChanged.connect(self.iteration_list_load)
            
        else:
            reply = QMessageBox.warning(self, 'Warning',"The Job number is not valid",QMessageBox.Ok)
            self.Initialization()
            self.Status_bar.setText("Open failed")
                   
    #close event, will be activate after the prj is finish    
    def closeEvent(self,  event):
        reply = QMessageBox.question(self,  'Message', 
        "Are you sure to quit?",  QMessageBox.Yes,  QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
            
if __name__ == "__main__":
    try:
        folder_check()
    except:
        pass
    app = QApplication(sys.argv)
    window = Main()
    _translate = QtCore.QCoreApplication.translate
    window.setWindowTitle("Job Manager      User : %s" % user)
    window.show()
    sys.exit(app.exec_())

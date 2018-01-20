'''
Created on Dec 17, 2017

@author: rabbitfj
'''

import sqlite3
import sys
import os

JM_database=r'c:\Job_Manager\data\Jobs_data.db'
JM_database_tabs=['Job_list','Project_list']
JM_files_db=r'c:\Job_Manager\data\Files_data.db'
JM_files_tabs=['Case_info','Include_info']


def Initiation():
    if not os.path.exists(database_dir):
        with open(database_dir,'w') as f:
            pass
    con=sqlite3.connect(database_dir)
    with con:
        cur=con.cursor()
        try:
            cur.execute("create table Job_list(job_number int primary key,base_on int,created_by str,created_on str,last_edit str,job_type str,job_name str,job_mark_ str,Machine_type str, Machine str,Product str,MK_info str,IK_info str,Access_flag str)")
            cur.execute("create table Project_list(Platform str,Machine_type str,Machine str primary key,Product str)")
        except:
            pass
        #cur.execute("insert into Job_list values(180000,0,'','','','','','','','','','','','')")

    if not os.path.exists(files_db):
        with open(files_db,'w') as f:
            pass
    con=sqlite3.connect(files_db)
    with con:
        cur=con.cursor()
        try:
            cur.execute("create table Case_info(job_number int primary key,main_file str,fem_file str,Ass1_file str,Ass2_file str,CPL_file str,steps_file str,Access_flag str)")
            cur.execute("create table Include_info(Include_name str primary key,user str,base_on str,type str,created_on str,edit_on str,edit_by str,comment str,flag_1 str)")
        except:
            pass
#Initiation()     
def showtabs(path):
    if os.path.exists(path):
        con=sqlite3.connect(path)
        with con:
            cur=con.cursor()
            try:
                cur.execute("select name from sqlite_master where type='table'")
                tabs=cur.fetchall()
                for tab in tabs:
                    print(tab)
            except:
                print('Database is not valid')
#showtabs(database_dir)
def createtab(path,tab,cols):
    if os.path.exists(path):
        con=sqlite3.connect(path)
        with con:
            cur=con.cursor()
            try:
                command='create table %s' % tab
                command+=cols+'\''
                cur.execute(command)
            except:
                print('Tab is already exist')
                
       
def printall(path,tab):
     if os.path.exists(path):
        con=sqlite3.connect(path)
        with con:
            cur=con.cursor()
            try:
                cur.execute("select * from %s" % tab)
                rows=cur.fetchall()
                for row in rows:
                    print(row)
            except:
                print('Tab is not valid')

def readrow(path,tab,key):
    if os.path.exists(path):
        con=sqlite3.connect(path)
        with con:
            cur=con.cursor()
            try:
                cur.execute("select * from %s" % tab)
                while True:
                    row_data=cur.fetchone()
                    if row_data[0]==key:
                        data=list(row_data)
                        data[9]=str(data[9])
                        row_data=tuple(data)
                        return data
                        break
                    if row_data==None:
                        return 'Not found %s in %s' % (key,tab)
                        break
            except:
                print('Given Job/Tab name is invalid')
    else:
        print('Given database is invalid')
#print(readrow(database_dir,'Job_list',170003))

def readrow_s(path,tab,key):
    if os.path.exists(path):
        con=sqlite3.connect(path)
        with con:
            cur=con.cursor()
            try:
                cur.execute("select * from %s" % tab)
                while True:
                    row_data=cur.fetchone()
                    if row_data[0]==key:
                        data=list(row_data)
                        row_data=tuple(data)
                        return data
                        break
                    if row_data==None:
                        return 'Not found %s in %s' % (key,tab)
                        break
            except:
                pass
                #print('Given Job/Tab name is invalid')
    else:
        pass
        #print('Given database is invalid')

def readrows(path,tab):
    if os.path.exists(path):
        con=sqlite3.connect(path)
        with con:
            cur=con.cursor()
            try:
                cur.execute("select * from %s" % tab)
                rows=cur.fetchall()
            except:
                print('Tab is not valid')
    return rows

def columns(path,tab):
    if os.path.exists(path):
        con=sqlite3.connect(path)
        with con:
            cur=con.cursor()
            cur.execute('select * from %s' % tab)
            return len(cur.description)

def printcolumns(path,tab):
    if os.path.exists(path):
        con=sqlite3.connect(path)
        with con:
            cur=con.cursor()
            cur.execute('select * from %s' % tab)
            # for des in cur.description:
            #     print(des[0])
            return cur.description[0][0]

def createrow(path,tab,row):
    if os.path.exists(path):
        con=sqlite3.connect(path)
        with con:
            cur=con.cursor()
            try:
                temp='(?'
                cols=columns(path,tab)
                if len(row)<cols:
                    j=cols-len(row)
                    for i in range(j):
                        row.append(None)
                temp+=',?'*(cols-1)
                temp+=')'
                command='insert into %s values' % tab 
                command+=temp
                cur.execute(command,row)
                return 1
            except:
                print('The Job is already in database')
                return -1



def edititem(path,tab,id,key,item):
    if os.path.exists(path):
        con=sqlite3.connect(path)
        with con:
            cur=con.cursor()
            try:
                command='update %s set %s=? where job_number=?' % (tab,key)
                cur.execute(command,(item,id))
            except:
                print('job_number is invalid')
#SQL_edititem(database_dir,'Job_list',170003,'base_on',170002)

def editrow(path,tab,row):
    head=printcolumns(path,tab)
    #print(head)
    row.append(row[0])
    row.pop(0)
    if os.path.exists(path):
        con=sqlite3.connect(path)
        with con:
            cur=con.cursor()
            cur.execute('select * from %s' % tab)
            col_names=[cn[0] for cn in cur.description]
            command='update %s set ' % tab
            for i in range(1,len(col_names)):
                command+='%s=?, ' % col_names[i]
            command=command[:-2]
            command+=' where %s=?' % head
            #print(command)
            #print(row)
            try:
                cur.execute(command,row)
            except:
                pass
                #print('job_number is invalid')

def replacerow(path,tab,row):
    head=printcolumns(path,tab)
    if os.path.exists(path):
        con=sqlite3.connect(path)
        with con:
            cur=con.cursor()
            cur.execute('select * from %s' % tab)
            col_names=[cn[0] for cn in cur.description]
            command='update %s set ' % tab
            for i in range(1,len(col_names)):
                command+='%s=?, ' % col_names[i]
            command=command[:-2]
            command+=' where %s=?' % head
            #print(command)
            try:
                cur.execute(command,row)
            except:
                print('%s is invalid' % head)    

def newjobnum(path,tab):
    key='Job_number'
    if os.path.exists(path):
        con=sqlite3.connect(path)
        with con:
            cur=con.cursor()
            try:
                cur.execute('select Job_number from %s' % tab)
                numbers=cur.fetchall()
                new_number=numbers[-1][0]+1
                return new_number
            except:
                print('Tab name is invalid')
#newjobnum(database_dir, 'Job_list')

def newPrjnum(path,tab):
    key='Number'
    if os.path.exists(path):
        con=sqlite3.connect(path)
        with con:
            cur=con.cursor()
            try:
                cur.execute('select Number from %s' % tab)
                numbers=cur.fetchall()
                new_number=numbers[-1][0]+1
                return new_number
            except:
                print('Tab name is invalid')

if __name__=='__main__':
    #test=['330K_C_pkg_FEM_005.inp', 'fem', 'rabbitfj', '330K_C_pkg_FEM_004.inp', 'Mon Jan  1 16:03:38 2018', 'Mon Jan  1 16:03:38 2018', 'rabbitfj', '111', '']
    #print(columns(database_dir,'Job_list'))
    #print(printcolumns(files_db,'Include_info'))
    #Initiation()
    #editrow(JM_files_db,JM_files_tabs[1],test)
    printall(JM_files_db,JM_files_tabs[1])
    #print(printcolumns(JM_files_db,JM_files_tabs[0]))
    #printall(JM_database,JM_database_tabs[0])
    
    #test='330K_C_pkg_FEM_005.inp'
    #print(readrow_s(JM_files_db, JM_files_tabs[1], test))
    #
    # test=[180002, 180001, 'rabbitfj', 'Mon Jan  1 19:15:17 2018', 'Mon Jan  1 19:15:20 2018', 'Gload', '180002_330K_C_pkg_Gload', 'Ongoing', 'HEX', '330K', 'C_pkg', '111', '111', None]
    # editrow(JM_database, JM_database_tabs[0], test)
    # printall(JM_database, JM_database_tabs[0])
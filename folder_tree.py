import os
import sqlite3
'''
folder_tree=[platform,machine_type,machine,product,job_files]
job_file_folder=[Inp&Res,Reports,CAD]
'''

# def folder_creation(case,case_structure):
#     global case_wd 
#     os.chdir(cwd)
#     tempdir=cwd
#     for i in range(len(case)):
#         if not os.path.exists(str(case[i])):
#             os.mkdir(str(case[i]))
#     tempdir+=str(case[i])+'\\'
#     os.chdir(tempdir)
#     if case[i]==case[-1]:
#         for folder in case_structure:
#             if not os.path.exists(folder):
#                 os.mkdir(tempdir+folder)
    
def folder_creation(case,case_structure):
    global case_wd 
    os.chdir(cwd)
    tempdir=cwd
    for i in range(len(case)):
        if not os.path.exists(str(case[i])):
            os.mkdir(str(case[i]))
        tempdir+=str(case[i])+'\\'
        os.chdir(tempdir)
        if case[i]==case[-1]:
            for folder in case_structure:
                if not os.path.exists(folder):
                    os.mkdir(tempdir+folder)    
cwd='d:\\JM\\'
JM_database=r'D:\Job_Manager\data\database.db'
case_structure=['Inp&Res','Reports','CAD']
con=sqlite3.connect(JM_database)
with con:
    cur=con.cursor()
    cur.execute('select * from Project_list')
    values=cur.fetchall()
    cases=[list(each) for each in values]
    for case in cases:
        case[0]='Project'
        print(case)
        folder_creation(case,case_structure)         
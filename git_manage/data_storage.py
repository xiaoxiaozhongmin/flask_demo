# -*- coding: utf-8 -*-
import sqlite3
import mytool

@mytool.singleton
class mysqlcls:
    databases=[]
    def __init__(self,database_name):
        print("create_mysqlcls")
        self.database_name=database_name
        self.conn = sqlite3.connect(str(database_name) + '.db', check_same_thread=False)
        self.create_table()
        self.databases.append(database_name)

    def create_table(self):
        if self.create_user_table():
            self.create_project_table()
            self.create_access_table()

    def create_user_table(self):
        print("create_user_table")
        sql = "SELECT COUNT(*) FROM sqlite_master where type='table' and name='users'"
        cursor = self.conn.execute(sql)
        if list(cursor) == [(0,)]:
            self.conn.execute('''CREATE TABLE users (ID INTEGER PRIMARY KEY AUTOINCREMENT,U_ID INT NOT NULL,U_NAME TEXT NOT NULL);''')
            self.conn.commit()
            print("create project user")
            self.conn.execute('''CREATE TABLE groups (ID INTEGER PRIMARY KEY AUTOINCREMENT,G_ID INT NOT NULL,G_NAME TEXT NOT NULL);''')
            self.conn.commit()
            self.conn.execute('''CREATE TABLE groupsproject (ID INTEGER PRIMARY KEY AUTOINCREMENT,G_ID INT NOT NULL,P_ID INT NOT NULL);''')
            self.conn.commit()
            print("create project user")
            return True
        return False

    def create_project_table(self):
        print("create_project_table")
        sql = "SELECT COUNT(*) FROM sqlite_master where type='table' and name='projects'"
        cursor = self.conn.execute(sql)
        if list(cursor) == [(0,)]:
            self.conn.execute('''CREATE TABLE projects
                   (
                   ID INTEGER PRIMARY KEY AUTOINCREMENT,
                   P_ID INT NOT NULL,
                   P_NAME TEXT NOT NULL,
                   URL TEXT NOT NULL,
                   USER_PROJECT INT NOT NULL
                    );'''
                              )
            self.conn.commit()
            print("create project table")

    def create_access_table(self):
        print('create_access_table')
        sql = "SELECT COUNT(*) FROM sqlite_master where type='table' and name='accesses'"
        cursor = self.conn.execute(sql)
        if list(cursor) == [(0,)]:
            self.conn.execute('''CREATE TABLE accesses 
                   (
                   ID INTEGER PRIMARY KEY AUTOINCREMENT,
                   P_ID INT NOT NULL,
                   U_ID INT NOT NULL,
                   access TEXT NOT NULL,
                   expires_at TEXT 
                    );'''
                              )
            self.conn.commit()
            print("create project table")

    def execute_sql(self,sql):
        print('execute_sql',sql)
        cursor=self.conn.execute(sql)
        self.conn.commit()
        return list(cursor)

    def close(self):
        print("close database")
        self.conn.close()



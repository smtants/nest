#!/usr/bin python
# -*- coding:utf-8 -*-

import os,sys
import mysql.connector as mariadb
from smtants.nest.include import log

class MariaDB:

    def __init__(self, host, port, user, password, database, charset):
        #   initiate config file
        self.host     = host
        self.port     = port
        self.user     = user
        self.password = password
        self.database = database
        self.charset  = charset
        
    # open a connection
    # @return   connection object
    def open(self):
        try:
            conn = mariadb.connect(
                host=self.host, 
                port=self.port, 
                user=self.user, 
                password=self.password, 
                database=self.database, 
                charset=self.charset)
        except Exception as e:
            log.lg_write_mariadb(str(e))
            sys.exit()
        return conn

    # check the sql syntax
    # @para    sql    sql statement
    # @return  sql
    def check_sql(self,sql):
        #   delete ";"
        sql = str(sql).replace(';','')
        return sql
    
    # query all
    # @para    sql    sql statement
    # @return  data
    def query(self,sql):
        conn = self.open()
        curs = conn.cursor()
        sql  = self.check_sql(sql)
        data = []
        try:
            curs.execute(sql)
            data = curs.fetchall()
        except Exception as e:
            log.lg_write_mariadb(" ==query== " + str(sql) + " == " + str(e))
            sys.exit(-1)
        conn.close()
        return data

    # execute sql
    # @para    sql    sql statement
    # @return  count  affect the number of rows
    def execute(self,sql):
        conn = self.open()
        curs = conn.cursor()
        sql  = self.check_sql(sql)
        isOk = False
        try:
            curs.execute(sql)
            conn.commit()
            isOk = True
        except Exception as e:
            log.lg_write_mariadb(" ==execute== " + str(sql) + " == " + str(e))
            conn.rollback()
            sys.exit(-1)
        conn.close()
        return isOk
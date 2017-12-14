#!/usr/bin python 
# -*- coding: utf-8 -*-
#
#   client to mariadb库
#   xianwen.zhang
#   2017-11-07

import os
import json
from smtants.nest.include import log        
from smtants.nest.libs import mariadb  

# 连接mariadb服务器
# @param    host
# @param    port 
# @param    user
# @param    password
# @param    database
# @param    charset
# @return   MariaDB实例对象
def init(database):
    if not os.path.exists('cfg.json'):
        log.lg_write_nest(' ==mariadbclass.init== cfg.json file is not exists !')
        exit()

    f = open('cfg.json',encoding='utf-8') 
    data = json.load(f)

    try:
        return conn(
            data['mariadb']['host'], 
            data['mariadb']['port'], 
            data['mariadb']['username'], 
            data['mariadb']['password'], 
            database, 
            data['mariadb']['charset']
        )
    except Exception as e:
        log.lg_write_mariadb(' ==init== ' + str(e))
        exit()

def conn(host, port, user, password, database, charset):
     return mariadb.MariaDB(host, port, user, password, database, charset)

if __name__ == "__main__":
    init('ops_nest')

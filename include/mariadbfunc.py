#!/usr/bin python 
# -*- coding: utf-8 -*-
#
#   mariadb function库
#   xianwen.zhang
#   2017-12-28

import os
import json
from smtants.nest.include import log 
from smtants.nest.include import mariadbclient

mariadbclient = mariadbclient.init()

def execute(sql):
    isOk = False
    try:
        isOk = mariadbclient.execute(sql)
    except Exception as e:
        log.lg_write_nest(" ==mariadbfunc.execute== " + str(e))
    return isOk

# check endpoint is exists and add endpoint
# @return  bool
# 
def endpoint_exists(endpoint):
    isOk = False
    try:
        sql = 'select count(1) from ops_endpoints where endpoint="' + endpoint + '"'
        if  mariadbclient.query(sql)[0][0] < 1:
            sql = "insert into ops_endpoints (endpoint,createdate) values('"
            sql += str(endpoint) + "'," 
            sql += "unix_timestamp(now()))"
            mariadbclient.execute(sql)
        isOk = True
    except Exception as e:
        log.lg_write_nest(" ==mariadbfunc.endpoint_exists== " + str(e))
    return isOk

# get endpoint 
# @return  endpoint
# 
def get_endpoint_id(endpoint):
        endpointId = 0
        try:
            isOk = endpoint_exists(endpoint)
            if isOk:
                sql = 'select id from ops_endpoints where endpoint="' + endpoint + '"'
                if  mariadbclient.query(sql)[0][0] > 0:
                    endpointId = mariadbclient.query(sql)[0][0]
        except Exception as e:
            log.lg_write_nest(" ==mariadbfunc.get_endpoint_id== " + str(e))
        return endpointId

# check items is exists and add item
# @return  bool
# 
def item_exists(endpointId, itemName):
    isOk = False
    try:
        sql = 'select count(1) from ops_items where endpointid=' + str(endpointId) + ' and name="' + str(itemName) + '"'
        if  mariadbclient.query(sql)[0][0] < 1:
            sql = 'insert into ops_items (endpointid,name) values('
            sql += str(endpointId) + ',"' 
            sql += str(itemName) + '")'
            mariadbclient.execute(sql)
        isOk = True
    except Exception as e:
        log.lg_write_nest(" ==mariadbfunc.item_exists== " + str(e))
    return isOk

# get item id
# @return  id
# 
def get_item_id(endpointId, itemName):
        try:
            isOk = item_exists(endpointId, itemName)
            itemId = 0
            if isOk:
                sql = 'select id from ops_items where endpointid=' + str(endpointId) + ' and name="' + str(itemName) + '"'
                if  mariadbclient.query(sql)[0][0] > 0:
                    itemId = mariadbclient.query(sql)[0][0]
        except Exception as e:
            log.lg_write_nest(" ==mariadbfunc.get_item_id== " + str(e))
        return itemId
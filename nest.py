#! /usr/bin python
# -*- coding:utf-8 -*-
#
#   nest
#   xianwen.zhang
#   2017-12-01

import os,time,json,demjson
import tornado.ioloop
import tornado.web
from smtants.nest.include import mariadbfunc
from smtants.nest.include import statuscode
from smtants.nest.include import log

endpointsDict = {}
itemsDict     = {}

isDebug = False

def debug(msg):
    print(msg)

class RouterConfig(tornado.web.Application):
    def route(self, url):
        def register(handler):
            self.add_handlers(".*$", [(url, handler)])
            return handler
        return register

app = RouterConfig()

@app.route(r'/v1/push')
class V1_PushHandler(tornado.web.RequestHandler):
    def post(self):
        endpoint  = ''
        value     = {}
        timestamp = ''
        step      = ''
        retJson   = {}
        try: 
            if self.get_argument('endpoint'):
                endpoint = self.get_argument('endpoint')

            if self.get_argument('value'):
                value = self.get_argument('value')

            if self.get_argument('timestamp'):
                timestamp = self.get_argument('timestamp')

            if self.get_argument('step'):
                step = self.get_argument('step')

            #   parameter cannot be empty
            if endpoint == '' or value == '' or timestamp == '' or step == '':
                retJson['res'] = statuscode.REQ_PARAM_ERROR
                return retJson
        
            #   string to json
            dataJson = demjson.decode(value)
            while True:
                if endpointsDict.get(endpoint):
                    endpointId = endpointsDict.get(endpoint)
                else:
                    endpointId = mariadbfunc.get_endpoint_id(endpoint)
                    endpointsDict[endpoint] = endpointId
                if endpointId < 1:
                    log.lg_write_nest(' ==nest.v1.push== ' + endpoint + 'endpointId get failed !')
                    break

                if len(dict(dataJson)) < 1:
                    retJson['res'] = statuscode.REQ_FORMAT_ERROR
                    break
                for key in dict(dataJson).keys():
                    if itemsDict.get(str(endpointId) + '.' + str(key)):    
                        itemId = itemsDict.get(str(endpointId) + '.' + str(key))
                    else:
                        itemId = mariadbfunc.get_item_id(endpointId, str(key))
                        itemsDict[str(endpointId) + '.' + str(key)] = itemId
                    if itemId < 1:
                        log.lg_write_nest(' ==nest.v1.push== ' + endpoint+ '.' + str(key)  + 'itemId get failed !')
                        break
                    isOk = mariadbfunc.add_history(itemId, dict(dataJson).get(key), timestamp, step)
                    
                    if not isOk:
                        log.lg_write_nest(' ==nest.v1.push== ' + endpoint + '.' + str(key) + 'add history failed !')
                        break
                
                retJson['res']  = statuscode.SUCCESS
                if isDebug:
                    debug(endpoint + " push is ok!")
                break

        except Exception as e:
            log.lg_write_nest(' ==nest.v1.push== ' + str(e))
            retJson['res'] = statuscode.API_ABNORMA

        self.write(retJson)

@app.route(r'/v1/plugin')
class V1_PluginHandler(tornado.web.RequestHandler):
    def post(self):
        endpoint  = ''
        item      = ''
        value     = ''
        timestamp = ''
        step      = ''
        retJson   = {}
        try: 
            if self.get_argument('endpoint'):
                endpoint = self.get_argument('endpoint')

            if self.get_argument('item'):
                item = self.get_argument('item')

            if self.get_argument('value'):
                value = self.get_argument('value')

            if self.get_argument('timestamp'):
                timestamp = self.get_argument('timestamp')

            if self.get_argument('step'):
                step = self.get_argument('step')

            #   parameter cannot be empty
            if endpoint == '' or item == '' or value == '' or timestamp == '' or step == '':
                retJson['res'] = statuscode.REQ_PARAM_ERROR
                return retJson

            while True:
                if endpointsDict.get(endpoint):
                    endpointId = endpointsDict.get(endpoint)
                else:
                    endpointId = mariadbfunc.get_endpoint_id(endpoint)
                    endpointsDict[endpoint] = endpointId
                if endpointId < 1:
                    log.lg_write_nest(' ==nest.v1.push== ' + endpoint + 'endpointId get failed !')
                    break

                if itemsDict.get(str(endpointId) + '.' + item):    
                    itemId = itemsDict.get(str(endpointId) + '.' + item)
                else:
                    itemId = mariadbfunc.get_item_id(endpointId, item)
                    itemsDict[(str(endpointId) + '.' + item)] = itemId
                if itemId < 1:
                    log.lg_write_nest(' ==nest.v1.push== ' + endpoint+ '.' + item  + 'itemId get failed !')
                    break

                isOk = mariadbfunc.add_history(itemId, value, timestamp, step)
                
                if not isOk:
                    log.lg_write_nest(' ==nest.v1.push== ' + endpoint + '.' + item + 'add history failed !')
                    break
                
                retJson['res']  = statuscode.SUCCESS
                break

        except Exception as e:
            log.lg_write_nest(' ==nest.v1.push== ' + str(e))
            retJson['res'] = statuscode.API_ABNORMA

        self.write(retJson)

def main():
    try:
        if not os.path.exists('cfg.json'):
            log.lg_write_nest(' ==nest.nest== cfg.json file is not exists !')
            exit()

        f = open('cfg.json',encoding='utf-8') 
        data = json.load(f)

        if not data['socket']['post']:
            log.lg_write_nest(' ==nest.nest== please enter the correct port !')
            exit()

        if data['debug']:
            isDebug = True
        
        port = data['socket']['post']

        app.listen(port)
        tornado.ioloop.IOLoop.current().start()
    except Exception as e:
        log.lg_write_nest(' ==nest.nest== ' + str(e))
        exit()

if __name__ == "__main__":
    main()
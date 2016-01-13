# coding: utf-8

import os
import sys
import urllib
import logging
import ConfigParser
import time
import thread
import win32ras

from twisted.web import proxy, http
from twisted.internet import reactor
from twisted.python import log


config = ConfigParser.ConfigParser()
config.read('./config.ini')
DIALNAME = config.get('main', 'DIALNAME')
ACCOUNT = config.get('main', 'ACCOUNT')
PASSWORD = config.get('main', 'PASSWORD')
NODE_NAME = config.get('main', 'NODE_NAME')
PORT = config.get('main', 'PORT')
DEBUG = config.get('main', 'DEBUG')

HTTP_CHANGE_STATUS_API = config.get('main', 'HTTP_CHANGE_STATUS_API')

logger = logging.getLogger('DialServer')
if DEBUG.upper().strip('\n') == 'DEBUG':
    level = logging.DEBUG
else:
    level = logging.ERROR
logging.basicConfig(level=level,
                    format='%(asctime)s %(filename)s:%(lineno)d %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='server.log',
                    filemode='w')
stream_handler = logging.StreamHandler(sys.stderr)
logger.addHandler(stream_handler)


class ProxyFactory(http.HTTPFactory):
    protocol = proxy.Proxy


class DynamicProxy(object):

    def __init__(self):
        self.pid = None

    def start_proxy(self, port=8080):
        reactor.listenTCP(port, ProxyFactory())
        reactor.run(installSignalHandlers=False)

    def dial(self, dialname, account, password):
        try:
            dial_params = (dialname, '', '', account, password, '')
            return win32ras.Dial(None, None, dial_params, None)
        except:
            time.sleep(1)
            return self.dial(dialname, account, password)

    def disdial(self, pid):
        if pid != None:
            try:
                win32ras.HangUp(pid)
                logger.info('Disconnection success!')
                self.pid = None
                return True
            except:
                logger.error(
                    'Disconnection failed, wait for 2 seconds and try again...')
                time.sleep(2)
                self.disdial(pid)
        else:
            logger.error('Cannot find the process!')
            return False

    def fetch_change(self):
        while True:
            content = ''
            try:
                uo = urllib.urlopen(
                    HTTP_CHANGE_STATUS_API + 'update?type=dynamic_http&node=%s&port=%s' % (NODE_NAME, PORT))
                content = uo.read()
                uo.close()
            except:
                logger.exception('Error response')
                if not self.pid:
                    logger.debug('Start dial...')
                    self.pid, ret = self.dial(DIALNAME, ACCOUNT, PASSWORD)
                    # print 'PID=%s, CODE=%s' % (self.pid, ret)
                    logger.info('[UPDATE REQ]PID=%s, CODE=%s' %
                                (self.pid, ret))
                else:
                    self.disdial(self.pid)

            logger.info('Checking change status')
            if 'SHOULD_UPDATE!' in content:
                if self.pid:
                    self.disdial(self.pid)
                else:
                    logger.info('No pid, so disconnect now')
                    os.system('rasdial %s /disconnect' % DIALNAME)
                    self.pid, ret = self.dial(DIALNAME, ACCOUNT, PASSWORD)
            print 'Waitting for query http content'
            time.sleep(1)



if __name__ == '__main__':
    dp = DynamicProxy()
    thread.start_new_thread(dp.start_proxy, (int(PORT),))
    thread.start_new_thread(dp.fetch_change, ())
    while True:
        time.sleep(1)

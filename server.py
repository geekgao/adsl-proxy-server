# coding: utf-8

import urllib
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
HTTP_CHANGE_STATUS_API = config.get('main', 'HTTP_CHANGE_STATUS_API')


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
            time.sleep(2)
            return self.dial(dialname, account, password)

    def disdial(self, pid):
        if pid != None:
            try:
                win32ras.HangUp(pid)
                print "Disconnection success!"
                self.pid = None
                return True
            except:
                print "Disconnection failed, wait for 2 seconds and try again..."
                time.sleep(2)
                self.disdial(pid)
        else:
            print "Can't find the process!"
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
                print 'Error response'
                if not self.pid:
                    print 'Start dial-1'
                    self.pid, ret = self.dial(DIALNAME, ACCOUNT, PASSWORD)
                    print 'PID=%s, CODE=%s' % (self.pid, ret)
                else:
                    self.disdial(self.pid)

            print 'Checking change status'
            if 'SHOULD_UPDATE!' in content:
                print 'Content:', content
                if self.pid:
                    print 'PID=%s, CODE=%s' % (self.pid, ret)
                    self.disdial(self.pid)
                else:
                    print 'Start dial-2'
                    self.pid, ret = self.dial(DIALNAME, ACCOUNT, PASSWORD)
                    print 'PID=%s, CODE=%s' % (self.pid, ret)
            print 'Waitting 1s for query http content'
            time.sleep(1)


if __name__ == '__main__':
    dp = DynamicProxy()
    thread.start_new_thread(dp.start_proxy, (int(PORT),))
    thread.start_new_thread(dp.fetch_change, ())
    while True:
        time.sleep(0.2)

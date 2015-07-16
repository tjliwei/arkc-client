import socket
import threading
import random
import string
from time import sleep

class coordinate(object):

    required = 4 #should be set by users?

    def __init__(self, ctlip, ctlport_remote, ctlport_local, localcert, remotecert):
        self.count = 0
        self.available = 0
        self.remotepub = remotecert
        self.localcert = localcert
        self.authdata = "8eac74242041e540b43ac0845683a7b761ec5b81"
        
        #TODO self.authdata = self.localcert.  get SHA1
        self.recvs = []
        #TODO: make the following string more random
        salt = list(string.ascii_letters)
        random.shuffle(salt)
        self.str = ''.join(salt[:16]) #TODO: should be used for AES in every data transmission
        self.udpsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpsock.bind(('', ctlport_local))
        self.addr = (ctlip, ctlport_remote)
        self.check = threading.Event()
        self.check.set()
        req = threading.Thread(target=self.reqconn)
        req.start()

    def newconn(self, recv):
        self.available += 1
        self.count += 1
        self.recvs.append(recv)
        if self.issufficient():
            self.check.clear()
        print("Available socket %d" % self.available)
            
    def closeconn(self):
        self.count -=1
        if self.count <0:
            self.count =0
            print("coordinate: minus count error")
        if not self.issufficient():
            self.check.set()
        print("Available socket %d" % self.available)

    def reqconn(self):
        while True:
            self.check.wait()
            self.requestdata = self.generatereq()
            self.udpsock.sendto(self.requestdata,self.addr)
            sleep(0.05)
            
    def generatereq(self):
        salt = list(string.ascii_letters)
        random.shuffle(salt)
        salt = salt[:16]
        saltstr = ''.join(salt)
        blank = saltstr + self.authdata
        blank = blank + self.localcert.encrypt(saltstr + self.str, "r")
        return self.remotepub.encrypt(blank, "r")
    
    def issufficient(self):
        return self.available >= self.required
    
    def offerconn(self):
        if self.available <=0:
            return None
        self.available -=1
        offer = self.recvs [0]
        self.recvs = self.recvs[1:]
        if not self.issufficient():
            self.check.set()
        print("Available socket %d" % self.available)
        return offer
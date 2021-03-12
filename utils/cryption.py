# -*- encoding=utf-8 -*-

import base64
import random
import time
from pyDes import *

__all__ = ['Cryption']

# attention: encrypt and decrypt only accept str, not unicode

class Cryption(object):
    global __pad, __k, __alchar, __encdict, __decdict
    __pad = 'p'
    __k = des('d3q75whv', CBC, 'woc^*d2l')
    __alchar = b'-_'
    __encdict = {
        0:['0','3','6','9','Z','X','C','V','B','N','M','q','w','e','r','t','y','u','i','o','p'],
        1:['1','4','7','A','S','D','F','G','H','J','K','L','a','s','d','f','g','h','j','k','l'],
        2:['2','5','8','Q','W','E','R','T','Y','U','I','O','P','z','x','c','v','b','n','m'],
        }
    __decdict = {
        '0':0,'3':0,'6':0,'9':0,'Z':0,'X':0,'C':0,'V':0,'B':0,'N':0,'M':0,'q':0,'w':0,'e':0,'r':0,'t':0,'y':0,'u':0,'i':0,'o':0,'p':0,
        '1':1,'4':1,'7':1,'A':1,'S':1,'D':1,'F':1,'G':1,'H':1,'J':1,'K':1,'L':1,'a':1,'s':1,'d':1,'f':1,'g':1,'h':1,'j':1,'k':1,'l':1,
        '2':2,'5':2,'8':2,'Q':2,'W':2,'E':2,'R':2,'T':2,'Y':2,'U':2,'I':2,'O':2,'P':2,'z':2,'x':2,'c':2,'v':2,'b':2,'n':2,'m':2
        }


    @staticmethod
    def encrypt(data,fixed=False):
        if not data:
            return ''
        d = __k.encrypt(data, __pad)
        b = base64.b64encode(d,__alchar)
        t = 0
        if fixed:
            return b.decode()
        if b.endswith(b'=='):
            t = 2
        elif b.endswith(b'='):
            t = 1
        return b.replace(b'=',b'').decode() + random.choice(__encdict[t])

    @staticmethod
    def decrypt(data,fixed=False):
        if not data:
            return ''
        if fixed:
            b = base64.b64decode(data,__alchar)
            return __k.decrypt(b, __pad).decode()
        t = __decdict.get(data[-1],-1)
        if t == -1:
            return None
        d = data[:-1]
        if t == 1:
            d += '='
        elif t == 2:
            d += '=='
        b = base64.b64decode(d,__alchar)
        return __k.decrypt(b, __pad).decode()

    @staticmethod
    def testdict():
        for ed in __encdict.items():
            for edl in ed[1]:
                if __decdict[edl] != ed[0]:
                    print('inner dict test faild:%s'%edl)
        print('inner dict test passed')

def fulltest():
    Cryption.testdict()
    hashtable = {}
    start = time.time()
    for i in range(100):
        ed = Cryption.encrypt(str(i))
        dd = Cryption.decrypt(ed)
        if int(dd) != i:
            print('%d not equals'%i)
            return
        if hashtable.has_key(ed):
            print('%d conflict'%i)
            return
        else:
            hashtable[ed] = i
    print(time.time() - start)
    print('fulltest is over')

def test():
    #str = raw_input('please input data:')
    start = time.time()
    ed = Cryption.encrypt(str)
    """print 'encode data is %s'%ed
    print 'time passed:%fs'%(time.time() - start)
    print 'decode data is %s'%Cryption.decrypt(ed)
    print 'time passed:%fs'%(time.time() - start)"""

if __name__ == '__main__':
    #test()
    #fulltest()
    # ri = random.randint(1, 1000)
    # s = '%s%d'%('shengli_zhang@qq.com',ri)
    # import hashlib
    # ms = hashlib.md5(s.encode()).hexdigest()
    # print(Cryption.encrypt(ms))
    # print(Cryption.decrypt('f9nymREgqkHSeooBtdiKnXwIXeYaLEZPfp-t2tU-aQIL'))
    a = Cryption.encrypt('',True)
    print(a)
    v = Cryption.decrypt(a,True)
    print(v)

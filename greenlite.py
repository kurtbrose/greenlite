'''
This is a simple implementation of greenlets, based on the idea of leveraging
the threads implementation which is already part of standard python.

Rather than building "up" and adding stack freezing capabilities to generators,
this approach builds "down" and simply only allows one thread to run at a time.
Which thread is currently running only changes when that thread voluntarily
gives up execution by sleeping.
'''
import threading
import time
from time import sleep
from functools import wraps

free = threading.Semaphore()
free.acquire() #code is currently running until the main thread bows out via sleep

@wraps(sleep)
def _sleep(seconds):
    free.release()
    sleep(seconds)
    free.acquire()
    
def monkey_patch():
    'monkey patch time.sleep'
    time.sleep = _sleep

def start_greenlite(target, *a, **kw):
    def run(): #TODO pass through arguments properly
        free.acquire()
        target()
    kw['target'] = run
    threading.Thread(*a, **kw).start()

if __name__ == '__main__':
    monkey_patch()
    
    def make_talker(name):
        def talker():
            for i in range(10):
                print "+",name,
                sleep(0.2) #use the original sleep which does not release control
                print "-",name,
                time.sleep(1.0) #pause so other pyglets can run
        return talker
    for i in [1,2,3,4]:
        talker = make_talker(str(i))
        start_greenlite(target=talker)
    print "going to sleep so pyglets can run"
    time.sleep(5) #let the talkers run for awhile


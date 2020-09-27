# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 13:39:19 2020

@author: Eric
"""

# ============================================================================
#Generate every 5 seconds a random number between 1-25 and print out the corresponding fibonacci number 
# ============================================================================

import time
import numpy as np

def fibonacci(n):
      """ Recursive function to print nth fibonacci number"""
      if n <=1:
            return n
      else:
            return(fibonacci(n-1) + fibonacci(n-2))

def main():
      num = np.random.randint(1,25)
      print("%dth fibonacci rumber is : %d"%(num, fibonacci(num)))
      
starttime = time.time() #returns the exact time in system time representation
timeout = time.time() + 60*2 # 60 seconds times 2 meaning the script will run for 2 minutes.
while time.time() <= timeout:
      try:
            main()
            time.sleep(5- ((time.time()-starttime) % 5.0))
      except KeyboardInterrupt:
            print("\n\nKeyboard exception recived. Exiting.")
            break
            






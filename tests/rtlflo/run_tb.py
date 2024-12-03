#!/usr/bin/env python
from tb_runner import tb_runner
          
def run_test():
    tb = tb_runner()
    tb.startproject()
    tb.runproject()

if __name__ == "__main__":
    run_test()

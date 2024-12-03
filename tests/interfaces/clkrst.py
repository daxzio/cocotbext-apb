from cocotb.clock import Clock
from cocotb import start_soon
from cocotb.triggers import RisingEdge, Timer

class Clk:
    def __init__(self, dut, period=10, units="ns", clkname='clk'):
        self.clk = getattr(dut, clkname)
        self.period = period
        start_soon(Clock(self.clk, self.period, units=units).start())        

    async def wait_clkn(self, length=1):
        for i in range(int(length)):
            await RisingEdge(self.clk)

    async def end_test(self, length=10):
       await self.wait_clkn(length)

class Reset:
    def __init__(self, dut, clk, reset_length=100, reset_sense=1, resetname='reset'):
        self.reset = getattr(dut, resetname)
        self.reset_length = reset_length
        self.reset_sense = reset_sense
        self.clk = clk
        self.finished = False

        self.reset.setimmediatevalue(self.reset_sense)
        start_soon(self.set_reset())
    
    async def set_reset(self):
        self.finished = False
        await self.clk.wait_clkn(self.reset_length)
        self.reset.value = (~self.reset_sense)  & 0x1
        self.finished = True

class ClkReset:
   def __init__(self, dut, period=10, clk_freq=None, reset_length=100, reset_sense=1, clkname='clk', resetname='reset'):
       self.clk_freq = clk_freq
       if not self.clk_freq is None:
           self.period = 1000/self.clk_freq
       else:
           self.period = period
       # print(f"clock period {self.period} {self.clk_freq}")
       self.clk = Clk(dut, period=self.period, clkname=clkname)
       self.reset = Reset(dut, self.clk, reset_length=reset_length, reset_sense=reset_sense, resetname=resetname)

   async def wait_clkn(self, length=1):
       await self.clk.wait_clkn(length)

   async def end_test(self, length=10):
       await self.wait_clkn(length)

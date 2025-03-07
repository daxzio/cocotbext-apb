from cocotbext.apb import ApbMaster, Apb4Bus

# import math
import logging
from random import seed
from random import randint


class ApbDriver:
    def __init__(
        self, dut, apb_prefix="s_apb", clk_name="clk", reset_name=None, seednum=None
    ):
        self.log = logging.getLogger(f"cocotb.ApbDriver")
        self.enable_logging()
        self.bus = Apb4Bus.from_prefix(dut, apb_prefix)
        if reset_name is None:
            self.intf = ApbMaster(dut, self.bus, getattr(dut, clk_name))
        else:
            self.intf = ApbMaster(
                dut, self.bus, getattr(dut, clk_name), getattr(dut, reset_name)
            )
        self.intf.log.setLevel(logging.WARNING)
        if seednum is not None:
            self.base_seed = seednum
        else:
            self.base_seed = randint(0, 0xFFFFFF)
        seed(self.base_seed)
        self.log.debug(f"Seed is set to {self.base_seed}")

    @property
    def returned_val(self):
        if hasattr(self.read_op, "data"):
            if hasattr(self.read_op.data, "data"):
                return int.from_bytes(self.read_op.data.data, byteorder="little")
            else:
                return int.from_bytes(self.read_op.data, byteorder="little")
        else:
            return int.from_bytes(self.read_op, byteorder="little")

    def enable_logging(self):
        self.log.setLevel(logging.DEBUG)

    def disable_logging(self):
        self.log.setLevel(logging.WARNING)

    #
    #     def enable_write_backpressure(self, seednum=None):
    #         if seednum is not None:
    #             self.base_seed = seednum
    #         self.axi_master.write_if.aw_channel.set_pause_generator(cycle_pause(self.base_seed+1))
    #         self.axi_master.write_if.w_channel.set_pause_generator(cycle_pause(self.base_seed+2))
    #         self.axi_master.write_if.b_channel.set_pause_generator(cycle_pause(self.base_seed+3))
    #
    #     def enable_read_backpressure(self, seednum=None):
    #         if seednum is not None:
    #             self.base_seed = seednum
    #         self.axi_master.read_if.r_channel.set_pause_generator(cycle_pause(self.base_seed+4))
    #         self.axi_master.read_if.ar_channel.set_pause_generator(cycle_pause(self.base_seed+5))
    #
    #     def enable_backpressure(self, seednum=None):
    #         self.enable_write_backpressure(seednum)
    #         self.enable_read_backpressure(seednum)
    #
    #     def disable_backpressure(self):
    # #         self.axi_master.write_if.aw_channel.clear_pause_generator()
    # #         self.axi_master.write_if.w_channel.clear_pause_generator()
    # #         self.axi_master.write_if.b_channel.clear_pause_generator()
    # #
    # #         self.axi_master.read_if.r_channel.clear_pause_generator()
    # #         self.axi_master.read_if.ar_channel.clear_pause_generator()
    #         self.axi_master.write_if.aw_channel.set_pause_generator(itertools.cycle([0,]))
    #         self.axi_master.write_if.w_channel.set_pause_generator(itertools.cycle([0,]))
    #         self.axi_master.write_if.b_channel.set_pause_generator(itertools.cycle([0,]))
    #
    #         self.axi_master.read_if.r_channel.set_pause_generator(itertools.cycle([0,]))
    #         self.axi_master.read_if.ar_channel.set_pause_generator(itertools.cycle([0,]))
    #
    #
    #     async def poll(self, addr, data, length=None, debug=False):
    #         self.log.debug(f"Poll  0x{addr:08x}: for 0x{data:04x}")
    #         while True:
    #             await self.read(addr, debug=debug)
    #             if data == self.returned_val:
    #                 self.log.debug(f"Condition Satisified")
    #                 break
    #         return
    #
    def check_read(self, debug=True):
        if debug:
            self.log.debug(f"Read  0x{self.addr:08x}: 0x{self.returned_val:08x}")
        if not self.returned_val == self.data and not None == self.data:
            raise Exception(
                f"Expected 0x{self.data:08x} doesn't match returned 0x{self.returned_val:08x}"
            )

    async def read(self, addr, data=None, debug=True):
        self.addr = addr
        self.data = data
        self.read_op = await self.intf.read(self.addr)
        self.check_read(debug)
        return self.read_op

    #
    #
    async def write(self, addr, data=None, debug=True):
        self.addr = addr
        self.data = data
        self.writedata = self.data
        if debug:
            self.log.debug(f"Write 0x{self.addr:08x}: 0x{self.data:08x}")
        bytesdata = self.data.to_bytes(len(self.bus.pwdata), "little")
        await self.intf.write(addr, bytesdata)


#     def init_read(self, *args, **kwargs):
#         self.read_op = self.axi_master.init_read(*args, **kwargs)
#
#     def read_nowait(self, addr, data=None, length=None, debug=True):
#         self.addr = addr
#         self.data = data
#         self.len = length
#         self.init_read(self.addr, self.length, arid=self.arid)
#         if debug:
#             self.log.debug(f"Read  0x{addr:08x}:")
#
#     def write_nowait(self, addr, data=None, length=None, debug=True):
#         self.len = length
#         self.addr = addr
#         if data is None:
#             self.data = 0
#             for i in range(0, self.length, 4):
#                 self.data = self.data | (randint(0, 0xffffffff) << i*8)
#         else:
#             self.data = data
#         self.writedata = self.data
#         if debug:
#             self.log.debug(f"Write 0x{self.addr:08x}: 0x{self.data:08x}")
#         bytesdata = tobytes(self.data, self.length)
#         #bytesdata = self.data.to_bytes(self.length, 'little')
#         self.write_op = self.axi_master.init_write(self.addr, bytesdata, awid=self.arid)

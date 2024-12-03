import logging
# import cocotb
# from cocotb.queue import Queue
# from cocotb.triggers import Event
from cocotb.triggers import RisingEdge
# from cocotb.triggers import FallingEdge

from .version import __version__
from .constants import ApbProt
from .address_space import Region
from .reset import Reset
# from .apb_bus import ApbBus


class ApbMaster(Region, Reset):
    def __init__(self, dut, bus, clock, reset=None, reset_active_level=True, **kwargs):
        self.bus = bus
        self.clock = clock
        self.reset = reset
        if bus._name:
            self.log = logging.getLogger(f"cocotb.{bus._entity._name}.{bus._name}")
        else:
            self.log = logging.getLogger(f"cocotb.{bus._entity._name}")

        self.log.info("APB master ")
        self.log.info(f"cocotbext-apb version {__version__}")
        self.log.info("Copyright (c) 2024 Daxzio")
        self.log.info("https://github.com/daxzio/cocotbext-apb")

        self.address_width = len(self.bus.paddr)
        self.width = len(self.bus.pwdata)
        self.byte_size = 8
        self.byte_lanes = self.width // self.byte_size
        self.data_mask = 2**self.width - 1
        self.strb_mask = 2**self.byte_lanes - 1

        self.penable_present = hasattr(self.bus, "penable")
        self.pstrb_present = hasattr(self.bus, "pstrb")
        self.pprot_present = hasattr(self.bus, "pprot")
        self.pslverr_present = hasattr(self.bus, "pslverr")

        super().__init__(2**self.address_width, **kwargs)

        self.log.info("APB master configuration:")
        self.log.info(f"  Address width: {self.address_width} bits")
        self.log.info(f"  Byte size: {self.byte_size} bits")
        self.log.info(f"  Data width: {self.width} bits ({self.byte_lanes} bytes)")

        self.log.info("APB master signals:")
        for sig in sorted(
            list(set().union(self.bus._signals, self.bus._optional_signals))
        ):
            if hasattr(self.bus, sig):
                self.log.info(f"  {sig} width: {len(getattr(self.bus, sig))} bits")
            else:
                self.log.info(f"  {sig}: not present")

        if self.pstrb_present:
            assert self.byte_lanes == len(self.bus.pstrb)
        assert self.byte_lanes * self.byte_size == self.width

        #         self.channel = ApbSource(bus, clock, reset, reset_active_level)
        #         self.channel.queue_occupancy_limit = 2
        #
        #         self.command_queue = Queue()
        #         self.command_queue.queue_occupancy_limit = 2
        #         self.current_command = None
        #
        #         self.int_resp_command_queue = Queue()
        #         self.current_resp_command = None
        #
        #         self.in_flight_operations = 0
        #         self._idle = Event()
        #         self._idle.set()
        #
        #         self._process_cr = None
        #         self._process_resp_cr = None

        if self.penable_present:
            self.bus.penable.value = 0
        self.bus.psel.value = 0
        self.bus.paddr.value = 0
        if self.pstrb_present:
            self.bus.pstrb.value = 0
        if self.pprot_present:
            self.bus.pprot.value = 0
        self.bus.pwrite.value = 0
        self.bus.pwdata.value = 0

        self._init_reset(reset, reset_active_level)

    #     def _handle_reset(self, state):
    #         if state:
    #             self.log.info("Reset asserted")
    #             if self._process_cr is not None:
    #                 self._process_cr.kill()
    #                 self._process_cr = None
    # #             if self._process_read_resp_cr is not None:
    # #                 self._process_read_resp_cr.kill()
    # #                 self._process_read_resp_cr = None
    # #
    #             self.achannel.clear()
    # #             self.r_channel.clear()
    # #
    # #             def flush_cmd(cmd):
    # #                 self.log.warning("Flushed read operation during reset: %s", cmd)
    # #                 if cmd.event:
    # #                     cmd.event.set(None)
    # #
    # #             while not self.read_command_queue.empty():
    # #                 cmd = self.read_command_queue.get_nowait()
    # #                 flush_cmd(cmd)
    # #
    # #             if self.current_read_command:
    # #                 cmd = self.current_read_command
    # #                 self.current_read_command = None
    # #                 flush_cmd(cmd)
    # #
    # #             while not self.int_read_resp_command_queue.empty():
    # #                 cmd = self.int_read_resp_command_queue.get_nowait()
    # #                 flush_cmd(cmd)
    # #
    # #             if self.current_read_resp_command:
    # #                 cmd = self.current_read_resp_command
    # #                 self.current_read_resp_command = None
    # #                 flush_cmd(cmd)
    # #
    #             self.in_flight_operations = 0
    #             self._idle.set()
    #         else:
    #             self.log.info("Reset de-asserted")
    #             if self._process_cr is None:
    #                 self._process_cr = cocotb.start_soon(self._process_cmd())
    # #             if self._process_resp_cr is None:
    # #                 self._process_resp_cr = cocotb.start_soon(self._process_cmd_resp())
    #
    #     async def _process_cmd(self):
    #         while True:
    #             cmd = await self.command_queue.get()
    #             self.current_read_command = cmd
    #
    # #             word_addr = (cmd.address // self.byte_lanes) * self.byte_lanes
    #
    # #             cycles = (cmd.length + self.byte_lanes-1 + (cmd.address % self.byte_lanes)) // self.byte_lanes
    #
    # #             resp_cmd = ApbReadRespCmd(cmd.address, cmd.length, cycles, cmd.prot, cmd.event)
    # #             await self.int_read_resp_command_queue.put(resp_cmd)
    #
    #             self.log.info(f"Read start addr: 0x{cmd.address:08x} prot: {cmd.prot}")
    #
    #             c = self.channel._transaction_obj()
    #             c.paddr = cmd.address
    #             c.pprot = cmd.prot
    #
    #             await self.channel.send(c)
    #             self.current_command = None

    async def read(self, address, prot=ApbProt.NONSECURE):
        if address < 0 or address >= 2**self.address_width:
            raise ValueError("Address out of range")

        if not self.pprot_present and prot != ApbProt.NONSECURE:
            raise ValueError(
                "pprot sideband signal value specified, but signal is not connected"
            )

        self.log.info(f"Read addr: 0x{address:08x} prot: {prot}")

        if self.penable_present:
            self.bus.penable.value = 1
        self.bus.psel.value = 1
        self.bus.paddr.value = address
        if self.pprot_present:
            self.bus.pprot.value = prot
        self.bus.pwrite.value = 0
        if self.pstrb_present:
            self.bus.pstrb.value = 0
        await RisingEdge(self.clock)

        while not self.bus.pready.value:
            await RisingEdge(self.clock)
        data = int(self.bus.prdata.value)
        self.log.info(f"Value read: 0x{data:08x}")

        if self.penable_present:
            self.bus.penable.value = 0
        self.bus.psel.value = 0
        self.bus.paddr.value = 0
        if self.pprot_present:
            self.bus.pprot.value = 0
        self.bus.pwrite.value = 0
        if self.pstrb_present:
            self.bus.pstrb.value = 0

        return data.to_bytes(len(self.bus.prdata), "little")

    #         event = Event()
    #
    #         self.in_flight_operations += 1
    #         self._idle.clear()
    #
    #         await self.command_queue.put(ApbReadCmd(address, prot, event))
    #
    #         await event.wait()
    #         return event.data

    async def write(self, address, data, strb=None, prot=ApbProt.NONSECURE):
        if address < 0 or address >= 2**self.address_width:
            raise ValueError("Address out of range")

        if not self.pprot_present and prot != ApbProt.NONSECURE:
            raise ValueError(
                "pprot sideband signal value specified, but signal is not connected"
            )

        data = int.from_bytes(data, byteorder="little")
        self.log.info(
            f"Write addr: 0x{address:08x} data: 0x{data:08x} prot: {prot}"
        )

        if self.penable_present:
            self.bus.penable.value = 1
        self.bus.psel.value = 1
        self.bus.paddr.value = address
        self.bus.pprot.value = prot
        self.bus.pwdata.value = data & self.data_mask
        self.bus.pwrite.value = 1
        if self.pstrb_present:
            if strb is None:
                self.bus.pstrb.value = self.strb_mask
            else:
                self.bus.pstrb.value = strb
        await RisingEdge(self.clock)

        while not self.bus.pready.value:
            await RisingEdge(self.clock)
#         data = int(self.bus.prdata.value)
#         self.log.info(f"Value read: 0x{data:08x}")

        if self.penable_present:
            self.bus.penable.value = 0
        self.bus.psel.value = 0
        self.bus.paddr.value = 0
        self.bus.pprot.value = 0
        self.bus.pwrite.value = 0
        self.bus.pwdata.value = 0
        if self.pstrb_present:
            self.bus.pstrb.value = 0

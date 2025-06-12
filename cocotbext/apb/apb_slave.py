"""

Copyright (c) 2024-2025 Daxzio

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

from cocotb import start_soon
from cocotb.triggers import RisingEdge

from .apb_base import ApbBase

# from .reset import Reset
#
from typing import Any


class ApbSlave(ApbBase):
    def __init__(self, bus, clock, target=None, **kwargs):
        super().__init__(bus, clock, name="slave", **kwargs)
        #         self.reset = reset
        self.target = target

        self.bus.pready.value = 0
        self.bus.prdata.value = 0
        self.bus.pslverr.value = 0

        self._run_coroutine_obj: Any = None
        self._restart()

    def _restart(self) -> None:
        if self._run_coroutine_obj is not None:
            self._run_coroutine_obj.kill()
        self._run_coroutine_obj = start_soon(self._run())

    async def _write(self, address, data, strb):
        for i in range(self.byte_lanes):
            if 1 == ((int(strb.value) >> i) & 0x1):
                await self.target.write_byte(address + i, data[i].to_bytes(1, "little"))

    async def _read(self, address, length):
        return await self.target.read(address, length)

    async def _run(self):
        await RisingEdge(self.clock)
        while True:
            await RisingEdge(self.clock)
            if bool(self.bus.psel.value):
                addr = int(self.bus.paddr.value)
                pwrite = bool(self.bus.pwrite.value)

                if addr < 0 or addr >= 2**self.address_width:
                    raise ValueError("Address out of range")

                for i in range(self.delay):
                    await RisingEdge(self.clock)

                self.bus.pready.value = 1
                if pwrite:
                    wdata = int(self.bus.pwdata.value)
                    await self._write(
                        addr, wdata.to_bytes(self.byte_lanes, "little"), self.bus.pstrb
                    )
                    self.log.debug(f"Write 0x{addr:08x} 0x{wdata:08x}")
                else:
                    x = await self._read(addr, self.byte_lanes)
                    rdata = int.from_bytes(x, byteorder="little")
                    self.bus.prdata.value = rdata
                    self.log.debug(f"Read  0x{addr:08x} 0x{rdata:08x}")
                await RisingEdge(self.clock)
                self.bus.pready.value = 0
                self.bus.prdata.value = 0

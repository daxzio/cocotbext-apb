"""

Copyright (c) 2024-2026 Daxzio

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

from typing import Any

from cocotb import start_soon
from cocotb.triggers import RisingEdge

from .apb_base import ApbBase
from .constants import (
    APBInstructionErr,
    APBPrivilegedErr,
    ApbProt,
    APBReadOnlyErr,
    APBSlvErr,
    APBWriteOnlyErr,
)


class InvalidAccess(Exception):
    pass


class ApbDevice(ApbBase):
    def __init__(self, bus, clock, target=None, **kwargs):
        super().__init__(bus, clock, name="device", **kwargs)
        #         self.reset = reset
        self.target = target
        self.privileged_addrs = []
        self.instruction_addrs = []
        self.ro_addrs = []
        self.wo_addrs = []

        self.bus.pready.value = 0
        self.bus.prdata.value = 0
        if self.pslverr_present:
            self.bus.pslverr.value = 0

        self._run_coroutine_obj: Any = None
        self._restart()

    def _restart(self) -> None:
        if self._run_coroutine_obj is not None:
            self._run_coroutine_obj.kill()
        self._run_coroutine_obj = start_soon(self._run())

    def _address_in(self, address, addresses):
        for addrs in addresses:
            if isinstance(addrs, int):
                if addrs == address:
                    return True
            elif isinstance(addrs, (list, tuple)):
                if addrs[1] < addrs[0]:
                    raise ValueError(f"Address range needs to be increasing , {addrs}")
                if len(addrs) != 2:
                    raise ValueError(f"Address range needs to be 2 value , {addrs}")
                if addrs[0] <= address < addrs[1]:
                    return True
            else:
                raise TypeError(f"Unknown addr type , {addrs}")
        return False

    def check_address(self, address, prot, addresses, prot_type, exception):
        if prot is not None:
            prot = int(prot.value) if hasattr(prot, "value") else int(prot)
        if (
            prot is not None
            and prot != prot_type
            and self._address_in(address, addresses)
        ):
            raise exception

    def check_permission(self, address, prot):
        self.check_address(
            address, prot, self.privileged_addrs, ApbProt.PRIVILEGED, APBPrivilegedErr
        )
        self.check_address(
            address,
            prot,
            self.instruction_addrs,
            ApbProt.INSTRUCTION,
            APBInstructionErr,
        )

    def check_rw_access(self, address, write):
        if write and self._address_in(address, self.ro_addrs):
            raise APBReadOnlyErr
        if not write and self._address_in(address, self.wo_addrs):
            raise APBWriteOnlyErr

    async def _write(self, address, data, strb=None, prot=None):
        self.check_permission(address, prot)
        self.check_rw_access(address, True)
        if strb is None:
            await self.target.write(address, data)
        else:
            for i in range(self.byte_lanes):
                if 1 == ((int(strb.value) >> i) & 0x1):
                    await self.target.write_byte(
                        address + i, data[i].to_bytes(1, "little")
                    )

    async def _read(self, address, length, prot=None):
        self.check_permission(address, prot)
        self.check_rw_access(address, False)
        return await self.target.read(address, length)

    async def _run(self):
        await RisingEdge(self.clock)
        while True:
            await RisingEdge(self.clock)
            if bool(self.bus.psel.value):
                # PWDATA is only required to be valid in ACCESS. With
                # registered-write bridges that is one cycle after SETUP.
                if self.penable_present and not bool(self.bus.penable.value):
                    await RisingEdge(self.clock)

                addr = int(self.bus.paddr.value)
                pwrite = bool(self.bus.pwrite.value)
                pprot = None
                if self.pprot_present:
                    pprot = int(self.bus.pprot.value)
                pstrb = None
                if self.pstrb_present:
                    pstrb = self.bus.pstrb

                if addr < 0 or addr >= 2**self.address_width:
                    raise ValueError("Address out of range")

                for i in range(self.delay):
                    await RisingEdge(self.clock)

                slverr = False
                rdata = 0
                wdata = 0
                try:
                    if pwrite:
                        wdata = int(self.bus.pwdata.value)
                        await self._write(
                            addr,
                            wdata.to_bytes(self.byte_lanes, "little"),
                            pstrb,
                            pprot,
                        )
                    else:
                        x = await self._read(addr, self.byte_lanes, pprot)
                        rdata = int.from_bytes(x, byteorder="little")
                except APBSlvErr as e:
                    slverr = True
                    err_name = type(e).__name__.removeprefix("APB")
                    self.log.warning(f"Access 0x{addr:08x} Invalid, {err_name}")

                # Registered slave: outputs update after this posedge and are
                # sampled on the next. Drive PSLVERR before PREADY so combo
                # masters that complete on pready & ~pslverr cannot see an
                # OKAY glitch in the same delta.
                if slverr and self.pslverr_present:
                    self.bus.pslverr.value = 1
                if not pwrite:
                    self.bus.prdata.value = 0 if slverr else rdata
                self.bus.pready.value = 1
                if not slverr:
                    if pwrite:
                        self.log.debug(f"Write 0x{addr:08x} 0x{wdata:08x}")
                    else:
                        self.log.debug(f"Read  0x{addr:08x} 0x{rdata:08x}")

                await RisingEdge(self.clock)
                self.bus.pready.value = 0
                self.bus.prdata.value = 0
                if self.pslverr_present:
                    self.bus.pslverr.value = 0

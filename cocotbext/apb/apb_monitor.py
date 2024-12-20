import math

from cocotb import start_soon
from cocotb.triggers import RisingEdge

from .constants import ApbProt
from .utils import resolve_x_int
from .apb_base import ApbBase


class ApbMonitor(ApbBase):
    def __init__(self, bus, clock, **kwargs) -> None:
        super().__init__(bus, clock, name="monitor", **kwargs)
        self.disable_logging()
        self.timeout_max = 1000
        self.timeout = 0

        for i, j in self.bus._signals.items():
            setattr(self, i, 0)

        self._run_coroutine_obj = None
        self._resolve_coroutine_obj = None
        self._restart()

    def _restart(self) -> None:
        if self._run_coroutine_obj is not None:
            self._run_coroutine_obj.kill()
        if self._resolve_coroutine_obj is not None:
            self._resolve_coroutine_obj.kill()
        self._run_coroutine_obj = start_soon(self._run())
        self._resolve_coroutine_obj = start_soon(self._resolve_signals())

    async def _resolve_signals(self):
        while True:
            for i, j in self.bus._signals.items():
                setattr(self, i, resolve_x_int(getattr(self.bus, i)))
            await RisingEdge(self.clock)

    async def _run(self):
        while True:
            self.timeout = 0

            if not 0 == self.psel:
                index = int(math.log2(self.psel))
                if not self.psel == 2**index:
                    self.log.critical(f"incorrect formatted psel {self.psel}")

                if self.paddr < 0 or self.paddr >= 2**self.address_width:
                    raise ValueError("Address out of range")

                if self.pprot_present and self.pprot != ApbProt.NONSECURE:
                    raise ValueError(
                        "pprot sideband signal value specified, but signal is not connected"
                    )
                if 1 == self.penable:
                    self.log.critical(
                        "penable is asserted in the same first cycle with psel"
                    )

                pwrite = self.pwrite
                paddr = self.paddr
                if self.pprot_present:
                    pprot = self.pprot
                    pprot_text = f"prot: {pprot}"
                else:
                    pprot_text = ""

                wdata = self.pwdata
                await RisingEdge(self.clock)
                if 0 == self.penable:
                    self.log.critical(
                        f"penable is not asserted in the second cycle after psel {self.penable}"
                    )
                while 0 == (self.pready and self.psel):
                    await RisingEdge(self.clock)
                    self.timeout += 1
                    if self.timeout >= self.timeout_max:
                        raise Exception(
                            f"pready wait has exceed timout {self.timeout_max}"
                        )
                apb = ""
                if not 0 == len(self.bus.psel) - 1:
                    apb = f"({index}) "
                if pwrite:
                    self.log.debug(
                        f"Write {apb}0x{paddr:08x}: 0x{wdata:08x} {pprot_text}"
                    )
                else:
                    rdata = (self.prdata >> 32 * index) & self.wdata_mask
                    self.log.debug(
                        f"Read  {apb}0x{paddr:08x}: 0x{rdata:08x} {pprot_text}"
                    )
            await RisingEdge(self.clock)

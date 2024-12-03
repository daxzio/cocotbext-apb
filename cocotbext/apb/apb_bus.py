from cocotb_bus.bus import Bus

# from apb.stream import define_stream
# ApbBus, ApbTransaction, ApbSource, ApbSink, ApbMonitor = define_stream("Apb",
#     signals=["psel", "penable", "pwrite", "pprot", "paddr", "pwdata", "pstrb", "pready", "prdata", "pslverr"],
#     optional_signals=[],
#     signal_widths={"pprot": 3}
# )
# apb5 'pwakeup', 'pauser', 'pwuser', 'pruser', 'pbuser', 'pnse',

class ApbBus(Bus):
    _signals = ['psel', 'pwrite', 'paddr', 'pwdata', 'pready', 'prdata', ]
    _optional_signals = ['penable', 'pstrb', 'pprot', 'pslverr', 'pwakeup', 'pauser', 'pwuser', 'pruser', 'pbuser', 'pnse',]

    def __init__(self, entity=None, prefix=None, **kwargs):
        super().__init__(entity, prefix, self._signals, optional_signals=self._optional_signals, **kwargs)

    @classmethod
    def from_entity(cls, entity, **kwargs):
        return cls(entity, **kwargs)

    @classmethod
    def from_prefix(cls, entity, prefix, **kwargs):
        return cls(entity, prefix, **kwargs)

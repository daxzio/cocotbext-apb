from cocotb_bus.bus import Bus

# from apb.stream import define_stream
# ApbBus, ApbTransaction, ApbSource, ApbSink, ApbMonitor = define_stream("Apb",
#     signals=["psel", "penable", "pwrite", "pprot", "paddr", "pwdata", "pstrb", "pready", "prdata", "pslverr"],
#     optional_signals=[],
#     signal_widths={"pprot": 3}
# )
# apb5 'pwakeup', 'pauser', 'pwuser', 'pruser', 'pbuser', 'pnse',


class Apb3Bus(Bus):
    _signals = [
        "psel",
        "pwrite",
        "paddr",
        "pwdata",
        "pready",
        "prdata",
    ]
    _optional_signals = ["penable"]

    def __init__(
        self, entity=None, prefix=None, signals=None, optional_signals=None, **kwargs
    ):
        if signals is None:
            signals = self._signals
        if optional_signals is None:
            optional_signals = self._optional_signals
        super().__init__(
            entity, prefix, signals, optional_signals=optional_signals, **kwargs
        )

    @classmethod
    def from_entity(cls, entity, **kwargs):
        return cls(entity, **kwargs)

    @classmethod
    def from_prefix(cls, entity, prefix, **kwargs):
        return cls(entity, prefix, **kwargs)


class Apb4Bus(Apb3Bus):
    def __init__(
        self, entity=None, prefix=None, signals=None, optional_signals=None, **kwargs
    ):
        if signals is None:
            signals = self._signals
        if optional_signals is None:
            optional_signals = self._optional_signals.extend(
                ["pstrb", "pprot", "pslverr"]
            )
        super().__init__(
            entity, prefix, signals, optional_signals=self._optional_signals, **kwargs
        )


class ApbBus(Apb4Bus):
    pass


class Apb5Bus(Apb4Bus):
    def __init__(
        self, entity=None, prefix=None, signals=None, optional_signals=None, **kwargs
    ):
        if signals is None:
            signals = self._signals
        if optional_signals is None:
            optional_signals = self._optional_signals.extend(
                [
                    "pwakeup",
                    "pauser",
                    "pwuser",
                    "pruser",
                    "pbuser",
                    "pnse",
                ]
            )
        super().__init__(
            entity, prefix, signals, optional_signals=self._optional_signals, **kwargs
        )

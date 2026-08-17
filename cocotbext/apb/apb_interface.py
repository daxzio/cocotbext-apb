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

from cocotb.handle import LogicArrayObject, LogicObject

try:
    from cocotbext.interface import Interface  # type: ignore[import]

    HAVE_COCOTBEXT_INTERFACE = True
except ImportError as _import_error:  # pragma: no cover - exercised without the dep
    HAVE_COCOTBEXT_INTERFACE = False
    _INTERFACE_IMPORT_ERROR = _import_error

    _MISSING_MSG = (
        "Apb4Interface requires the optional 'cocotbext-interface' package, "
        "which is not installed. Install it with:\n\n"
        "    pip install cocotbext-interface\n\n"
        "Alternatively use ApbBus / Apb4Bus, which have no extra dependencies."
    )

    class Apb4Interface:  # type: ignore[no-redef]
        """Placeholder used when ``cocotbext-interface`` is not installed.

        Importing :mod:`cocotbext.apb` still succeeds so the rest of the
        package works without the optional dependency; any attempt to
        construct or connect this bus raises a clear, actionable error.
        """

        def __init__(self, *args, **kwargs):
            raise ImportError(_MISSING_MSG) from _INTERFACE_IMPORT_ERROR

        @classmethod
        def from_prefix(cls, *args, **kwargs):
            raise ImportError(_MISSING_MSG) from _INTERFACE_IMPORT_ERROR

        @classmethod
        def from_entity(cls, *args, **kwargs):
            raise ImportError(_MISSING_MSG) from _INTERFACE_IMPORT_ERROR

else:

    class Apb4Interface(Interface):  # type: ignore[no-redef]
        """APB4 bus using cocotbext-interface.

        Drop-in replacement for Apb4Bus / ApbBus: provides the same signal
        attributes and the ``_signals`` / ``_optional_signals`` compatibility
        layer expected by ApbBase and its subclasses (ApbHost, ApbDevice,
        ApbMonitor, ApbRam).

        Connection mirrors the existing API::

            bus = Apb4Interface.from_prefix(dut, "s_apb")
            host = ApbHost(bus, dut.clk)
        """

        # --- Required (APB3 core) ---
        psel: LogicObject | LogicArrayObject
        pwrite: LogicObject
        paddr: LogicArrayObject
        pwdata: LogicArrayObject
        pready: LogicObject
        prdata: LogicArrayObject

        # --- Optional (APB4) ---
        penable: LogicObject | None = None
        pstrb: LogicArrayObject | None = None
        pprot: LogicArrayObject | None = None
        pslverr: LogicObject | None = None

        def __init__(self, signals, index=None):
            super().__init__(signals, index=index)

            # Derive optional signal names from the class definition: any
            # signal declared with a default value (= None) is optional.
            # This mirrors how Interface._get_requirements() works internally.
            requirements = self._get_requirements()
            optional_names = [
                name for name, default in requirements.items() if default is None
            ]

            # bus.Bus never sets an attribute for an absent optional signal, so
            # hasattr(bus, "penable") is False.  Interface instead assigns None.
            # Deleting the instance attribute is not enough: the class-level
            # "penable = None" default would still satisfy the lookup.  Record
            # the absent names and reject them in __getattribute__ so the VIPs'
            # hasattr() guards (ApbBase, ApbHost, ApbDevice, ApbMonitor) work.
            absent = frozenset(
                name for name in optional_names if getattr(self, name, None) is None
            )
            for name in absent:
                self.__dict__.pop(name, None)
                if name in self._signals_list:
                    self._signals_list.remove(name)
            self._absent_signals = absent

            self._signals = {n: getattr(self, n) for n in self._signals_list}
            self._optional_signals = list(optional_names)
            self._name = ""

        def __getattribute__(self, name):
            # Absent optional signals must look genuinely missing, otherwise
            # the class-level None default would make hasattr() return True.
            try:
                absent = object.__getattribute__(self, "_absent_signals")
            except AttributeError:
                absent = ()
            if name in absent:
                raise AttributeError(
                    f"{type(self).__name__!r} object has no attribute {name!r}: "
                    "optional signal not present in the RTL"
                )
            return object.__getattribute__(self, name)

        @classmethod
        def from_prefix(cls, entity, prefix, **kwargs):
            """Connect to ``entity.<prefix>_<signal>`` (e.g. ``from_prefix(dut, 's_apb')``)."""
            pattern = f"{prefix}_%" if "%" not in prefix else prefix
            instance = cls.from_pattern(entity, pattern=pattern, **kwargs)
            instance._name = prefix
            return instance

        @classmethod
        def from_entity(cls, entity, **kwargs):
            """Connect to ``entity.<signal>`` (no prefix)."""
            instance = super().from_entity(entity, **kwargs)
            instance._name = ""
            return instance

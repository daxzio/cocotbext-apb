# test_interface — APB with cocotbext-interface style

This directory runs the same test flow as `test_basic` but connects to the DUT
using the **cocotbext-interface** style (`Apb4Interface.from_prefix`) instead of
`ApbBus.from_prefix`.

## Prerequisites

Needs the optional `cocotbext-interface` dependency:

```bash
pip install -e .[interface]
```

`cocotbext-interface` is never required by `cocotbext-apb` itself. Without it,
`import cocotbext.apb` still works and these tests **skip** rather than fail
(they gate on the exported `HAVE_COCOTBEXT_INTERFACE` flag).

This suite is included in the root `make verilog` list.

## Run

Activate the project venv, then:

```bash
make SIM=icarus
```

## What this demonstrates

- **Apb4Interface** (`cocotbext.apb.apb_interface`) uses the cocotbext-interface
  `Interface` base and `from_prefix(entity, prefix)` for connection
  (e.g. `s_apb_psel`, `s_apb_paddr`, …).
- The same **ApbHost** and **ApbMonitor** are used unchanged; they see a
  bus-compatible object (`_signals`, `_optional_signals`, `hasattr`-based
  optional signal detection) so no VIP changes were required.

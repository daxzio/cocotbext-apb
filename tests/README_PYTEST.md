# Quick Start: Running Tests with pytest

## Installation

```bash
pip install -r requirements.txt
```

This installs `cocotb-test` which provides pytest integration for cocotb.

## Running Tests

### Run all pytest-based tests

```bash
pytest tests/
```

### Run specific test file

```bash
pytest tests/test_addrmap/test_addrmap_pytest.py
pytest tests/test_format_addr.py   # AddressMap reverse lookup (no simulation)
```

See also [test_addrmap/README.md](test_addrmap/README.md) for cocotb address-map
integration tests and Makefile usage.

### Run with specific parameter value

```bash
# Run only the test with REGWIDTH=16
pytest tests/test_addrmap/test_addrmap_pytest.py::test_addrmap[16]
```

### Run in parallel (faster!)

```bash
# Install pytest-xdist first: pip install pytest-xdist
pytest tests/ -n auto
```

### Run with specific simulator

```bash
SIM=verilator pytest tests/test_addrmap/test_addrmap_pytest.py
```

## Example: Parameterized Test

The `test_addrmap_pytest.py` file demonstrates running the same test with different elaboration-time parameters:

```python
@pytest.mark.parametrize("regwidth", [8, 16, 32])
def test_addrmap(regwidth):
    run(
        verilog_sources=[...],
        toplevel="regblock",
        module="test_dut",
        parameters={"REGWIDTH": regwidth},  # Passed to DUT at elaboration
    )
```

This automatically runs 3 test cases:
- `test_addrmap[8]` - with REGWIDTH=8
- `test_addrmap[16]` - with REGWIDTH=16
- `test_addrmap[32]` - with REGWIDTH=32

## Migration from Makefile

See `example_pytest_migration.md` for detailed migration instructions.

## Files

- `test_*_pytest.py` - pytest wrapper files that call `cocotb_test.simulator.run()`
- `test_dut.py` - Your actual test code (unchanged from Makefile version)
- `test_format_addr.py` - unit tests for `AddressMap.format()` / `ApbHost.format_addr()`
- `conftest.py` - Shared pytest fixtures and configuration

## Benefits

✅ **Parameterization**: Easy to test multiple configurations
✅ **Parallel execution**: Run tests faster with `-n auto`
✅ **Better reporting**: Clear test results and failure information
✅ **CI/CD friendly**: Easy integration with GitHub Actions, etc.
✅ **No Makefile needed**: Pure Python test configuration

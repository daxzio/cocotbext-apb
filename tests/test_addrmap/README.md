# test_addrmap — register name address mapping

This directory exercises [`AddressMap`](../../cocotbext/apb/address_map.py)
integration with `ApbHost`: using register names instead of numeric addresses
for reads and writes, indexed register access, and name-based transaction logging.

See the main [README AddressMap section](../../README.md#addressmap) for API
details.

## What is tested

| Test       | Description |
|------------|-------------|
| `addrmap0` | Assign map via `addrmap[0] = {...}`, read/write by name |
| `addrmap2` | Assign map via `addaddrmap()` |
| `addrmap3` | Indexed access with `"NAME[N]"` bracket notation |
| `addrmap4` | Indexed access with the `index=` parameter |

## Run

```bash
cd tests/test_addrmap
make clean sim WAVES=0 RDL_ARGS="-P REGWIDTH=32"
```

Or from the project root (all register widths):

```bash
make   # includes test_addrmap for REGWIDTH 8, 16, 32
```

## Related unit tests

Reverse lookup (`format` / `format_addr`) is covered without simulation in
[tests/test_format_addr.py](../test_format_addr.py):

```bash
pytest tests/test_format_addr.py -v
```

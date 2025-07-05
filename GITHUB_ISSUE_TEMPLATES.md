# GitHub Issue Templates for APB Extension Bugs

## Issue Template 1: List Mutation Bug in APB Bus Classes

### Title
`[Bug] APB4Bus and APB5Bus optional_signals set to None due to incorrect extend() usage`

### Issue Body
```
**Bug Description**
The `Apb4Bus` and `Apb5Bus` classes have a critical bug where `optional_signals` is being set to `None` due to incorrect use of the `extend()` method.

**Location**
- File: `cocotbext/apb/apb_bus.py`
- Lines: 44-45 and 60-61

**Problem**
The `extend()` method modifies a list in place and returns `None`, but the code assigns the return value to `optional_signals`:

```python
# Buggy code:
optional_signals = self._optional_signals.extend(["pstrb", "pprot", "pslverr"])
# extend() returns None, so optional_signals becomes None
```

**Impact**
- **Severity**: High
- Complete loss of functionality for APB4Bus and APB5Bus
- APB4 signals (`pstrb`, `pprot`, `pslverr`) not recognized
- APB5 signals (`pwakeup`, `pauser`, `pwuser`, `pruser`, `pbuser`, `pnse`) not recognized
- Runtime errors when accessing these signals

**Expected Behavior**
APB4 and APB5 buses should properly inherit all optional signals and function correctly.

**Proposed Fix**
```python
# Fixed code:
optional_signals = self._optional_signals.copy()
optional_signals.extend(["pstrb", "pprot", "pslverr"])
```

**Environment**
- Python version: [Your Python version]
- cocotb version: [Your cocotb version]
- cocotbext-apb version: [Current version]

**Labels**
bug, high-priority, runtime-error
```

---

## Issue Template 2: Incorrect Byte Calculation Bug

### Title
`[Bug] Incorrect byte calculation in ApbBase class causing data corruption risk`

### Issue Body
```
**Bug Description**
The byte calculation in the `ApbBase` class is incorrect, dividing the bit width by 4 instead of 8 (bits per byte).

**Location**
- File: `cocotbext/apb/apb_base.py`
- Lines: 45-46

**Problem**
```python
# Buggy code:
self.rbytes = int(self.rwidth / 4)  # Should be 8 bits per byte
self.wbytes = int(self.wwidth / 4)  # Should be 8 bits per byte
```

**Impact**
- **Severity**: Medium-High
- Incorrect buffer sizes and memory calculations
- Data corruption risk during read/write operations
- Incorrect byte lane calculations
- Performance degradation due to wrong buffer sizes
- Potential memory access violations

**Expected Behavior**
Byte calculations should correctly reflect actual data sizes based on 8 bits per byte.

**Proposed Fix**
```python
# Fixed code:
self.rbytes = int(self.rwidth / 8)  # Correct: 8 bits per byte
self.wbytes = int(self.wwidth / 8)  # Correct: 8 bits per byte
```

**Steps to Reproduce**
1. Create an APB bus with any data width
2. Check the calculated `rbytes` and `wbytes` values
3. Observe they are 2x larger than expected

**Environment**
- Python version: [Your Python version]
- cocotb version: [Your cocotb version]
- cocotbext-apb version: [Current version]

**Labels**
bug, data-corruption, performance
```

---

## Issue Template 3: Address Range Boundary Security Bug

### Title
`[Security] Address range boundary condition allows unauthorized access to privileged memory`

### Issue Body
```
**Security Issue Description**
The address range check in `ApbSlave` has an off-by-one error that creates a security vulnerability allowing unauthorized access to boundary addresses of privileged/instruction memory regions.

**Location**
- File: `cocotbext/apb/apb_slave.py`
- Line: 74

**Problem**
```python
# Buggy code:
if addrs[0] <= address < addrs[1]:  # Upper boundary excluded
    raise exception
```

**Security Impact**
- **Severity**: High (Security Vulnerability)
- Unauthorized access to privileged memory regions
- Unauthorized access to instruction memory regions
- Bypass of APB protection mechanisms
- Potential system compromise in secure environments

**Attack Scenario**
An attacker could access address `addrs[1]` (upper boundary) without proper authorization, potentially reading/writing privileged data or executing unauthorized instructions.

**Expected Behavior**
All addresses in the range `[addrs[0], addrs[1]]` should be properly protected according to APB specification.

**Proposed Fix**
```python
# Fixed code:
if addrs[0] <= address <= addrs[1]:  # Upper boundary included
    raise exception
```

**Steps to Reproduce**
1. Configure a privileged address range `[0x1000, 0x1FFF]`
2. Attempt to access address `0x1FFF` without privileged permissions
3. Observe that access is allowed (security bypass)

**Environment**
- Python version: [Your Python version]
- cocotb version: [Your cocotb version]
- cocotbext-apb version: [Current version]

**Labels**
security, vulnerability, high-priority, privilege-escalation
```

---

## How to Submit These Issues

1. **Navigate to the repository**: https://github.com/daxzio/cocotbext-apb
2. **Go to Issues tab**: Click on "Issues" in the repository navigation
3. **Create New Issue**: Click the "New issue" button
4. **Copy and paste**: Use the templates above, filling in your specific environment details
5. **Add labels**: If you have permissions, add the suggested labels
6. **Submit**: Click "Submit new issue"

## Additional Notes

- **Check existing issues first**: Search the existing issues to make sure these bugs haven't already been reported
- **Consider creating a PR**: Since you already have the fixes, you might want to create a Pull Request instead of or in addition to the issues
- **Reference the fixes**: You can mention that you already have working fixes available
- **Be helpful**: Offer to help test or review any fixes the maintainers might propose

## Pull Request Option

Instead of just reporting issues, you could also create a Pull Request with the fixes:

1. Fork the repository
2. Create a new branch for your fixes
3. Apply the fixes I made
4. Create a Pull Request referencing the issues
5. Include the detailed explanations from the bug report

This approach is often more appreciated by maintainers as it provides both the problem identification and the solution.
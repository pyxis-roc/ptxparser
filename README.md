# ptxparser

A parser for NVIDIA's PTX virtual instruction set. Based on the PTX
6.5 specification, though note changes below.

This is **alpha** quality software. APIs and interfaces are subject to
change. Limitations are noted below.

## Installation

In a virtual environment (preferably), run:

```
make -C grammar
make -C ptxparser
python3 setup.py develop
```

No other method of installation beyond `develop` is supported right now.

## Usage

See `scripts/testparser.py` for an example of using the API.

## Testing

Assuming you have extracted a PTX file and it has been preprocessed
using `cpp` (this is true for PTX files embedded in binaries), the
following commands can run some sanity checks.

```
rtcheck_quick.sh ptxfile.ptx
```

This performs a round-trip test. Essentially, it parses `ptxfile.ptx`,
writing it out to a file `tmp1.ptx`. It then parses `tmp1.ptx` and
writes it out to `tmp2.ptx`. It then checks if `tmp1.ptx` and
`tmp2.ptx` are the same (using `diff`).

The command `rtcheck.sh` additionally runs `tmp2.ptx` through `ptxas`
to check for syntax errors.

TODO: The command `rtcheck_sass.sh` checks that the SASS assemblies of
`ptxfile.ptx` and `tmp1.ptx` are the same.

## Limitations

Syntax is limited to PTX 6.5, though support for some constructs beyond 6.5 is
supported.

Does not support `.section` directives whose section names start with
a `.`. This essentially causes the parser to break on PTX code that
contains debug information.

Behaves differently from `ptxas` in one notable aspect. By default,
`ptxas` accepts "modifiers" on opcodes in _any_ order contravening the
syntax specification. We intend to eventually support this behaviour.

import re

# The error raised when the dt file is invalid.
class DTDecodeError(Exception): pass

# Type aliases
_BOOL = 0
_BYTE = 1
_INT = 2
_SHORT = 3
_LONG = 4
_FLOAT = 5
_DOUBLE = 6
_CHAR = 7
_STRING = 8

# Tokenizer regular expression
_rx_tok = r";.*$|\"(?:[^\"\\]|\\.)*\"|\'\\?.\'|[\[\]{}:;]|[^\s\[\]{}:;]+"

# Key pattern
_rx_key = re.compile(r"^(?!true|false)(?:[_a-zA-Z][_a-zA-Z0-9]*)$")

# Value patterns
_rx_val = {
        _BOOL:     re.compile(r"^(true|false)$"),
        _BYTE:     re.compile(r"^0[xX]([0-9a-fA-F])+$"),
        _INT:      re.compile(r"^([0-9]+)$"),
        _SHORT:    re.compile(r"^([0-9]+)[sS]$"),
        _LONG:     re.compile(r"^([0-9]+)[lL]$"),
        _FLOAT:    re.compile(r"^([0-9]*\.[0-9]*)[fF]$"),
        _DOUBLE:   re.compile(r"^([0-9]*\.[0-9]*)$"),
        _CHAR:     re.compile(r"^'(\\?.)'$"),
        _STRING:   re.compile(r"^\"((?:[^\"\\]|\\.)*)\"$"),
    }
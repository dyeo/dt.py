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

# Returns a python-acceptable primitive from a datatag token
def _get_value(token):
    for k,v in _rx_val.items():
        match = re.match(v, token)
        if match:
            val = match.group(1)
            if not val:
                raise DTDecodeError(f"Unkown value type for value {state.tokens[state.iter]}")
            if k == _BOOL:
                val = val == "true"
            elif k in {_BYTE,_INT,_SHORT,_LONG}:
                val = int(val, 16 if k == "byte" else 10)
            elif k in {_FLOAT, _DOUBLE}:
                val = float(val)       
            else:
                val = str(val.encode("utf-8").decode("unicode_escape"))
            return val
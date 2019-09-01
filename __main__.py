import re

# The internal state of the parser.
class __State(object):
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.iter = 0
        self.objects = list()
        self.objects.append(dict())
        self.mode = ""
        self.keys = list({""})

class SyntaxError(Exception): pass

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

# Regular expressions
_rx_tokenize = r";.*$|\"(?:[^\"\\]|\\.)*\"|\'\\?.\'|[\[\]{}:;]|[^\s\[\]{}:;]+"
_rx_key = re.compile(r"^(?!true|false)(?:[_a-zA-Z][_a-zA-Z0-9]*)$")
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

# Converts a datatag string into a list of acceptable tokens.
def _tokenize(s):
    tokens = list()
    matches = re.finditer(_rx_tokenize, s, re.MULTILINE)
    for _, match in enumerate(matches, start=1):
        token = match.group()
        if token and (not token[0] == ';'):
            tokens.append(token)
    return tokens

# Parses a token list into an acceptable dict containing datatag values.
def _parse(tokens):
    state = __State(tokens)
    while state.iter < len(state.tokens):
        state = __parseNext(state)
    return state.objects[0]

# Returns a python-acceptable value from a given token string.
def __get_value(token):
    for k,v in _rx_val.items():
        match = re.match(v, token)
        if match:
            val = match.group(1)
            if not val:
                raise SyntaxError(f"Unkown value type for value {state.tokens[state.iter]}")
            if k == _BOOL:
                val = val == "true"
            elif k in {_BYTE,_INT,_SHORT,_LONG}:
                val = int(val, 16 if k == "byte" else 10)
            elif k in {_FLOAT, _DOUBLE}:
                val = float(val)       
            else:
                val = str(val.encode("utf-8").decode("unicode_escape"))
            return val

# Advances the parser state.
def __continue(state: __State, steps):
    state.iter += steps;
    return state;

# Enters the current parser scope, whether it's an array or object.
def __enter_scope(state: __State, type):
    state.objects.append(type())
    if type == list:
        state.mode = 'a' # awaiting array values
    elif type == dict:
        state.keys.append("")
        state.mode = ''
    return state

# Exits the current parser scope, whether it's an array or object.
def __exit_scope(state: __State):
    if isinstance(state.objects[-1], dict):
        state.keys.pop()
    popped = state.objects.pop()
    if isinstance(state.objects[-1], dict):
        if not state.keys[-1]: raise SyntaxError(f"Value {popped} is preceeded by an empty or invalid key")
        state.objects[-1][state.keys[-1]] = popped
        state.keys[-1] = ""
        state.mode = ''
    else:#isinstance(s.objects[-1], list):
        state.objects[-1].append(popped)
        state.mode = 'a'
    return state

# Parses the next token in order to construct the data set.
def __parseNext(state: __State):
    token = state.tokens[state.iter]
    key = re.match(_rx_key, token)
    if state.mode == '' and key:
        if state.tokens[state.iter+1] == ':':
            state.mode = 'v' # awaiting a value
            state.keys[-1] = token
            return __continue(state, 2)
        else:
            raise SyntaxError(f"Key {token} not proceeded by an assignment")
    if token == '[':
        state = __enter_scope(state, list)
        return __continue(state, 1)
    if token == '{':
        state = __enter_scope(state, dict)
        return __continue(state, 1)
    if token in {']', '}'}:
        state = __exit_scope(state)
        return __continue(state, 1)
    if state.mode == 'v' and not key:
        state.objects[-1][state.keys[-1]] = __get_value(token)
        state.mode = ''
        return __continue(state, 1)
    if state.mode == 'a' and not key:
        state.objects[-1].append(__get_value(token))
        return __continue(state, 1)
    raise SyntaxError(f"Invalid token {token}")

def load(fp):
    """Loads a python filestream containing a datatag file into python objects representing the dataset.
    Returns a dict containing the dataset, as key value pairs corresponding to their representation in the datatag file."""
    return _parse(_tokenize(fp.dump()))

def loads(s):
    """Loads a string containing a datatag file into python objects representing the dataset.
    Returns a dict containing the dataset, as key value pairs corresponding to their representation in the datatag file."""
    return _parse(_tokenize(s))

#for k,v in loads("a: [ 1 2 3 ]").items():
#    print(f"{k}: {v}")
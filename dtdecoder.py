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

# The internal state of the parser.
class DTDecoder(object):
    # DTParser constructor.
    def __init__(self):
        self.iter = 0
        self.objects = list()
        self.objects.append(dict())
        self.mode = ""
        self.keys = list([""])
    
    # Regular expressions
    _rx_tok = r";.*$|\"(?:[^\"\\]|\\.)*\"|\'\\?.\'|[\[\]{}:;]|[^\s\[\]{}:;]+"
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
    
    def decode(self, s):
        self.tokenize(s)
        return self.parse()

    # Converts a datatag string into a list of acceptable tokens.
    def tokenize(self, s):
        self.tokens = list()
        matches = re.finditer(self._rx_tok, s, re.MULTILINE)
        for _, match in enumerate(matches, start=1):
            token = match.group()
            if token and (not token[0] == ';'):
                self.tokens.append(token)
    
    # Parses a token list into an acceptable dict containing datatag values.
    def parse(self):
        while self.iter < len(self.tokens):
            self._parse_next()
        return self.objects[0]
    
    # Returns a python-acceptable value from a given token string.
    def _get_value(self, token):
        for k,v in self._rx_val.items():
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
    
    # Advances the parser state.
    def _continue(self, steps):
        self.iter += steps;
    
    # Enters the current parser scope, whether it's an array or object.
    def _enter_scope(self, type):
        self.objects.append(type())
        if type == list:
            self.mode = 'a' # awaiting array values
        elif type == dict:
            self.keys.append("")
            self.mode = ''
    
    # Exits the current parser scope, whether it's an array or object.
    def _exit_scope(self):
        if isinstance(self.objects[-1], dict):
            self.keys.pop()
        popped = self.objects.pop()
        if isinstance(self.objects[-1], dict):
            if not self.keys[-1]: raise DTDecodeError(f"Value {popped} is preceeded by an empty or invalid key")
            self.objects[-1][self.keys[-1]] = popped
            self.keys[-1] = ""
            self.mode = ''
        else:#isinstance(s.objects[-1], list):
            self.objects[-1].append(popped)
            self.mode = 'a'
    
    # Parses the next token in order to construct the data set.
    def _parse_next(self):
        token = self.tokens[self.iter]
        key = re.match(self._rx_key, token)
        if self.mode == '' and key:
            if self.tokens[self.iter+1] == ':':
                self.mode = 'v' # awaiting a value
                self.keys[-1] = token
                self._continue(2)
            else:
                raise DTDecodeError(f"Key {token} not proceeded by an assignment")
        elif token == '[':
            self._enter_scope(list)
            self._continue(1)
        elif token == '{':
            self._enter_scope(dict)
            self._continue(1)
        elif token in {']', '}'}:
            self._exit_scope()
            self._continue(1)
        elif self.mode == 'v' and not key:
            self.objects[-1][self.keys[-1]] = self._get_value(token)
            self.mode = ''
            _continue(1)
        elif self.mode == 'a' and not key:
            self.objects[-1].append(self._get_value(token))
            self._continue(1)
        else:
            raise DTDecodeError(f"Invalid token {token}")
import re
from dtdecoderutils import DTDecodeError
from dtdecoderutils import _BOOL, _BYTE, _INT, _SHORT, _LONG, _FLOAT, _DOUBLE, _CHAR, _STRING
from dtdecoderutils import _rx_tok, _rx_key, _rx_val

# The internal state of the parser.
class DTDecoder(object):

    # DTParser constructor.
    def __init__(self, objo):
        self.decode_to_class = objo
        self.iter = 0
        self.objects = list()
        self.objects.append(dict())
        self.mode = ''
        self.keys = list([""])

    def decode(self, s):
        """
        Return the Python representation of s (a str instance containing a Datatag document).
        DTDecodeError will be raised if the given Datatag document is not valid.
        """
        self._tokenize(s)
        return self._parse()

    # Converts a datatag string into a list of acceptable tokens.
    def _tokenize(self, s):
        self.tokens = list()
        matches = re.finditer(_rx_tok, s, re.MULTILINE)
        for _, match in enumerate(matches, start=1):
            token = match.group()
            if token and (not token[0] == ';'):
                self.tokens.append(token)
    
    # Parses a token list into an acceptable dict containing datatag values.
    def _parse(self):
        while self.iter < len(self.tokens):
            self._parse_next()
        return self.objects[0]
    
    # Returns a python-acceptable value from a given token string.
    def _get_value(self, token):
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
    
    # Advances the parser state.
    def _continue(self, steps):
        self.iter += steps;

    # Defines a key to be assigned to.
    def _define_key(self, token):
        if self.tokens[self.iter+1] == ':':
            self.mode = 'v' # awaiting a value
            self.keys[-1] = token
            self._continue(2)
        else:
            raise DTDecodeError(f"Key {token} not proceeded by an assignment")
    
    # Enters the current parser scope, whether it's an array or object.
    def _enter_scope(self, token):
        if token == '[':
            self.objects.append(list())
            self.mode = 'a' # awaiting array values
        elif token == '{':
            self.objects.append(dict())
            self.keys.append("")
            self.mode = ''
        self._continue(1)
    
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
        self._continue(1)
    
    # Assigns a primitive to a key.
    def _assign_primitive(self, token):
        self.objects[-1][self.keys[-1]] = self._get_value(token)
        self.mode = ''
        self._continue(1)

    # Appends a primitive to an array.
    def _append_primitive(self, token):
        self.objects[-1].append(self._get_value(token))
        self._continue(1)
        
    # Parses the next token in order to construct the data set.
    def _parse_next(self):
        token = self.tokens[self.iter]
        key = re.match(_rx_key, token)
        if self.mode == '' and key:
            self._define_key(token)
        elif token in {'[', '{'}:
            self._enter_scope(token)
        elif token in {']', '}'}:
            self._exit_scope()
        elif self.mode == 'v' and not key:
            self._assign_primitive(token)
        elif self.mode == 'a' and not key:
            self._append_primitive(token)
        else:
            raise DTDecodeError(f"Invalid token {token}")
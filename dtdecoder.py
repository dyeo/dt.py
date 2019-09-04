import re
from dtdecoderutils import DTDecodeError
from dtdecoderutils import _BOOL, _BYTE, _INT, _SHORT, _LONG, _FLOAT, _DOUBLE, _CHAR, _STRING
from dtdecoderutils import _rx_tok, _rx_key, _rx_val, _get_value

class DTDecoder(object):
    """
    The object responsible for decoding datatag files into an acceptable python representation of their data.
    """

    # DTParser constructor.
    def __init__(self, decode_class, loose_arrays):
        # Configuration settings
        self.decode_class = decode_class
        self.loose_arrays = loose_arrays
        # State variables
        self.iter = 0
        self.objects = list()
        if decode_class:
            self.objects.append(decode_class())
        else:
            self.objects.append(dict())
        self.mode = ''
        self.keys = list([""])
        self.types = list()

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
        if len(self.objects) > 1:
            raise DTDecodeError(f"Invalid termination of scope for object {self.objects[-1]}")
        return self.objects[0]
    
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
            if not self.loose_arrays:
                self.types.append(None)
            self.objects.append(list())
            self.mode = 'a' # awaiting array values
        elif token == '{':
            if not self.decode_class or isinstance(self.objects[-1], dict) or isinstance(self.objects[-1], list) or isinstance(getattr(self.objects[-1], self.keys[-1], None), dict):
                self.objects.append(dict())
            else:
                self.objects.append(getattr(self.objects[-1], self.keys[-1]))
            self.keys.append("")
            self.mode = ''
        self._continue(1)
    
    # Exits the current parser scope, whether it's an array or object.
    def _exit_scope(self, token):
        if len(self.objects) <= 1:
            raise DTDecodeError(f"Unexpected token {token}")
        is_object = not isinstance(self.objects[-1], list)
        if token == ']' and is_object or token == '}' and not is_object:
            raise DTDecodeError(f"Invalid termination of scope for object {self.objects[-1]}")
        elif is_object:
            self.keys.pop()
        elif not self.loose_arrays:
            self.types.pop()
        popped = self.objects.pop()
        if not isinstance(self.objects[-1], list):
            if not self.keys[-1]:
                raise DTDecodeError(f"Value {popped} is preceeded by an empty or invalid key")
            self._assign_primitive(popped)
            self.mode = ''
        else:#isinstance(s.objects[-1], list):
            self._append_primitive(popped)
            self.mode = 'a'
    
    # Assigns a primitive to a key.
    def _assign_primitive(self, value):
        if self.decode_class and not isinstance(self.objects[-1], dict):
            setattr(self.objects[-1], self.keys[-1], value)
        else:
            self.objects[-1][self.keys[-1]] = value
        self.keys[-1] = ""
        self.mode = ''
        self._continue(1)

    # Appends a primitive to an array.
    def _append_primitive(self, value):
        if not self.loose_arrays:
            if self.types[-1] is None:
                self.types[-1] = type(value)
            elif self.types[-1] is not type(value):
                raise DTDecodeError(f"Array element {value} has mismatched type")
        self.objects[-1].append(value)
        self.mode = 'a'
        self._continue(1)
        
    # Parses the next token in order to construct the data set.
    def _parse_next(self):
        token = self.tokens[self.iter]
        key = re.match(_rx_key, token)
        if self.mode == '' and key:
            self._define_key(token)
        elif token in "[{":
            self._enter_scope(token)
        elif token in "]}":
            self._exit_scope(token)
        elif self.mode == 'v' and not key:
            self._assign_primitive(_get_value(token))
        elif self.mode == 'a' and not key:
            self._append_primitive(_get_value(token))
        else:
            raise DTDecodeError(f"Unexpected token {token}")
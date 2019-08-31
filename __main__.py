import re

class SyntaxError(Exception): pass

_rx_tokenize = r";.*$|\"(?:[^\"\\]|\\.)*\"|\'\\?.\'|[\[\]{}:;]|[^\s\[\]{}:;]+"

_rx_key = re.compile(r"^(?!true|false)(?:[_a-zA-Z][_a-zA-Z0-9]*)$")

_val = {
        "bool":     r"(true|false)",
        "byte":     r"0[xX]([0-9a-fA-F])+",
        "int":      r"([0-9]+)",
        "short":    r"([0-9]+)[sS]",
        "long":     r"([0-9]+)[lL]",
        "float":    r"([0-9]*\.[0-9]*)[fF]",
        "double":   r"([0-9]*\.[0-9]*)",
        "char":     r"'(\\?.)'",
        "string":   r"\"((?:[^\"\\]|\\.)*)\"",
    }
for k,v in _val.items(): _val[k] = re.compile('^' + v + '$')

def _tokenize(file):
    tokens = list()
    matches = re.finditer(_rx_tokenize, file, re.MULTILINE)
    for _, match in enumerate(matches, start=1):
        token = match.group()
        if token and (not token[0] == ';'):
            tokens.append(token)
    return tokens

# the state of the parser
class _pstate(object):
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.iter = 0
        self.objects = list()
        self.objects.append(dict())
        self.mode = ""
        self.keys = list({""})

def _parse(tokens):
    state = _pstate(tokens)
    while state.iter < len(state.tokens):
        state = _parseNext(state)
    return state.objects[0]

def _get_value(s: _pstate):
    for k,v in _val.items():
        match = re.match(v, s.tokens[s.iter])
        if match:
            val = match.group(1)
            if not val:
                raise SyntaxError(f"Unkown value type for value {s.tokens[s.iter]}")
            if k == "bool":
                val = val == "true"
            elif k in {"byte","int","short","long"}:
                val = int(val, 16 if k == "byte" else 10)
            elif k in {"float", "double"}:
                val = float(val)       
            else:
                val = str(val.encode("utf-8").decode("unicode_escape"))
            return val

def _parseNext(s: _pstate):
    is_key = re.match(_rx_key, s.tokens[s.iter])
    if s.mode == '' and is_key:
            if s.tokens[s.iter+1] == ':':
                s.mode = 'v' # awaiting a value
                s.keys[-1] = s.tokens[s.iter]
                s.iter += 2
                return s
            else:
                raise SyntaxError(f"Key {s.tokens[s.iter]} not proceeded by an assignment")
    if s.tokens[s.iter] == '[':
        s.objects.append(list())
        s.mode = 'a'
        s.iter += 1
        return s
    if s.tokens[s.iter] == ']':
        popped = s.objects.pop()
        if isinstance(s.objects[-1], dict):
            s.objects[-1][s.keys[-1]] = popped
            s.mode = ''
        else:#isinstance(s.objects[-1], list):
            s.objects[-1].append(popped)
            s.mode = 'a'
        s.mode = ''
        s.iter += 1
        return s
    if s.tokens[s.iter] == '{':
        s.keys.append("")
        s.objects.append(dict())
        s.mode = ''
        s.iter += 1
        return s
    if s.tokens[s.iter] == '}':
        popped = s.objects.pop()
        s.keys.pop()
        if isinstance(s.objects[-1], dict):
            s.objects[-1][s.keys[-1]] = popped
            s.mode = ''
        else:#isinstance(s.objects[-1], list):
            s.objects[-1].append(popped)
            s.mode = 'a'
        s.iter += 1
        return s
    if s.mode == 'v' and not is_key:
        s.objects[-1][s.keys[-1]] = _get_value(s)
        s.mode = ''
        s.iter += 1
        return s
    if s.mode == 'a' and not is_key:
        s.objects[-1].append(_get_value(s))
        s.iter += 1
        return s
    raise SyntaxError(f"Invalid token {s.tokens[s.iter]}")

def load(file):
    return _parse(_tokenize(file))
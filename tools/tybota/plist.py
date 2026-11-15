"""Minimal read-only parser for the Glyphs (OpenStep-style) plist format."""
import re

_UNQUOTED = re.compile(r'[A-Za-z0-9_.\-+/$:]+')
_NUM = re.compile(r'^-?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?$')


class Parser:
    def __init__(self, text):
        self.s = text
        self.i = 0
        self.n = len(text)

    def ws(self):
        s, n = self.s, self.n
        while self.i < n:
            c = s[self.i]
            if c in ' \t\r\n':
                self.i += 1
            elif c == '/' and self.i + 1 < n and s[self.i + 1] == '*':
                self.i = s.index('*/', self.i) + 2
            elif c == '/' and self.i + 1 < n and s[self.i + 1] == '/':
                j = s.find('\n', self.i)
                self.i = n if j < 0 else j
            else:
                break

    def value(self):
        self.ws()
        c = self.s[self.i]
        if c == '{':
            return self.dict_()
        if c == '(':
            return self.list_()
        if c == '"':
            return self.qstring()
        if c == '<':
            j = self.s.index('>', self.i)
            v = self.s[self.i:j + 1]
            self.i = j + 1
            return v
        m = _UNQUOTED.match(self.s, self.i)
        if not m:
            raise ValueError('unexpected %r at %d: %r' % (c, self.i, self.s[self.i:self.i + 40]))
        self.i = m.end()
        tok = m.group(0)
        if _NUM.match(tok):
            f = float(tok)
            return int(f) if f == int(f) and '.' not in tok and 'e' not in tok.lower() else f
        return tok

    def qstring(self):
        s = self.s
        self.i += 1
        out = []
        while True:
            c = s[self.i]
            if c == '"':
                self.i += 1
                break
            if c == '\\':
                self.i += 1
                d = s[self.i]
                if d == 'n':
                    out.append('\n')
                elif d == 't':
                    out.append('\t')
                elif d == 'U' or d == 'u':
                    out.append(chr(int(s[self.i + 1:self.i + 5], 16)))
                    self.i += 4
                elif d.isdigit():
                    m = re.match(r'[0-7]{1,3}', s[self.i:self.i + 3])
                    out.append(chr(int(m.group(0), 8)))
                    self.i += len(m.group(0)) - 1
                else:
                    out.append(d)
                self.i += 1
            else:
                out.append(c)
                self.i += 1
        return ''.join(out)

    def dict_(self):
        self.i += 1
        d = {}
        while True:
            self.ws()
            if self.s[self.i] == '}':
                self.i += 1
                return d
            k = self.value()
            self.ws()
            if self.s[self.i] != '=':
                raise ValueError('expected = at %d: %r' % (self.i, self.s[self.i - 20:self.i + 20]))
            self.i += 1
            v = self.value()
            self.ws()
            if self.s[self.i] == ';':
                self.i += 1
            d[str(k)] = v

    def list_(self):
        self.i += 1
        out = []
        while True:
            self.ws()
            if self.s[self.i] == ')':
                self.i += 1
                return out
            out.append(self.value())
            self.ws()
            if self.s[self.i] == ',':
                self.i += 1


def load(path):
    with open(path, encoding='utf-8') as fh:
        return Parser(fh.read()).value()

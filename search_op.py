import re
from functools import reduce

# X Y -> X and Y

from enum import Enum


quote_symbols = '«»"\''


class Term:
    def __init__(self, regex):
        self.regex = regex

    # "X Y" -> X Y
    def op_quote(self):
        return Term(self.regex.translate(quote_symbols))

    # X and Y -> (?=.*X)(?=.*Y).*
    def op_and(self, other, n=None):
        return Term(f'(?=.*{self.regex})(?=.*{other.regex}).*')

    # X or Y -> X|Y
    def op_or(self, other, n=None):
        return Term(f'{self.regex}|{other.regex}')

    # X nD Y: X(?: \S+){0,n} Y|Y(?: \S+){0,n} X
    def op_d(self, other, n):
        return Term(f'{self.regex}(?: \\S+){{0,{n}}} {other.regex}|'
                    f'{other.regex}(?: \\S+){{0,{n}}} {self.regex}')

    # X nW Y: X(?: \S+){n} Y
    def op_w(self, other, n):
        return Term(f'{self.regex}(?: \\S+){{{n}}} {other.regex}')

    # X+ -> X\S*
    def op_plus(self):
        return Term(f'{self.regex.replace("+", "")}\\S*')

    def invoke_by_op(self, op, other, arg):
        if op == Operations.W:
            return self.op_w(other, arg)
        elif op == Operations.D:
            return self.op_d(other, arg)
        elif op == Operations.AND:
            return self.op_and(other)
        elif op == Operations.OR:
            return self.op_or(other)

    def __str__(self):
        return self.regex

    def __repr__(self):
        return self.regex


class Operation:
    def __init__(self, op, arg=None):
        self.op = op
        self.arg = arg

    def __str__(self):
        if self.arg:
            return f'{self.op}({self.arg})'
        return f'{self.op}'

    def __repr__(self):
        return self.__str__()


class Operations(Enum):
    W = 1
    D = 2
    AND = 3
    OR = 4


def get_op(string):
    if string == 'and':
        return Operation(Operations.AND)
    if string == 'or':
        return Operation(Operations.OR)
    if re.match(r'^\d+w$', string):
        return Operation(Operations.W, re.findall(r'\d+', string)[0])
    if re.match(r'^\d+d$', string):
        return Operation(Operations.D, re.findall(r'\d+', string)[0])
    return None


def is_normalized(string):
    if any(x in string for x in string):
        return True
    if ' ' in string:
        return False
    return True


def join_term(terms, ops):
    offset = 0

    for operation in Operations:
        for i, op in enumerate(ops):
            if op.op is operation:
                terms[i - offset] = terms[i - offset].invoke_by_op(operation, terms[i - offset + 1], op.arg)
                terms.pop(i - offset + 1)
                offset += 1

    return terms[0].regex


def parse_string(string):
    split = re.findall(r'[^"\s]\S*|".+?"', string.lower())
    arr = []
    for i, s in enumerate(split):
        if arr and not get_op(arr[-1]) and not get_op(s):
            arr.append('and')
            arr.append(s)
        else:
            arr.append(s)

    terms = []
    ops = []
    for word in arr:
        op = get_op(word)
        if op:
            ops.append(op)
        else:
            term = Term(word).op_quote()
            if '+' in word:
                term = term.op_plus()

            terms.append(term)

    return join_term(terms, ops)

test_company_names = '''increase
increasing
increment
decreasing increasing lala
fracture
frac
factorial
height
high
restriction
restructure
fracture height
increasing fracture
fuck incr incr aaa
fracture height restriction
restriction of fracture height
restriction due to fracture height
fracture height'''


if __name__ == '__main__':
    while True:
        cmd = input()
        result_regex = parse_string(cmd)
        print(result_regex)
        print(re.findall(result_regex, test_company_names))

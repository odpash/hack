import json
import re
from functools import reduce

# X Y -> X and Y

from enum import Enum


quote_symbols = '«»"\''
P_LINK, P_TITLE, P_DESCR, P_AUTHOR, P_OWNER, P_YEAR = range(6)


class Term:
    def __init__(self, regex):
        self.regex = regex

    # "X Y" -> \bX Y\b
    def op_quote(self):
        s = self.regex
        for q in quote_symbols:
            s = s.replace(q, '')
        return Term(f'\\b{s}\\b')

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


with open('okved_groups.json', encoding='utf8') as file:
    groups = json.loads(file.read())
    categories = list(groups.keys())
    classes = []
    subclasses = []
    for c in categories:
        for d in groups[c]:
            for cl in d:
                classes.append(cl)
                for scl in d[cl]:
                    subclasses.append(scl)

    classes_sub = '\n'.join(classes)
    subclasses_sub = '\n'.join(subclasses)


def is_okved(regex):
    if re.search(regex, classes_sub, re.IGNORECASE):
        return 1
    elif re.search(regex, subclasses_sub, re.IGNORECASE):
        return 2
    return 0


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

    # print(ops)
    # print(list(Operations))

    for operation in Operations:
        for i, op in enumerate(ops):
            if op.op is operation:
                terms[i - offset] = terms[i - offset].invoke_by_op(operation, terms[i - offset + 1], op.arg)
                terms.pop(i - offset + 1)
                if len(terms) != i - offset + 1:
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
            term = Term(word)
            if any(q in word for q in quote_symbols):
                term = term.op_quote()
            elif '+' in word:
                term = term.op_plus()

            terms.append(term)

    return join_term(terms, ops)


def get_companies_by_query(query, companies):
    result = []
    regex = parse_string(query)
    check_okved = is_okved(regex)
    for company in companies:
        if re.search(regex, company['company_name'], re.IGNORECASE):
            result.append(company)
        # Дополнительно по ОКВЭД'ам
        elif check_okved:
            for num, name in company['activity']:
                if re.search(regex, name, re.IGNORECASE):
                    result.append(company)

    return result


def get_patents_by_query(query, patents):
    result = []
    regex = parse_string(query)
    for patent in patents:
        if re.search(regex, patent[P_TITLE], re.IGNORECASE) or re.search(regex, patent[P_DESCR], re.IGNORECASE):
            result.append(patent)

    return result


company_list = '''increase
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
fracture height'''.splitlines()


def generate_test_companies():
    return [{'company_name': s} for s in company_list]


if __name__ == '__main__':
    test_companies = generate_test_companies()
    while True:
        cmd = input()
        print(get_companies_by_query(cmd, test_companies))

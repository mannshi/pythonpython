import sys
from enum import Enum
from enum import IntEnum, auto

class TokenKind(Enum):
    TK_RESERVED =  auto()
    TK_IDENT    =  auto()
    TK_NUM      =  auto()
    TK_EOF      =  auto()
    TK_RETURN   =  auto()
    TK_WHILE    =  auto()
    IF          =  auto()
    ELSE        =  auto()
    TK_FOR      =  auto()

tk_reserved_list = [ '+' , '-' , '*' , '/' , '(' , ')',
                     '==', '!=', '>', '>=', '<', '<=',
                     '=',
                     ';'
                   ]

tkn = []
code = []
lvars = {}
offset = 0

class NodeKind(Enum):
    ND_ADD   = auto()
    ND_SUB   = auto()
    ND_MUL   = auto()
    ND_DIV   = auto()
    ND_NUM   = auto()
    ND_EQU   = auto()  # '=='
    ND_NEQ   = auto()  # '!='
    ND_LT    = auto()  # '<'
    ND_LTE   = auto()  # '<='
    ND_ASSIGN = auto() # '='
    ND_LVAR = auto()
    ND_RETURN = auto()
    IF = auto()
    ELSE = auto()
    BLOCK = auto()
    FUNC = auto()

class Token:
    def __init__(self):
        self.kind = 0
        self.val = 0
        self.str = ''

class Node:
    def __init__(self):
        self.kind = 0
        self.lhs = 0
        self.rhs = 0
        self.val = 0 # kindがND_NUMの場合のみ使う
        self.offset = 0 # kindがND_LVARの場合のみ使う

class NodeIF:
    def __init__(self):
        self.kind = 0
        self.expr = 0
        self.truebl = 0
        self.elsebl = 0

class NodeBLOCK:
    def __init__(self):
        self.kind = 0
        self.stmts = []

class NodeFUNC:
    def __init__(self):
        self.kind = 0
        self.name = 0
        self.para = [] 


# 辞書を使うなら必要ない？
class cLVar:
    def __init__(self):
        self.name = ''
        self.offset = 0
    

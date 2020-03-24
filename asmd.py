import sys
from enum import Enum
from enum import IntEnum, auto

class TokenKind(Enum):
    TK_RESERVED =  auto()
    TK_IDENT    =  auto()
    TK_NUM      =  auto()
    TK_EOF      =  auto()

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

# 辞書を使うなら必要ない？
class cLVar:
    def __init__(self):
        self.name = ''
        self.offset = 0
    

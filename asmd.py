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
    INT         =  auto()
    SIZEOF      =  auto()

tk_reserved_list = [ '+' , '-' , '*' , '/' , '(' , ')',
                     '==', '!=', '>', '>=', '<', '<=',
                     '=',
                     ';'
                   ]

tkn = []
code = []
glvars = {}  #グローバル変数用
llvars = {}  #スコープ（関数）毎にこの変数に代入する
llvars_t = {} 
offset = 0
functions = []

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
    FUNCDEF = auto()
    ADDR = auto()
    DEREF = auto()

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
        self.type = 0

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

class NodeFUNCCALL:
    def __init__(self):
        self.kind = 0
        self.name = 0
        self.para = [] 

class typ(Enum):
    INT   = auto()
    PTR   = auto()

class myType:
    def __init__(self):
        self.ty = typ.INT;
        self.ptr_to = 0;

class NodeFUNCDEF:
    def __init__(self):
        self.kind = 0
        self.name = 0
        self.type = 0
        self.lvars = {} # 変数名　と　offset
        self.lvars_t = {} # 変数名　と　型
        self.offset = 0
        self.block = []  # 関数本体（ブロックといっしょ）
        self.para = [] # 引数の変数名を保存する lvars は辞書で実装しているため、順序をもてないので、別に用意する
        self.paranum = 0
        self.param_offset = []

# 辞書を使うなら必要ない？
class cLVar:
    def __init__(self):
        self.name = ''
        self.offset = 0
    
class ManncError(Exception) : pass

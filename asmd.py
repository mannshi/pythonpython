import sys
from enum import Enum
from enum import IntEnum, auto

class TokenKind(Enum):
    RESERVED =  auto()
    IDENT    =  auto()
    NUM      =  auto()
    EOF      =  auto()
    RETURN   =  auto()
    WHILE    =  auto()
    IF       =  auto()
    ELSE     =  auto()
    TK_FOR   =  auto()
    INT      =  auto()
    SIZEOF   =  auto()

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
llvars_s = {} 
offset = 0
functions = []

class NodeKind(Enum):
    ADD   = auto()
    SUB   = auto()
    MUL   = auto()
    DIV   = auto()
    NUM   = auto()
    EQU   = auto()  # '=='
    NEQ   = auto()  # '!='
    LT    = auto()  # '<'
    LTE   = auto()  # '<='
    ASSIGN = auto() # '='
    LVAR = auto()
    RETURN = auto()
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
        self.size = 0

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
    ARRAY = auto()

class myType:
    def __init__(self):
        self.ty = typ.INT;
        self.ptr_to = 0;
        self.array_size = 0; # 配列の要素数（バイト数ではない？）

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

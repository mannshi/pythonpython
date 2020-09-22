import sys
from enum import Enum
from enum import IntEnum, auto
import pprint
import inspect

class TokenKind(Enum):
    RESERVED =  auto()
    IDENT    =  auto()
    NUM      =  auto()
    EOF      =  auto()
    RETURN   =  auto()
    WHILE    =  auto()
    SWITCH   =  auto()
    CASE     =  auto()
    BREAK    =  auto()
    CONTINUE =  auto()
    IF       =  auto()
    ELSE     =  auto()
    TK_FOR   =  auto()
    INT      =  auto()
    INT2     =  auto()
    CHAR     =  auto()
    STRUCT   =  auto()
    SIZEOF   =  auto()
    STRING   =  auto()

tkn = []
code = []

strings = [] #文字列を格納する配列
strings_i  = 0 #カウンタ


#######################################################
#   リファクタリング
#######################################################

class StorageClas(Enum):
    TYPEDEF = auto()
    #STATIC  = auto()
    #EXTERN  = auto()

class Type2:
    def __init__( self, kind, size, align, is_complete, base, array_len, members, return_ty ):
        self.kind = kind
        self.size = size
        self.align = align
        self.is_complete = is_complete
        self.base = base
        self.array_len = array_len
        self.members = members
        self.return_ty = return_ty

class Var2:
    #def __init__( self ):
    def __init__( self, name, ty, is_local, offset, is_static, initializer ):
        self.name = name
        self.ty = ty
        self.is_local = is_local
        self.offset = offset
        self.is_static = is_static
        self.initializer = initializer


#######################################################
#   リファクタリング
#######################################################

class TypeType:
    def __init__(self, kind, size, align, array_len, base, function):
        self.kind = kind
        self.size = size
        self.align = align
        self.array_len = array_len
        self.base  = base # pointer or array
        self.function = function
    def myself(self):
        print('#kind={0} size={1} align={2} array_len={3} base={4}'.format(self.kind, self.size, self.align, self.array_len, self.base))

class MYVar:
    def __init__( self ):
        #ref self.name = 0
        #self.type = 0
        self.offet = 0

#glvars = {}  #グローバル変数用
glvars_t = {}

lvars   = {}
lvars_t = {}

offset = 0

functions = []

strings = {} 
string_i = 0

current_switch = 0

class NodeKind(Enum):
    NOP      = auto()
    ADD      = auto()
    SUB      = auto()
    MUL      = auto()
    DIV      = auto()
    NUM      = auto()
    MEMBER   = auto()  # 構造体の'. '
    ARROW    = auto()  # 構造体の'->'
    EQU      = auto()  # '=='
    NEQ      = auto()  # '!='
    LT       = auto()  # '<'
    LTE      = auto()  # '<='
    ASSIGN   = auto()  # '='
    LVAR     = auto()
    LVAR2    = auto()
    RETURN   = auto()
    IF       = auto()
    WHILE    = auto()
    SWITCH   = auto()
    CASE     = auto()
    BREAK    = auto()
    CONTINUE = auto()
    ELSE     = auto()
    BLOCK    = auto()
    FUNC     = auto()
    FUNCDEF  = auto()
    ADDR     = auto()
    DEREF    = auto()
    STRING   = auto()
    PTR_ADD  = auto()

class Token:
    def __init__(self):
        self.kind = 0
        self.val = 0
        self.str = ''
        self.strid = 0

    def myself(self):
        print('#kind={0:20} val={1:5}, str={2:10}'.format(self.kind, self.val, self.str))
        return

class Node:
    def __init__(self):
        self.name2 = 0
        self.kind = 0
        self.lhs = 0
        self.rhs = 0
        self.val = 0 # kindがND_NUMの場合のみ使う/STRING の場合は文字列のIDとする
        self.offset = 0 # kindがND_LVARの場合のみ使う
        self.type = 0
        self.size = 0

class NodeIF:
    def __init__(self):
        self.kind = 0
        self.expr = 0
        self.truebl = 0
        self.elsebl = 0

class NodeSWITCH:
    def __init__(self):
        self.kind = 0
        self.expr = 0
        self.block = 0
        self.case_next = 0
        self.case_label = 0
        self.default_case = 0

class NodeCASE:
    def __init__(self):
        self.kind = 0
        self.val = 0
        self.block = 0
        self.case_next = 0

class NodeWHILE:
    def __init__(self):
        self.kind = 0
        self.expr = 0
        self.block = 0

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
    INT    = auto()
    INT2   = auto()
    CHAR   = auto()
    PTR    = auto()
    ARRAY  = auto()
    STRUCT = auto()

class myType:
    def __init__(self):
        self.ty = typ.INT;
        # 配列以外なら size = align だが
        # 配列なら、align はその型のsizeになる 
        # int num[100] は、800に整列しなくていいため
        self.align = 0;
        self.size = 0;
        self.ptr_to = 0;
        self.array_size = 0; # 配列の要素数（バイト数ではない？）

class NodeFUNCDEF:
    def __init__(self):
        self.kind = 0
        self.name = 0
        self.type = 0
        self.lvars = {} # 変数名　と　offset
        self.lvars2 = {} # 変数名　と　offset リファクタリング用
        self.lvars_t = {} # 変数名　と　型
        self.offset = 0
        self.block = []  # 関数本体（ブロックといっしょ）
        self.para = [] # 引数の変数名を保存する lvars は辞書で実装しているため、順序をもてないので、別に用意する
        self.paranum = 0
        self.param_offset = []

    def myself(self):
        print('#PRINTFUNC START')
        print('#name = {0} kind = {1} type = {2} lvars = {3} lvars_t = {4} offset = {5} block = {6} para = {7} paranum = {8} param_offset = {9}'.\
            format( self.name , self.kind , self.type , self.lvars , self.lvars_t , self.offset , self.block , self.para , self.paranum , self.param_offset ) )





class ManncError(Exception) : pass

# offset が 2のべき乗の時（？） に
# align 以上で、offset で割り切れる最小の値を返す？
def align_to( offset, align ):
    return ( offset + align -1 ) & ~ ( align -1 )

#インスタンスの中身を出力する（コメント#つき）
def pins( i ):
    print( '# pins ' ) 
    print( '#' +  pprint.pformat( vars(i), width=1024, compact=True ) ) if i!=0 else print('# null')

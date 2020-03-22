from enum import Enum
import sys
from enum import IntEnum, auto

class TokenKind(Enum):
    TK_RESERVED =  auto()
    TK_IDENT    =  auto()
    TK_NUM      =  auto()
    TK_EOF      =  auto()

tk_reserved_list = [ '+' , '-' , '*' , '/' , '(' , ')',
                     '==', '!=', '>', '>=', '<',
                     '=',
                     ';'
                   ]

tkn = []
code = []
LVar = [] # リストよりも連想配列のほうがよさそう

class NodeKind(Enum):
    ND_ADD   = auto()
    ND_SUB   = auto()
    ND_MUL   = auto()
    ND_DIV   = auto()
    ND_NUM   = auto()
    ND_ASSIGN = auto()
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
    
#
# 関数定義
#

#
# パーサ
#

#
# program = stmt*
#
def program():
    while tkn[0].kind != TokenKind.TK_EOF :
        code.append( stmt() )

#
# stmt = expr ";"
#
def stmt():
    print("# stmt")
    node = expr()
    expect(';')
    return node

#
# expr = assign
#
def expr():
    print("# expr")
    return assign()

#
# assign = equality ("=" assign)?
#
def assign():
    print("# assign")
    node = equality()
    if consume( '=' ):
        node = new_node( ND_ASSIGN, node, assign() )
    return node
        
#
# equality = relational ("==" relational | "!=" relational)*
#
def equality():
    print("# equality")
    node = relational()
    print("# EQUALITY")

    while True:
        if consume( '==' ) or consume( '!=' ) :
            node = relational()
        break

    return node


#
# relational = add ("<" add | "<=" add | ">" add | ">=" add)*
#
def relational():
    print("# relational")
    node = add()
    print("# RELATIONAL")
    #while True:
        #if consume( '<' ) or consume( '<=' ) or consume( '>' ) or consume( '>=' ) :
            #add()
    return node

#
# add = mul ("+" mul | "-" mul)*
#
def add():

    print("# add")
    node = mul()
    print("# ADD")
    while True:
        if consume( '+' ) :
            node = new_node( NodeKind.ND_ADD, node, mul() )
        elif consume( '-' ) :
            node = new_node( NodeKind.ND_SUB, node, mul() )
        else:
            return node
    
#
# mul = unary ("*" unary | "/" unary)*
#
def mul():
    print("# mul")
    node = unary()

    while True:
        if consume( '*' ):
            node = new_node( NodeKind.ND_MUL, node, primary() )
        elif consume( '/' ):
            node = new_node( NodeKind.ND_DIV, node, primary() )
        else:
            return node

#
# unary = ("+" | "-")? primary
#
def unary():
    print("# unary")
    if consume( '+' ):
        lnode = new_node_num( 0 )
        node = new_node( NodeKind.ND_ADD, lnode, primary )
        return node

    if consume( '-' ):
        lnode = new_node_num( 0 )
        node = new_node( NodeKind.ND_SUB, lnode, primary )
        return node
    
    return primary()

#
# primary = num | ident | "(" expr ")"
#
def primary():
    print('# primary()')
    if tkn[0].kind == TokenKind.TK_NUM :
        return new_node_num( expect_number() )

    if tkn[0].kind == TokenKind.TK_IDENT :
        newnode = Node()
        newnode.kind = NodeKind.ND_NUM
        newnode.str = tkn[0].str
        return newnode

    if consume( '(' ):
        node = expr()
        expect( ')' );
        return node

    # 必要？
    return new_node_num( expect_number() )

#
# パーサ
#


def new_node( kind, lhs, rhs ):
    newnode = Node()
    newnode.kind = kind
    newnode.lhs = lhs
    newnode.rhs = rhs

    return newnode

def new_node_num( val ):
    newnode = Node()
    newnode.kind = NodeKind.ND_NUM
    newnode.val = val

    return newnode


#
# トークナイザ  
#


def tokenize(fname):
    with open(fname, 'rb') as f:

        offset = 0
        while True:
            f.seek( offset )
            # print("offset='{0}'".format(offset))
            chb = f.read(1)
            ch = chb.decode('utf-8')
            offset += 1
            if ch == '' :
                break
            # print("readch='{0}'".format(ch) )

            if ch == '\n' or ch == ' ':
                continue
            if ch in tk_reserved_list:
                newtkn = Token()
                newtkn.kind = TokenKind.TK_RESERVED
                newtkn.str = ch
                
                tkn.append( newtkn )
                continue

            # 変数の場合
            if ch.isalpha():
                print('alpha')
                tmpstr = ''
                while ch.isalpha():
                    tmpstr += ch
                    f.seek( offset )
                    chb = f.read(1)
                    ch = chb.decode('utf-8')
                    offset +=1

                print('tmpstr={0}'.format( tmpstr ) )
                newtkn = Token()
                newtkn.kind = TokenKind.TK_IDENT
                newtkn.str = tmpstr
                tkn.append( newtkn )

                offset -= 1
                continue
                    
            # 数字の場合    
            if ch >= '0' and ch <= '9':
                tmpnum = ''
                # print('digit')
                while ch >= '0' and ch <= '9':
                    tmpnum += ch
                    f.seek( offset )
                    chb = f.read(1)
                    ch = chb.decode('utf-8')
                    offset += 1

                newtkn = Token()
                newtkn.kind = TokenKind.TK_NUM
                newtkn.val = int( tmpnum )
                tkn.append( newtkn )

                offset -= 1
                    
                # print("number='{0}'".format(tmpnum) )

    newtkn = Token()
    newtkn.kind = TokenKind.TK_EOF
    tkn.append( newtkn )
#
# トークナイザ  完了
#

#
# コード生成
#
def gen( node ):

    if node.kind == NodeKind.ND_NUM :
        print( '\tpush {0}'.format( node.val ) )
        return

    gen( node.lhs )
    gen( node.rhs )

    print('\tpop rdi')
    print('\tpop rax')
    
    if node.kind == NodeKind.ND_ADD :
        print('\tadd rax, rdi')
    elif node.kind == NodeKind.ND_SUB :
        print('\tsub rax, rdi')
    elif node.kind == NodeKind.ND_MUL :
        print('\timul rax, rdi')
    elif node.kind == NodeKind.ND_DIV :
        print('\tcqo')
        print('\tidiv rax, rdi')

    print('\tpush rax')

    return
#
# コード生成　完了
#

def consume(op):
    if tkn[0].kind != TokenKind.TK_RESERVED or tkn[0].str != op :
        return False
    del tkn[0]
    return True


def expect( op ):
    print(" # expect {0}".format( op ) )
    if tkn[0].kind != TokenKind.TK_RESERVED or tkn[0].str != op:
        print( "'{0}'ではありません".format(op) )
        sys.exit()
    del tkn[0]
    return True

def expect_number():
    if tkn[0].kind != TokenKind.TK_NUM:
        print("数ではありません")
        sys.exit()
    
    val = tkn[0].val
    del tkn[0]
    return val

###############################################
print('# tokenize start')
tokenize(sys.argv[1])
print('# tokenize end')

print('#print tkn start')
for t in tkn:
    print("#'{0}' , '{1}', '{2}'".format(t.kind, t.val, t.str) )
print('#print tkn end')

###############################################

print('# parse start')
program()
print('# parse end')

###############################################
print('.intel_syntax noprefix')
print('.global main')
print('main:')

for nd in code:
    print(  "#root kind={0} val={1}".format(nd.kind, nd.val) )
    #print( "#left kind={0} val={1}".format(nd.lhs.kind, nd.lhs.val) )
    #print( "#rght kind={0} val={1}".format(nd.rhs.kind, nd.rhs.val) )
    #print( "#left left kind={0} val={1}".format(nd.lhs.lhs.kind, nd.lhs.lhs.val) )
    #print( "#left rght kind={0} val={1}".format(nd.lhs.rhs.kind, nd.lhs.rhs.val) )
    #print( "#rght left kind={0} val={1}".format(nd.rhs.lhs.kind, nd.rhs.lhs.val) )
    #print( "#rght rght kind={0} val={1}".format(nd.rhs.rhs.kind, nd.rhs.rhs.val) )

    gen( nd )

print('\tpop rax')
print("\tret")    


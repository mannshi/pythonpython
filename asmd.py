from enum import Enum
import sys

class TokenKind(Enum):
    TK_RESERVED =  1
    TK_NUM      =  2
    TK_EOF      =  3

tk_reserved_list = [ '+' , '-' , '*' , '/' , '(' , ')' ]

class NodeKind(Enum):
    ND_ADD   = 1
    ND_SUB   = 2
    ND_MUL   = 3
    ND_DIV   = 4
    ND_NUM   = 5

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
        self.val = 0

def new_node( kind, lhs, rhs ):
    newnode = Node()
    newnode.kind = kind
    newnode.lhs = lhs
    newnode.rhs = rhs

    return newnode

def new_node_num( val ):
    newnode = Node()
    newnode.kind = NodeKind.ND_NUM
    newnode.val  = val

    return newnode

def expr():
    node = mul()

    while True:
        if consume( '+' ) :
            node = new_node( NodeKind.ND_ADD, node, mul() )
        elif consume( '-' ) :
            node = new_node( NodeKind.ND_SUB, node, mul() )
        else:
            return node

def mul():
    node = primary()

    while True:
        print('#mul')
        if consume( '*' ):
            node = new_node( NodeKind.ND_MUL, node, primary() )
        elif consume( '/' ):
            node = new_node( NodeKind.ND_DIV, node, primary() )
        else:
            return node

def primary():
    if consume( '(' ):
        node = expr()
        expect( ')' );
        return node

    return new_node_num( expect_number() )

#
# トークナイザ  
#

tkn = []

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
tokenize(sys.argv[1])

print('#print tkn')
for t in tkn:
    print("#'{0}' , '{1}', '{2}'".format(t.kind, t.val, t.str) )

###############################################
mynode = expr()

print( "#root kind={0} val={1}".format(mynode.kind, mynode.val) )
#print( "#left kind={0} val={1}".format(mynode.lhs.kind, mynode.lhs.val) )
#print( "#rght kind={0} val={1}".format(mynode.rhs.kind, mynode.rhs.val) )
#print( "#left left kind={0} val={1}".format(mynode.lhs.lhs.kind, mynode.lhs.lhs.val) )
#print( "#left rght kind={0} val={1}".format(mynode.lhs.rhs.kind, mynode.lhs.rhs.val) )
#print( "#rght left kind={0} val={1}".format(mynode.rhs.lhs.kind, mynode.rhs.lhs.val) )
#print( "#rght rght kind={0} val={1}".format(mynode.rhs.rhs.kind, mynode.rhs.rhs.val) )

###############################################
print('.intel_syntax noprefix')
print('.global main')
print('main:')

gen( mynode )

print('\tpop rax')
print("\tret")    


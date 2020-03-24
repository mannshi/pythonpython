import sys
import asmd

#
# パーサ
#

#
# program = stmt*
#
def program():
    while asmd.tkn[0].kind != asmd.TokenKind.TK_EOF :
        asmd.code.append( stmt() )

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
        node = new_node( asmd.NodeKind.ND_ASSIGN, node, assign() )
    return node
        
#
# equality = relational ("==" relational | "!=" relational)*
#
def equality():
    print("# equality")
    node = relational()
    print("# EQUALITY")

    while True:
        if consume( '==' ) :
            node = new_node( asmd.NodeKind.ND_EQU, node, relational() )
        if consume( '!=' ) :
            node = new_node( asmd.NodeKind.ND_NEQ, node, relational() )
        break

    return node


#
# relational = add ("<" add | "<=" add | ">" add | ">=" add)*
#
def relational():
    print("# relational")
    node = add()
    print("# RELATIONAL")
    while True:
        #if consume( '<' ) or consume( '<=' ) or consume( '>' ) or consume( '>=' ) :
        if consume( '<' ):
            node = new_node( asmd.NodeKind.ND_LT, node, add() )
        elif consume( '<=' ):
            node = new_node( asmd.NodeKind.ND_LTE, node, add() )
        elif consume( '>' ):
            node = new_node( asmd.NodeKind.ND_LT, add(), node )
        elif consume( '>=' ):
            node = new_node( asmd.NodeKind.ND_LTE, add(), node )
        else:
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
            node = new_node( asmd.NodeKind.ND_ADD, node, mul() )
        elif consume( '-' ) :
            node = new_node( asmd.NodeKind.ND_SUB, node, mul() )
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
            node = new_node( asmd.NodeKind.ND_MUL, node, primary() )
        elif consume( '/' ):
            node = new_node( asmd.NodeKind.ND_DIV, node, primary() )
        else:
            return node

#
# unary = ("+" | "-")? primary
#
def unary():
    print("# unary")
    if consume( '+' ):
        lnode = new_node_num( 0 )
        node = new_node( asmd.NodeKind.ND_ADD, lnode, primary )
        return node

    if consume( '-' ):
        lnode = new_node_num( 0 )
        node = new_node( asmd.NodeKind.ND_SUB, lnode, primary )
        return node
    
    return primary()

#
# primary = num | ident | "(" expr ")"
#
def primary():
    print('# primary()')
    if asmd.tkn[0].kind == asmd.TokenKind.TK_NUM :
        return new_node_num( expect_number() )

    if asmd.tkn[0].kind == asmd.TokenKind.TK_IDENT :
        newnode = asmd.Node()
        newnode.kind = asmd.NodeKind.ND_NUM
        newnode.str = asmd.tkn[0].str
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
    newnode = asmd.Node()
    newnode.kind = kind
    newnode.lhs = lhs
    newnode.rhs = rhs

    return newnode

def new_node_num( val ):
    newnode = asmd.Node()
    newnode.kind = asmd.NodeKind.ND_NUM
    newnode.val = val

    return newnode

def consume(op):
    if asmd.tkn[0].kind != asmd.TokenKind.TK_RESERVED or asmd.tkn[0].str != op :
        return False
    del asmd.tkn[0]
    return True


def expect( op ):
    print(" # expect {0}".format( op ) )
    if asmd.tkn[0].kind != asmd.TokenKind.TK_RESERVED or asmd.tkn[0].str != op:
        print( "'{0}'ではありません".format(op) )
        sys.exit()
    del asmd.tkn[0]
    return True

def expect_number():
    if asmd.tkn[0].kind != asmd.TokenKind.TK_NUM:
        print("数ではありません")
        sys.exit()

    val = asmd.tkn[0].val
    del asmd.tkn[0]
    return val

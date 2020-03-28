import sys
import asmd
from asmd import TokenKind as TK
from asmd import NodeKind as ND


#
# パーサ
#

#
# program = stmt*
#
def program():
    while asmd.tkn[0].kind != TK.TK_EOF :
        asmd.code.append( stmt() )

#
# stmt = expr ";"
# | "{" stmt* "}"
# | "if" "(" expr ")" stmt ("else" stmt)?
# | "while" "(" expr ")" stmt
# | "for" "(" expr? ";" expr? ";" expr? ")" stmt
def stmt():
    print("# stmt")
    #
    # 関数内関数
    #
    def stmt_if():
        print('#IF')
        if not consume( '(' ) :
            print('if の後は ( が必要です')
            sys.exit()
        node = asmd.NodeIF()
        node.kind = ND.IF
        node.expr = expr()
        if not consume( ')' ) :
            print('#IF 2')
            print('if の ''('' 後は '')'' が必要です')
            sys.exit()
        print('#IF 3')
        node.truebl = stmt()
        print('#IF 3.5')
        if consume_tk( TK.ELSE ) :
            print('#IF 4')
            node.elsebl = stmt()
        print('#IF 5')
        return node
    #
    # 関数内関数 おわり 
    #

    if consume( '{' ) :
        print('#print BLOCK start')
        node = asmd.NodeBLOCK()
        node.kind = ND.BLOCK
        while True:
            newstmt = stmt()
            node.stmts.append( newstmt )
            if consume( '}' ):
                break;
        
        return node

    if consume_tk( TK.IF ):
        return stmt_if()
        
    if consume( TK.TK_RETURN ) :
        print('#return')
        node = asmd.Node()
        node.kind = asmd.NodeKind.ND_RETURN
        print('#1')
        node.lhs = expr()
        print('#2')
    else :
        print('#3')
        node = expr()
        print('#4')

    print('##consume ;')
    if consume( ';' ):
        print('#consume ;')
        return node
    else:
        print(';ではないトークンです')
        sys.exit()

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
    if asmd.tkn[0].kind == TK.TK_NUM :
        print('#TK_NUMMMM')
        return new_node_num( expect_number() )

    if asmd.tkn[0].kind == TK.TK_IDENT :
        print('######TK_IDENT')
        newnode = asmd.Node()
        newnode.kind = asmd.NodeKind.ND_LVAR
        newnode.str = asmd.tkn[0].str
        if asmd.tkn[0].str in asmd.lvars :
            pass
        else :
            asmd.lvars[ asmd.tkn[0].str ] = asmd.offset + 8
        newnode.offset = asmd.lvars[ asmd.tkn[0].str ]
        asmd.offset += 8
        print('### newnode.kind {0}', newnode.kind )
        print('### newnode.str {0}', newnode.str )
        print('### newnode.offset {0}', newnode.offset )
            
        del asmd.tkn[0]

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
    print('#newnode num {0}'.format(val))
    newnode = asmd.Node()
    newnode.kind = asmd.NodeKind.ND_NUM
    newnode.val = val

    return newnode

def consume_tk(tk):
        print("# hikaku {0} {1}".format( asmd.tkn[0].kind, tk ) )
        if asmd.tkn[0].kind == tk:
            print('#consume_tk true')
            del asmd.tkn[0]
            return True
        else :
            print('#consume_tk false')
            return False
    
def consume(op):
    print('# consume tknknd {0}'.format(asmd.tkn[0].kind ))
    if op == TK.TK_RETURN :
        if asmd.tkn[0].kind == TK.TK_RETURN:
            del asmd.tkn[0]
        else :
            return False
            
        
    if asmd.tkn[0].kind != TK.TK_RESERVED or asmd.tkn[0].str != op:
        return False

    del asmd.tkn[0]

    return True



def expect( op ):
    print(" # expect {0}".format( op ) )
    if asmd.tkn[0].kind != TK.TK_RESERVED or asmd.tkn[0].str != op:
        print( "'{0}'ではありません".format(op) )
        sys.exit()
    del asmd.tkn[0]
    return True

def expect_number():
    print('# expect_number  tknknd {0}'.format(asmd.tkn[0].kind ))
    if asmd.tkn[0].kind != TK.TK_NUM:
        print("数ではありません")
        sys.exit()

    val = asmd.tkn[0].val
    del asmd.tkn[0]
    return val

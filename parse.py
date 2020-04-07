import sys
import asmd
from asmd import TokenKind as TK
from asmd import NodeKind as ND


#
# パーサ
#

#
# program = funcdef*
#
def program() :
    while asmd.tkn[0].kind != TK.TK_EOF:
        asmd.code.append( funcdef() )

#
# funcdef = ( idnet '(' ')' |
#            ident '(' ( "," ident )* ')'  ) "{" stmt* "}"
#
def funcdef():

    if asmd.tkn[0].kind != TK.TK_IDENT:
        raise asmd.ManncError( '関数の定義ではありません' )
        #print('関数の定義ではありません')
        #sys.exit()

    newnode = asmd.NodeFUNCDEF()
    newnode.kind = ND.FUNCDEF
    newnode.name = asmd.tkn[0].str
    del asmd.tkn[0]

#
# ここでグローバル変数の lvars を初期化する？
# primary()の返り値を newnode と lvars にする？
#
    
    if not consume( '(' ):
        raise asmd.ManncError('関数パラメータの定義がおかしいです A')
        #sys.exit()

    while True :
        if consume( ')' ):
            # 引数のない関数
            break;

        if asmd.tkn[0].kind != TK.TK_IDENT:
            raise asmd.ManncError('関数パラメータの定義がおかしいです B')
            #sys.exit()

        para = expr();
        newnode.para.append( para )
        newnode.paranum += 1

        # ローカル変数用左辺値
        if asmd.tkn[0].str in newnode.lvars :
            pass
        else :
            newnode.lvars[ asmd.tkn[0].str ] = newnode.offset + 8
        newnode.offset = newnode.lvars[ asmd.tkn[0].str ]
        asmd.offset += 8

        if consume( ')' ):
            # 引数のない関数
            break;
        
        if not consume( ',' ):
            raise asmd.ManncError('関数パラメータの定義がおかしいです C')
            sys.exit()
        
    # パラメータ読み込み終わり

    # 関数の実行部分は BLOCK で書き換えられる？
    # BLOCKにしないと、genする時にうまく生成できない？
    llvars = newnode.lvars
    newnode.block = stmt()

    return newnode

#
# program = stmt*
#
#def program():
#    while asmd.tkn[0].kind != TK.TK_EOF :
#        asmd.code.append( stmt() )

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
            raise asmd.ManncError('if の後は ( が必要です')
            #sys.exit()
        node = asmd.NodeIF()
        node.kind = ND.IF
        node.expr = expr()
        if not consume( ')' ) :
            print('#IF 2')
            raise asmd.ManncError('if の ''('' 後は '')'' が必要です')
            #sys.exit()
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
        raise asmd.ManncError(';ではないトークンです')
        #sys.exit()

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
# primary = num |
#           ident |
#           "(" expr ")"
#            ident "(" expr "," ")"
#
def primary():
    def primary_IDENT() :

        print('######TK_IDENT')

        if saki( '(', 1 ):
            newnode = asmd.NodeFUNCCALL()
            newnode.kind = ND.FUNC
            newnode.name = asmd.tkn[0].str
            del asmd.tkn[0]
            del asmd.tkn[0]

            # 関数呼び出しの場合
            if consume( ')' ):
                return newnode
            
            while True :
                para = expr();
                newnode.para.append( para )

                if consume( ')' ) :
                    break
                if not consume( ',' ):
                    raise asmd.ManncError('関数呼び出し方が不正です' )
                    # sys.exit()
            return newnode

        else :
            # 変数（左辺値）の場合
            newnode = asmd.Node()
            newnode.kind = asmd.NodeKind.ND_LVAR
            newnode.str = asmd.tkn[0].str
            if asmd.tkn[0].str in asmd.llvars :
                pass
            else :
                asmd.llvars[ asmd.tkn[0].str ] = asmd.offset + 8
            newnode.offset = asmd.llvars[ asmd.tkn[0].str ]
            asmd.offset += 8
            print('### newnode.kind {0}', newnode.kind )
            print('### newnode.str {0}', newnode.str )
            print('### newnode.offset {0}', newnode.offset )
            
        del asmd.tkn[0]
        return newnode

    print('# primary()')
    if asmd.tkn[0].kind == TK.TK_NUM :
        print('#TK_NUMMMM')
        return new_node_num( expect_number() )

    if asmd.tkn[0].kind == TK.TK_IDENT :
        print('#primary_IDENT')
        return primary_IDENT()

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
    
# saki : 先読みフラグ
# 0     の時は先読みしないトークンを消費する
# 0以外 の時は先読みしてトークンを消費しない
def consume(op ):
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


def saki( op, saki ):
    
    saki_kind = asmd.tkn[saki].kind
    saki_str  = asmd.tkn[saki].str
    
    if saki_kind != TK.TK_RESERVED or saki_str != op:
        return False

    return True

def expect( op ):
    print(" # expect {0}".format( op ) )
    if asmd.tkn[0].kind != TK.TK_RESERVED or asmd.tkn[0].str != op:
        raise asmd.ManncError( "'{0}'ではありません".format(op) )
        #sys.exit()

    del asmd.tkn[0]
    return True

def expect_number():
    print('# expect_number  tknknd {0}'.format(asmd.tkn[0].kind ))
    if asmd.tkn[0].kind != TK.TK_NUM:
        raise asmd.ManncError("数ではありません")
        #sys.exit()

    print('# valval {0}'.format(asmd.tkn[0].val ) )

    val = asmd.tkn[0].val
    del asmd.tkn[0]

    return val

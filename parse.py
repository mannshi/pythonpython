import sys
import asmd
from asmd import TokenKind as TK
from asmd import NodeKind as ND
from asmd import typ as TYP


#
# パーサ
#

#
# program = funcdef*
#
def program() :
    while asmd.tkn[0].kind != TK.EOF:
        asmd.code.append( funcdef() )

#
# funcdef = ( idnet '(' ')' |
#            ident '(' ( "," ident )* ')'  ) "{" stmt* "}"
#
def funcdef():
    newnode = asmd.NodeFUNCDEF()

    if asmd.tkn[0].kind != TK.INT:
        raise asmd.ManncError( '関数の定義が型名からはじまりません。' )
    del asmd.tkn[0]

    newnode.type = asmd.myType()
    newnode.type = TYP.INT
    print('#ftype {0}'.format( newnode.type ) )

    if asmd.tkn[0].kind != TK.IDENT:
        raise asmd.ManncError( '関数の定義ではありません' )
        #print('関数の定義ではありません')
        #sys.exit()

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

        if asmd.tkn[0].kind != TK.INT:
            raise asmd.ManncError( '関数の引数が型名からはじまりません。' + asmd.tkn[0].kind )
        del asmd.tkn[0]

        if asmd.tkn[0].kind != TK.IDENT:
            raise asmd.ManncError('関数パラメータの定義がおかしいです B')
            #sys.exit()

        #para = expr();
        #newnode.lvars.append( para )
        newnode.paranum += 1

        # 関数引数のローカル変数用左辺値
        if asmd.tkn[0].str in newnode.lvars :
            # パラメータの変数名が重複する場合は考慮しない
            pass
        else :
            newnode.lvars[ asmd.tkn[0].str ] = newnode.offset + 8
            newnode.lvars_t[ asmd.tkn[0].str ] = asmd.myType()
            newnode.para.append( asmd.tkn[0].str )
            newnode.offset += 8

        del asmd.tkn[0]

        if consume( ')' ):
            # 引数のない関数
            break;
        
        if not consume( ',' ):
            raise asmd.ManncError('関数パラメータの定義がおかしいです C')
            sys.exit()
        
    # パラメータ読み込み終わり

    # 関数の実行部分は BLOCK で書き換えられる？
    # BLOCKにしないと、genする時にうまく生成できない？
    asmd.llvars = newnode.lvars.copy()
    asmd.llvars_t = newnode.lvars_t.copy()
    asmd.offset = newnode.offset

    newnode.block = stmt()

    newnode.lvars = asmd.llvars.copy()
    newnode.lvars_t = asmd.llvars_t.copy()
    newnode.offset = asmd.offset

    return newnode

#
# program = stmt*
#
#def program():
#    while asmd.tkn[0].kind != TK.EOF :
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

    # 変数の宣言文の場合    
    if consume_tk( TK.INT ):
        if asmd.tkn[0].kind != TK.IDENT and asmd.tkn[0].str != '*':
            raise asmd.ManncError('型名の後ろが識別子 でも * でもありません')

        if asmd.tkn[0].kind == TK.IDENT :
            if asmd.tkn[1].str == '[' :
                #配列の場合
                print('#配列の場合')
                thistype = asmd.myType()
                thistype.ty = TYP.ARRAY

                if asmd.tkn[2].kind != TK.NUM:
                    raise asmd.ManncError('配列の添え字が数字ではありません')

                thistype.array_size = asmd.tkn[2].val
                print('#配列の場合 {0}'.format(thistype.array_size))
                asmd.offset += 8 * asmd.tkn[2].val
                asmd.llvars[ asmd.tkn[0].str ] = asmd.offset
                asmd.llvars_t[ asmd.tkn[0].str ] = thistype.ty

                if asmd.tkn[3].str != ']' :
                    raise asmd.ManncError('配列が ] で閉じられていません')

                del asmd.tkn[0]
                del asmd.tkn[0]
                del asmd.tkn[0]
                del asmd.tkn[0]
                
            else :
                # 配列ではない変数の場合
                # int型の場合
                thistype = asmd.myType()
                thistype.ty = TYP.INT
                #asmd.offset += 4
                asmd.offset += 8
                asmd.llvars[ asmd.tkn[0].str ] = asmd.offset
                asmd.llvars_t[ asmd.tkn[0].str ] = thistype.ty
                del asmd.tkn[0]
        else :
            # int型へのポインタの場合
            del asmd.tkn[0]
            asmd.offset += 8
            asmd.llvars[ asmd.tkn[0].str ] = asmd.offset
            thistype = asmd.myType()
            thistype.ty = TYP.PTR
            thistype.ptr_to = asmd.myType()
            thistype.ptr_to.ty = TYP.INT
            asmd.llvars_t[ asmd.tkn[0].str ] = thistype.ty
            del asmd.tkn[0]

        if not consume( ';' ):
            raise asmd.ManncError(';ではないトークンです {0}'.format(asmd.tkn[0].str))

        return 0
        
    # if文の場合
    if consume_tk( TK.IF ):
        return stmt_if()
        
    if consume_tk( TK.RETURN ) :
        print('#returrrrrrn')
        node = asmd.Node()
        node.kind = ND.RETURN
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
        raise asmd.ManncError(';ではないトークンです{0}'.format(asmd.tkn[0].str))
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
        node = new_node( ND.ASSIGN, node, assign() )
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
            node = new_node( ND.EQU, node, relational() )
        if consume( '!=' ) :
            node = new_node( ND.NEQ, node, relational() )
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
            node = new_node( ND.LT, node, add() )
        elif consume( '<=' ):
            node = new_node( ND.LTE, node, add() )
        elif consume( '>' ):
            node = new_node( ND.LT, add(), node )
        elif consume( '>=' ):
            node = new_node( ND.LTE, add(), node )
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
            node = new_node( ND.ADD, node, mul() )
        elif consume( '-' ) :
            node = new_node( ND.SUB, node, mul() )
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
            node = new_node( ND.MUL, node, primary() )
        elif consume( '/' ):
            node = new_node( ND.DIV, node, primary() )
        else:
            return node

#
# unary = ("+" | "-")? primary
#
def unary():
    print("# unary")

    #sizeof
    if consume_tk( TK.SIZEOF ):
        node = unary()
        if node.type == TYP.INT:
            return new_node_num( 8 )
        else :
            return new_node_num( 8 )

    if consume( '+' ):
        lnode = new_node_num( 0 )
        node = new_node( ND.ADD, lnode, primary )
        return node

    if consume( '-' ):
        lnode = new_node_num( 0 )
        node = new_node( ND.SUB, lnode, primary )
        return node
    
    if asmd.tkn[1].str == '[':
        #配列の場合
        newnode = new_node( ND.DEREF, 0, 0 )
        newnode.lhs = new_node( ND.ADD, 0, 0 )
        newnode.lhs.lhs = primary()
        del asmd.tkn[0] #[
        newnode.lhs.rhs = expr()
        if not consume( ']' ):
            raise asmd.ManncError('配列が]で閉じられていません{0}'.format(asmd.tkn[0].str) )

        return newnode

    # アドレス（ポインタ）用演算子
    if consume( '*' ):
        print('#ND.DEREF')
        node = new_node( ND.DEREF, unary(), 0 )
        return node
    if consume( '&' ):
        print('#ND.ADDR')
        node = new_node( ND.ADDR, unary(), 0 )
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
            if not asmd.tkn[0].str in asmd.llvars :
                raise asmd.ManncError('宣言されていない変数を使用しようとしています<{0}><{1}>'.format(asmd.tkn[0].str, asmd.llvars ) )

            #配列ではない場合の場合
            newnode = asmd.Node()
            newnode.kind = ND.LVAR
            newnode.str = asmd.tkn[0].str

            newnode.offset = asmd.llvars[ asmd.tkn[0].str ]
            newnode.type = asmd.llvars_t[ asmd.tkn[0].str ]

            print('### newnode.kind {0}'.format(newnode.kind ) );
            print('### newnode.str {0}'.format(newnode.str ) );
            print('### newnode.offset {0}'.format(newnode.offset ) );
            print('### newnode.type {0}'.format(newnode.type ) );
        
            del asmd.tkn[0]
            return newnode

    print('# primary()')
    if asmd.tkn[0].kind == TK.NUM :
        print('#TK_NUMMMM')
        return new_node_num( expect_number() )

    if asmd.tkn[0].kind == TK.IDENT :
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
    newnode.kind = ND.NUM
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
    if op == TK.RETURN :
        if asmd.tkn[0].kind == TK.RETURN:
            del asmd.tkn[0]
        else :
            return False
            
        
    if asmd.tkn[0].kind != TK.RESERVED or asmd.tkn[0].str != op:
        return False

    del asmd.tkn[0]

    return True


def saki( op, saki ):
    
    saki_kind = asmd.tkn[saki].kind
    saki_str  = asmd.tkn[saki].str
    
    if saki_kind != TK.RESERVED or saki_str != op:
        return False

    return True

def expect( op ):
    print(" # expect {0}".format( op ) )
    if asmd.tkn[0].kind != TK.RESERVED or asmd.tkn[0].str != op:
        raise asmd.ManncError( "'{0}'ではありません".format(op) )
        #sys.exit()

    del asmd.tkn[0]
    return True

def expect_number():
    print('# expect_number  tknknd {0}'.format(asmd.tkn[0].kind ))
    if asmd.tkn[0].kind != TK.NUM:
        raise asmd.ManncError("数ではありません")
        #sys.exit()

    print('# valval {0}'.format(asmd.tkn[0].val ) )

    val = asmd.tkn[0].val
    del asmd.tkn[0]

    return val

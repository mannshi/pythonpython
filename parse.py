import sys
import asmd
import type
from asmd import TokenKind as TK
from asmd import NodeKind as ND
from asmd import typ as TYP
import copy

#
# パーサ
#

#
# グローバル変数
#
def getgvar2():
    ( t, name ) =  type.declaration( 'NOTPARA' )
    asmd.glvars_t[ name ] = t
    return

def getgvar():


    if asmd.tkn[0].str != 'int' and asmd.tkn[0].str != 'char':
        raise asmd.ManncError( '変数の定義が型名からはじまりません。 1' )

    #
    # 型
    #
    if consume_tk( TK.INT ) :
        thistype = asmd.myType()
        if consume( '*' ) :
            # intへのポインタ型
            thistype.ty = TYP.PTR
            thistype.ptr_to = asmd.myType()
            thistype.ptr_to.ty = TYP.INT
        else:
            # int型
            thistype.ty = TYP.INT
    elif consume_tk( TK.CHAR ) :
        if consume( '*' ) :
            # charへのポインタ型
            thistype.ty = TYP.PTR
            thistype.ptr_to = asmd.myType()
            thistype.ptr_to.ty = TYP.CHAR
        else:
            # char型
            thistype.ty = TYP.CHAR
    else:
        raise asmd.ManncError( '変数の定義が型名からはじまりません。2 {0}'.format(asmd.tkn[0].str ) )

    if asmd.tkn[0].str in asmd.glvars_t:
        raise asmd.ManncError( 'グローバル変数が二重で宣言されています' )
        
    asmd.glvars_t[ asmd.tkn[0].str ] = thistype
    
    del asmd.tkn[0]

    if consume( '=' ) :
        #グローバル変数の初期化
        raise asmd.ManncError( 'グローバル変数の初期化は未実装' )
        pass

    if not consume( ';' ):
        raise asmd.ManncError( 'グローバル変数が ; で終了していません。{0}'.format( asmd.tkn[0].str ) )
        
    return

#
# program = ( funcdef | gvardef )*
#
def program() :
    while asmd.tkn[0].kind != TK.EOF:
        # グローバル変数？  関数定義？
        if asmd.tkn[0].str != 'int' and asmd.tkn[0].str != 'char':
            raise asmd.ManncError( '関数、変数の定義が型名からはじまりません。{0}'.format( asmd.tkn[0].str ) )
            
        if asmd.tkn[1].str == '*' :
            if asmd.tkn[2].kind != TK.IDENT: 
                raise asmd.ManncError( '型名の後ろが識別子ではありません' )
            if asmd.tkn[3].str == '(':
                #ポインタを返す関数
                asmd.code.append( funcdef() )
            else:
                #グローバルのポインタ変数
                getgvar2()
        else:
            if asmd.tkn[1].kind != TK.IDENT: 
                raise asmd.ManncError( '型名の後ろが識別子ではありません' )
            if asmd.tkn[2].str == '(':
                #ポインタ以外を返す関数
                asmd.code.append( funcdef() )
            else:
                #グローバルのポインタ以外の変数
                getgvar2()

#
# funcdef = ( idnet '(' ')' |
#            ident '(' ( "," ident )* ')'  ) "{" stmt* "}"
#
def funcdef():
    newnode = asmd.NodeFUNCDEF()

    if asmd.tkn[0].kind == TK.INT:
        newnode.type = asmd.TypeType( kind = TYP.INT,  size = 4, align = 4, array_len = 0, base = 0, function = 0 )
    elif asmd.tkn[0].kind == TK.CHAR:
        newnode.type = asmd.TypeType( kind = TYP.CHAR, size = 1, align = 1, array_len = 0, base = 0, function = 0 )
    else:
        raise asmd.ManncError( '関数の定義が型名からはじまりません。' )
    del asmd.tkn[0]

    if asmd.tkn[0].kind != TK.IDENT:
        raise asmd.ManncError( '関数の定義ではありません' )

    newnode.kind = ND.FUNCDEF
    newnode.name = asmd.tkn[0].str
    del asmd.tkn[0]

    newnode.offset = 0

    if not consume( '(' ):
        raise asmd.ManncError('関数パラメータの定義がおかしいです A')

    while True :
        if consume( ')' ):
            # 引数のない関数
            break;
##############
        ( thistype, vname ) =  type.declaration( 'PARA' )

        #asmd.glvars_t[ name ] = t
##############

        newnode.paranum += 1

        #vname = asmd.tkn[0].str

        # 関数引数のローカル変数用左辺値
        if vname in newnode.lvars :
           # パラメータの変数名が重複する場合は考慮しない
            pass
        else :

            newnode.lvars_t[ vname ] = thistype
            newnode.para.append( vname )

            newnode.lvars[ vname ] = asmd.MYVar()
            newnode.lvars[ vname ].name = vname
            newnode.lvars[ vname ].type = thistype
            newnode.lvars[ vname ].offset  = asmd.align_to( newnode.offset, thistype.align )
            newnode.lvars[ vname ].offset += newnode.lvars[ vname ].type.size 
            
            newnode.offset += newnode.lvars_t[ vname ].size
            #newnode.offset = newnode.lvarst[ vname ].offset

        #del asmd.tkn[0]

        if consume( ')' ):
            # 引数のない関数
            break;
        
        if not consume( ',' ):
            raise asmd.ManncError('関数パラメータの定義がおかしいです C')
            sys.exit()
        
    # パラメータ読み込み終わり

    # 関数の実行部分は BLOCK で書き換えられる？
    # BLOCKにしないと、genする時にうまく生成できない？

    asmd.offset =   newnode.offset
    asmd.lvars_t = copy.deepcopy( newnode.lvars_t )
    asmd.lvars = copy.deepcopy( newnode.lvars )

    newnode.block = stmt()

    newnode.lvars = copy.deepcopy( asmd.lvars )

    newnode.lvars_t = copy.deepcopy( asmd.lvars_t )
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
    #print("# stmt")
    #
    # 関数内関数
    #

    def stmt_break():
        if not consume( ';' ):
            raise asmd.ManncError('break の後は ; が必要です')
        node = asmd.Node()
        node.kind = ND.BREAK
        return node
        
    def stmt_continue():
        if not consume( ';' ):
            raise asmd.ManncError('continue の後は ; が必要です')
        node = asmd.Node()
        node.kind = ND.CONTINUE
        return node
        
    def stmt_while():
        if not consume( '(' ):
            raise asmd.ManncError('while の後は ( が必要です')
        node = asmd.NodeWHILE()
        node.kind = ND.WHILE
        node.expr = expr()

        if not consume( ')' ) :
            raise asmd.ManncError('while の ''('' 後は '')'' が必要です')
        node.block = stmt()
        
        return node

    def stmt_if():
        #print('#IF')
        if not consume( '(' ) :
            raise asmd.ManncError('if の後は ( が必要です')
        node = asmd.NodeIF()
        node.kind = ND.IF
        node.expr = expr()
        if not consume( ')' ) :
            raise asmd.ManncError('if の ''('' 後は '')'' が必要です')
        node.truebl = stmt()
        if consume_tk( TK.ELSE ) :
            node.elsebl = stmt()

        return node
    #
    # 関数内関数 おわり 
    #

    if consume( '{' ) :
        #print('#print BLOCK start')
        node = asmd.NodeBLOCK()
        node.kind = ND.BLOCK
        while True:
            newstmt = stmt()
            node.stmts.append( newstmt )
            if consume( '}' ):
                break;
        
        return node

    # 変数の宣言文の場合    
    if asmd.tkn[0].kind in ( TK.INT, TK.CHAR ):
        tknkind = asmd.tkn[0].kind 
        
        ( thistype, vname ) =  type.declaration( 'NOTPARA' )
        print('#var dec')
        print('#{0}'.format(vname))
        thistype.myself()
        if thistype.base != 0 :
            thistype.base.myself()

        asmd.lvars_t[ vname ] = thistype
        asmd.offset = asmd.align_to( asmd.offset, thistype.align )
        asmd.offset += asmd.lvars_t[ vname ].size
        asmd.lvars[ vname ] = asmd.MYVar()
        asmd.lvars[ vname ].offset = asmd.offset
        print('#offset aaaaa')
        print('#offset  {0}'.format( asmd.offset ) )
        print('#lvars   {0}'.format( asmd.lvars[ vname ].offset ) )
        #print('#lvars_t {0}'.format( asmd.lvars_t[ vname ].offset ) )
        #del asmd.tkn[0]

        return 0
        
    if consume_tk( TK.CONTINUE ):
        return stmt_continue()
    if consume_tk( TK.BREAK ):
        return stmt_break()
    if consume_tk( TK.WHILE ):
        return stmt_while()
    if consume_tk( TK.IF ):
        return stmt_if()
    if consume_tk( TK.RETURN ) :
        node = asmd.Node()
        node.kind = ND.RETURN
        node.lhs = expr()
    else :
        node = expr()

    if consume( ';' ):
        return node
    else:
        raise asmd.ManncError(';ではないトークンです{0}'.format(asmd.tkn[0].str))

#
# expr = assign
#
def expr():
    #print("# expr")
    n = assign()
    add_type( n )
    return n

#
# assign = equality ("=" assign)?
#
def assign():
    #print("# assign")
    node = equality()
    if consume( '=' ):
        node = new_node( ND.ASSIGN, node, assign() )
    return node
        
#
# equality = relational ("==" relational | "!=" relational)*
#
def equality():
    #print("# equality")
    node = relational()
    #print("# EQUALITY")

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
    #print("# relational")
    node = add()
    #print("# RELATIONAL")
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

    #print("# add")
    node = mul()
    #print("# ADD")
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
    #print("# mul")
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
    #print("# unary")

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
        #newnode.type = TYP.ARRAY
        newnode.lhs = new_node( ND.PTR_ADD, 0, 0 )
        newnode.lhs.lhs = primary()
        newnode.lhs.type = newnode.lhs.lhs.type
        del asmd.tkn[0] # [ を削除する
        newnode.lhs.rhs = expr()
        if not consume( ']' ):
            raise asmd.ManncError('配列が]で閉じられていません{0}'.format(asmd.tkn[0].str) )

        return newnode

    # アドレス（ポインタ）用演算子
    if consume( '*' ):
        print('#ND.DEREF')
        node = new_node( ND.DEREF, unary(), 0 )
        if node.lhs.kind == ND.ADD:
            node.lhs.kind = ND.PTR_ADD
        node.type = node.lhs.type
        #node = new_node( ND.DEREF, 0, 0 )
        #node.lhs = new_node( ND.PTR_ADD, unary(), 0 )
        #node.type = node.lhs.type
        #node.lhs.type = node.lhs.type
        print("#DEREF pins" )
        asmd.pins( node )
        asmd.pins( node.lhs )
        
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

        #print('######TK_IDENT')

        if saki( '(', 1 ):
            newnode = asmd.NodeFUNCCALL()
            newnode.kind = ND.FUNC
            newnode.name = asmd.tkn[0].str
            del asmd.tkn[0]
            del asmd.tkn[0]

            #
            # 関数呼び出しの場合
            #
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
            #
            # 変数（左辺値）の場合
            #
            if asmd.tkn[0].str in asmd.glvars_t:
                #グローバル変数として宣言されている場合
                newnode = asmd.Node()
                newnode.kind = ND.LVAR
                newnode.str = asmd.tkn[0].str
                newnode.size = asmd.glvars_t[ asmd.tkn[0].str ].size
                newnode.type = asmd.glvars_t[ asmd.tkn[0].str ]
                del asmd.tkn[0]
                return newnode

            if not asmd.tkn[0].str in asmd.lvars :
                raise asmd.ManncError('宣言されていない変数を使用しようとしています<{0}><{1}>'.format(asmd.tkn[0].str, asmd.lvars ) )

            #配列ではない場合
            newnode = asmd.Node()
            newnode.kind = ND.LVAR
            newnode.str = asmd.tkn[0].str
            newnode.size = asmd.lvars_t[ asmd.tkn[0].str ].size

            newnode.offset = asmd.lvars[ asmd.tkn[0].str ]
            newnode.type = asmd.lvars_t[ asmd.tkn[0].str ]

            del asmd.tkn[0]
            return newnode

    if asmd.tkn[0].kind == TK.STRING :
        # 文字リテラルはグローバル変数として扱う
        # .dataセグメントに書き込む？
        # ラベル名＝変数名になる
        #print('#parse string')
        newnode = asmd.Node()
        newnode.kind = ND.LVAR
        newnode.str = asmd.tkn[0].str
        newnode.size = len( asmd.tkn[0].str )
        newnode.type = asmd.TypeType( TYP.ARRAY,
                                        newnode.size+1,
                                        1,
                                        newnode.size + 1,
                                        asmd.TypeType( TYP.INT,  4, 4, 0, 0, 0),
                                        0)
        asmd.glvars_t[ newnode.str ] = newnode.type

        del asmd.tkn[0]
        return newnode

    #print('# primary()')
    if asmd.tkn[0].kind == TK.NUM :
        #print('#TK_NUMMMM')
        return new_node_num( expect_number() )

    if asmd.tkn[0].kind == TK.IDENT :
        #print('#primary_IDENT')
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

    if kind == ND.ADD:
        newnode.type = asmd.TypeType( TYP.INT,  4, 4, 0, 0, 0)
    if kind == ND.LVAR:
        pass
    if kind == ND.ADDR:
        newnode.type = asmd.TypeType( TYP.PTR,  8, 8, 0, 0, 0)
    if kind == ND.DEREF:
        pass
    
    return newnode

def new_node_num( val ):
    #print('#newnode num {0}'.format(val))
    newnode = asmd.Node()
    newnode.kind = ND.NUM
    newnode.val = val
    newnode.type = asmd.TypeType( TYP.INT,  4, 4, 0, 0, 0)

    return newnode

def consume_tk(tk):
        #print("# hikaku {0} {1}".format( asmd.tkn[0].kind, tk ) )
        if asmd.tkn[0].kind == tk:
            #print('#consume_tk true')
            del asmd.tkn[0]
            return True
        else :
            #print('#consume_tk false')
            return False
    
# saki : 先読みフラグ
# 0     の時は先読みしないトークンを消費する
# 0以外 の時は先読みしてトークンを消費しない
def consume(op ):
    #print('# consume tknknd {0}'.format(asmd.tkn[0].kind ))
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
    #print(" # expect {0}".format( op ) )
    if asmd.tkn[0].kind != TK.RESERVED or asmd.tkn[0].str != op:
        raise asmd.ManncError( "'{0}'ではありません".format(op) )
        #sys.exit()

    del asmd.tkn[0]
    return True

def expect_number():
    #print('# expect_number  tknknd {0}'.format(asmd.tkn[0].kind ))
    if asmd.tkn[0].kind != TK.NUM:
        raise asmd.ManncError("数ではありません {0}".format(asmd.tkn[0].str))
        #sys.exit()

    #print('# valval {0}'.format(asmd.tkn[0].val ) )

    val = asmd.tkn[0].val
    del asmd.tkn[0]

    return val

def set_type( ty, size, align, ptr_to, array_size ):
        
        newtype = asmd.myType()

        if ty == TK.INT or ty == TK.CHAR:
            newtype.size = size;
            newtype.align = align;
        elif ty == TK.CHAR:
            newtype.size = 1;
            newtype.align = 1;
        else:
            newtype.size = size * array_size

        #newtype.ty = ty;
        #newtype.align = align;
        #newtype.size = size;
        #newtype.ptr_to = ptr_to;
        #newtype.array_size = array_size; # 配列の要素数（バイト数ではない？）
    
        return newtype

def add_type( node ) :
    if node == 0:
        return
    print('#add_type {0}'.format(node.kind) )
    if node.kind == ND.FUNC:
        return
        
    add_type( node.lhs )
    add_type( node.rhs )
    
    if node.kind == ND.PTR_ADD or \
       node.kind == ND.ASSIGN :
        node.type = node.lhs.type
        #node.size = node.lhs.type.size
        return
    elif node.kind == ND.DEREF :
        print('#deref add_type')
        node.type = node.lhs.type.base
        print('#add_type')
        asmd.pins( node.lhs.type )
        node.size = node.lhs.type.base.size
        print('#deref add_type {0}'.format( node.type ))
        return


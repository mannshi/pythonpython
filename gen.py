import asmd
import sys
from asmd import NodeKind as ND
from asmd import typ as TYP

if_num = 0
#
# コード生成
#
def gen( node ):
    global if_num
    
    if node == 0:
        return

    if node.kind == ND.ADDR :
        gen_lval( node.lhs )
        return
    
    if node.kind == ND.DEREF :
        gen( node.lhs )
        print('\tpop rax')
        print('\tmov rax, [rax]')
        print('\tpush rax')
        return

    if node.kind == ND.FUNCDEF :
        # 関数の名前＝ラベル
        print("{0}:".format(node.name))

        # プロローグ
        print('#プロローグ')
        print('\tpush rbp')
        print('\tmov rbp, rsp')
        print('\tsub rsp, {0}'.format(node.offset))

        # レジスタの中身をパラメータにコピーする
        para_i = 0
        para_reg = [ "rdi", "rsi", "rdx", "rcx" ];
        while para_i < node.paranum :
            print("#para{0}".format(para_i) )
            print("#para{0}".format(node.para[para_i]) )
            print("\tmov rax, rbp\n");
            print("\tsub rax, {0}\n".format(node.lvars[node.para[para_i]]));
            print("\tmov [rax], {0}\n".format(para_reg[para_i]));
            para_i += 1
            
        asmd.llvars = node.lvars.copy()

        # 関数本体（ブロック）を出力する
        gen( node.block )

        #エピローグ
        #最後の式の結果がRAXに残っているのでそれが返り値になる
        print('#エピローグ')
        print('\tpop rax')
        print('\tmov rsp, rbp')
        print('\tpop rbp')

        return

    # NodeKind が FUNC　の場合
    if node.kind == ND.FUNC :
        print('#FUNC')
        pcnt = 0
        for para in node.para:
            gen( para )
            if pcnt == 0:
                print("\tpop rdi\n");
            elif pcnt == 1:
                print("\tpop rsi\n");
            elif pcnt == 2:
                print("\tpop rdx\n");
            elif pcnt == 3:
                print("\tpop rcx\n");
            else:
                raise asmd.ManncError('関数の引数は４つまで')
                #sys.exit()
            pcnt += 1
        print('\tcall {0}'.format(node.name) )
        print('\tpush rax')
        
        return
        
    # NodeKindが、数値の場合
    # スタックにその値をプッシュする
    if node.kind == ND.ND_NUM :
        print( '\tpush {0}'.format( node.val ) )
        return

    if node.kind == ND.BLOCK:
        for stmt in node.stmts:
            gen( stmt )
        return 

    if node.kind == ND.IF :
        print('#ifgen')
        gen( node.expr )
        print('\tpop rax')
        print('\tcmp rax, 0')
        if_num_tmp1 = if_num
        if_num += 1
        if_num_tmp2 = if_num
        if_num += 1
        print('\tje .ELSE' + str(if_num_tmp1).zfill(3) )
        print('#ture gen')
        if not node.truebl == 0:
            gen( node.truebl )
        print('\tjmp .IFEND' + str(if_num_tmp2).zfill(3) )
        print('\t.ELSE' + str(if_num_tmp1).zfill(3) + ':')
        if not node.elsebl == 0:
            gen( node.elsebl )
        print('.IFEND' + str(if_num_tmp2).zfill(3) + ':' )
        
        
        return

    # NodeKind が左辺値の場合
    if node.kind == ND.ND_LVAR :
        gen_lval( node )
        print('\tpop rax')
        print('\tmov rax, [rax]')
        print('\tpush rax')
        return 

    # NodeKind が代入の場合
    if node.kind == ND.ND_ASSIGN :

        gen_lval( node.lhs )
        gen( node.rhs )

        print('\tpop rdi')
        print('\tpop rax')
        print('\tmov [rax], rdi')
        print('\tpush rdi')

        return

    # NodeKind が reurn の場合
    if node.kind == ND.ND_RETURN :
        print('#NDRETUN')
        gen( node.lhs )
        print('#NDRETURN エピローグ')
        print('\tpop rax')
        print('\tmov rsp, rbp')
        print('\tpop rbp')
        print('\tret')
        return
    
    # NodeKindが、二項演算子（四則演算、等号、不等号）の場合
    # lhs がスタックトップ
    # rhs がその次
    # pop してその二つを rdi と rax に入れる
    # 演算の結果は rax に入れてプッシュする
    
    gen( node.lhs )
    gen( node.rhs )

    print('\tpop rdi')
    print('\tpop rax')
    
    if node.kind == ND.ND_ADD :
        #ポインタの計算をする場合

        print('#add kind {0}'.format(node.lhs.kind))

        if node.lhs.kind == ND.ND_LVAR:
            print('#add type {0}'.format(node.lhs.type))
            if node.lhs.type == TYP.PTR :
                print('\timul rdi, 4')
        print('\tadd rax, rdi')
    elif node.kind == ND.ND_SUB :
        print('\tsub rax, rdi')
    elif node.kind == ND.ND_MUL :
        print('\timul rax, rdi')
    elif node.kind == ND.ND_DIV :
        print('\tcqo')
        print('\tidiv rax, rdi')
    elif node.kind == ND.ND_EQU :
        print('\tcmp rax, rdi')
        print('sete al')
        print('movzb rax, al')
    elif node.kind == ND.ND_NEQ :
        print('\tcmp rax, rdi')
        print('\tsetne al')
        print('\tmovzb rax, al')
    elif node.kind == ND.ND_LT :
        print('\tcmp rax, rdi')
        print('\tsetl al')
        print('\tmovzb rax, al')
    elif node.kind == ND.ND_LTE :
        print('\tcmp rax, rdi')
        print('\tsetle al')
        print('\tmovzb rax, al')

    print('\tpush rax')

    return
#
# コード生成　完了
#

def gen_lval(node):
    if node.kind == ND.ND_LVAR:
        var = node.str
        print('#here {0}'.format(var))
        offset = asmd.llvars[var]
        print('#gen_lval var={0} offset={1}'.format(var, offset ) )

        print('\tmov rax, rbp')
        print('\tsub rax, {0}'.format(asmd.llvars[node.str]))
        print('\tpush rax')

        return 

    if node.kind == ND.DEREF:
        gen( node.lhs )
        return 

    raise asmd.ManncError('代入の左辺値が変数ではありません')

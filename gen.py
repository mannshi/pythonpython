import asmd
import sys
from asmd import NodeKind as NK

if_num = 0
#
# コード生成
#
def gen( node ):
    global if_num
    
    # NodeKind が FUNC　の場合
    if node.kind == NK.FUNC :
        print('#FUNC')
        print('\tcall {0}'.format(node.name) )
        print('\tpush rax')
        
        return
        
    # NodeKindが、数値の場合
    # スタックにその値をプッシュする
    if node.kind == NK.ND_NUM :
        print( '\tpush {0}'.format( node.val ) )
        return

    if node.kind == NK.BLOCK:
        for stmt in node.stmts:
            gen( stmt )
        return 

    if node.kind == NK.IF :
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
    if node.kind == NK.ND_LVAR :
        gen_lval( node )
        print('\tpop rax')
        print('\tmov rax, [rax]')
        print('\tpush rax')
        return 

    # NodeKind が代入の場合
    if node.kind == NK.ND_ASSIGN :

        gen_lval( node.lhs )
        gen( node.rhs )

        print('\tpop rdi')
        print('\tpop rax')
        print('\tmov [rax], rdi')
        print('\tpush rdi')

        return

    # NodeKind が reurn の場合
    if node.kind == NK.ND_RETURN :
        gen( node.lhs )
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
    
    if node.kind == NK.ND_ADD :
        print('\tadd rax, rdi')
    elif node.kind == NK.ND_SUB :
        print('\tsub rax, rdi')
    elif node.kind == NK.ND_MUL :
        print('\timul rax, rdi')
    elif node.kind == NK.ND_DIV :
        print('\tcqo')
        print('\tidiv rax, rdi')
    elif node.kind == NK.ND_EQU :
        print('\tcmp rax, rdi')
        print('sete al')
        print('movzb rax, al')
    elif node.kind == NK.ND_NEQ :
        print('\tcmp rax, rdi')
        print('\tsetne al')
        print('\tmovzb rax, al')
    elif node.kind == NK.ND_LT :
        print('\tcmp rax, rdi')
        print('\tsetl al')
        print('\tmovzb rax, al')
    elif node.kind == NK.ND_LTE :
        print('\tcmp rax, rdi')
        print('\tsetle al')
        print('\tmovzb rax, al')

    print('\tpush rax')

    return
#
# コード生成　完了
#

def gen_lval(node):
    if node.kind != NK.ND_LVAR:
        print('代入の左辺値が変数ではありません')
        sys.exit()
    
    print('\tmov rax, rbp')
    print('\tsub rax, {0}'.format(node.offset))
    print('\tpush rax')

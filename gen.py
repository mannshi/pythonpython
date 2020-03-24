import asmd
#
# コード生成
#
def gen( node ):
    
    # NodeKindが、数値の場合
    # スタックにその値をプッシュする
    if node.kind == asmd.NodeKind.ND_NUM :
        print( '\tpush {0}'.format( node.val ) )
        return

    # NodeKindが、二項演算子の場合
    # lhs がスタックトップ
    # rhs がその次
    # pop してその二つを rdi と rax に入れる
    # 演算の結果は rax に入れてプッシュする
    
    gen( node.lhs )
    gen( node.rhs )

    print('\tpop rdi')
    print('\tpop rax')
    
    if node.kind == asmd.NodeKind.ND_ADD :
        print('\tadd rax, rdi')
    elif node.kind == asmd.NodeKind.ND_SUB :
        print('\tsub rax, rdi')
    elif node.kind == asmd.NodeKind.ND_MUL :
        print('\timul rax, rdi')
    elif node.kind == asmd.NodeKind.ND_DIV :
        print('\tcqo')
        print('\tidiv rax, rdi')
    elif node.kind == asmd.NodeKind.ND_EQU :
        print('\tcmp rax, rdi')
        print('sete al')
        print('movzb rax, al')
    elif node.kind == asmd.NodeKind.ND_NEQ :
        print('\tcmp rax, rdi')
        print('\tsetne al')
        print('\tmovzb rax, al')

    print('\tpush rax')

    return
#
# コード生成　完了
#

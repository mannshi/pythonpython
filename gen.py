import asmd
#
# コード生成
#
def gen( node ):

    if node.kind == asmd.NodeKind.ND_NUM :
        print( '\tpush {0}'.format( node.val ) )
        return


    
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

    print('\tpush rax')

    return
#
# コード生成　完了
#

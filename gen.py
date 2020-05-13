import asmd
import sys
from asmd import NodeKind as ND
from asmd import typ as TYP
import json # json.dumps 用
import pprint


para_reg64 = [ "rdi", "rsi", "rdx", "rcx" ];
para_reg32 = [ "edi", "esi", "edx", "ecx" ];
para_reg8  = [ "dil", "sil", "dl",  "cl" ];

if_num = 0
#
# コード生成
#
def gen( node ):
    global if_num
    
    if node == 0:
        return

    if node.kind == ND.STRING :
        print("\tpush offset .L.strings.{0}".format( node.val ) );
        print('\tpop rax')
        print('\tmov rax, [rax]')
        print('\tpush rax')
        return


    if node.kind == ND.ADDR :
        gen_lval( node.lhs )
        return
    
    if node.kind == ND.DEREF :
        print('#DEREF START {0}'.format(node))
        print('#DEREF START {0}'.format(node.kind))

        asmd.pins( node )

        gen( node.lhs )
        print('\tpop rax')

        print('#DEREF {0}'.format( node.lhs.type.base.size ))
        size = node.lhs.type.base.size
        if size == 1:
            print('\tmovsx  rax, byte ptr [rax]')
            print('\tpush rax')
        elif size == 4:
            print('\tmovsxd rax, dword ptr [rax]')
            print('\tpush rax')
        else:
            print('\tmov rax, [rax]')
            print('\tpush rax')


        return

    if node.kind == ND.FUNCDEF :

        node.myself()

        # 関数の名前＝ラベル
        print("{0}:".format(node.name))

        # プロローグ
        print('#プロローグ')
        print('\tpush rbp')
        print('\tmov rbp, rsp')
        print('\tsub rsp, {0}'.format(node.offset))

        # レジスタの中身をパラメータにコピーする
        para_i = 0
        #para_reg64 = [ "rdi", "rsi", "rdx", "rcx" ];
        #para_reg32 = [ "edi", "esi", "edx", "ecx" ];
        #para_reg8  = [ "dil", "sil", "dl",  "cl" ];
        while para_i < node.paranum :
            print("#para{0}".format(para_i) )
            print("#para{0}".format(node.para[para_i]) )
            print("\tmov rax, rbp\n");
            #print("#DDDDEBUG {0}".format( node.para[para_i] ) )
            print("\tsub rax, {0}\n".format(node.lvars[ node.para[para_i] ].offset));
            if node.lvars_t[ node.para[para_i] ].size == 8:
                print("\tmov [rax], {0}\n".format(para_reg64[para_i]));
            elif node.lvars_t[ node.para[para_i] ].size == 4:
                print("\tmov [rax], {0}\n".format(para_reg32[para_i]));
            elif node.lvars_t[ node.para[para_i] ].size == 1:
                print("\tmov [rax], {0}\n".format(para_reg8[para_i]));
            else :
                raise asmd.ManncError('代入のサイズがおかしい')
            
            para_i += 1
            
        #asmd.llvars = node.lvars.copy()
        asmd.lvars = node.lvars.copy()
        asmd.lvars_t = node.lvars_t.copy()

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
        print('#raxtest 2')
        print('\tpush rax')
        
        return
        
    # NodeKindが、数値の場合
    # スタックにその値をプッシュする
    if node.kind == ND.NUM :
        print( '\tpush {0}'.format( node.val ) )
        return

    if node.kind == ND.BLOCK:
        for stmt in node.stmts:
            gen( stmt )
            print('#raxtest 3')
            #print('\tpush rax')
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
    if node.kind == ND.LVAR :
        gen_lval( node )
        # 配列の場合のみアドレスが指す先をメモリから読み込む処理を飛ばす
        if node.type != TYP.ARRAY:
            print('\tpop rax')
            if node.size == 1:
                print('\tmovsx rax, byte ptr [rax]')
            elif node.size == 4:
                print('\tmovsxd rax, dword ptr[rax]')
            else:
                print('\tmov rax, [rax]')
            print('\tpush rax')
        return 

    # NodeKind が代入の場合
    if node.kind == ND.ASSIGN :

        gen_lval( node.lhs )
        gen( node.rhs )

        print('\tpop rdi')
        print('\tpop rax')

        # サイズによって使用するレジスタを変える
        print('#assign size {0}'.format( node.lhs.size ))
        if node.lhs.size == 1:
            print('\tmov [rax], dil')
        elif node.lhs.size == 4:
            print('\tmov [rax], edi')
        else:
            print('\tmov [rax], rdi')

        print('\tpush rdi')

        return

    # NodeKind が reurn の場合
    if node.kind == ND.RETURN :
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
    
    if node.kind == ND.ADD :
        #ポインタの計算をする場合

        print('#addddddddddd')
        print('#add kind {0}'.format(node.lhs.kind))

        if node.lhs.kind == ND.LVAR:
            print('#add type {0}'.format(node.lhs.type))
            if node.lhs.type == TYP.PTR :
                print('\timul rdi, 4')
        print('\tadd rax, rdi')
    elif node.kind == ND.SUB :
        print('\tsub rax, rdi')
    elif node.kind == ND.MUL :
        print('\timul rax, rdi')
    elif node.kind == ND.DIV :
        print('\tcqo')
        print('\tidiv rax, rdi')
    elif node.kind == ND.EQU :
        print('\tcmp rax, rdi')
        print('sete al')
        print('movzb rax, al')
    elif node.kind == ND.NEQ :
        print('\tcmp rax, rdi')
        print('\tsetne al')
        print('\tmovzb rax, al')
    elif node.kind == ND.LT :
        print('\tcmp rax, rdi')
        print('\tsetl al')
        print('\tmovzb rax, al')
    elif node.kind == ND.LTE :
        print('\tcmp rax, rdi')
        print('\tsetle al')
        print('\tmovzb rax, al')

    print('#raxtesta5')
    print('\tpush rax')

    return
#
# コード生成　完了
#

def gen_lval(node):


    if node.kind == ND.LVAR:
        var = node.str
        

        if var in asmd.glvars_t:
            # グローバル変数の左辺値
            print("\tpush offset {0}".format( var ) );
            return

        # グローバル変数でないときにローカル変数とみなす
        print('#here {0}'.format(var))
        offset = asmd.lvars[var].offset
        #offset = node.offset
        print('#gen_lval var={0} offset={1}'.format(var, offset ) )

        print('\tmov rax, rbp')
        print('\tsub rax, {0}'.format(offset))
        print('#raxtest 6')
        print('\tpush rax')

        return 

    if node.kind == ND.DEREF:
        gen( node.lhs )
        return 

    raise asmd.ManncError('代入の左辺値が変数ではありません')

def gen_gvar():
    #if len( asmd.glvars_t ) == 0:
        #return

    # 初期化しないグローバル変数を出力する
    for gv in asmd.glvars_t:
        print('.global {0}'.format(gv) )

    print('.bss')
    for gv in asmd.glvars_t.keys():
        print('.align {0}'.format(asmd.glvars_t[gv].align) )
        print('{0}:'.format( gv ) )
        print('\t.zero {0}'.format(asmd.glvars_t[gv].size) )
        #print('\t.zero 4' )

    print('.data')
    # 初期化するグローバル変数を出力する
    # 未実装
    
    # 文字列のデータを出力する
    gen_strings()

    return

def gen_strings():
    idx = 0
    for string in asmd.strings:
        print('.align 1')
        print('.L.strings.{0}:'.format(idx))
        chi = 0
        while chi < len(string):
            print('\t.byte {0}'.format(ord(string[chi])))
            chi +=1
        print('\t.byte 0')
        idx += 1

    return

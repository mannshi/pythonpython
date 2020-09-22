from enum import Enum
import sys
from enum import IntEnum, auto
from asmd import NodeKind as ND
import asmd
import gen
import parse
import mytokenize
import testprint

###############################################
def mannc( filename ):

    #
    # トークナイズ
    #
    mytokenize.mytokenize(filename)

    print('#PRINT TKN START')
    for t in asmd.tkn:
        t.myself()
    print('#PRINT TKN END')


    #
    # パース
    #
    asmd.offset = 0
    parse.program()

    print('#PRINT glvars_t START')
    for g in asmd.glvars_t.keys():
        print('#name={0}'.format(g))
        asmd.glvars_t[ g ].myself()
    print('#PRINT glvars_t END')

    print('#offset {0}'.format(asmd.offset))

    #
    # ローカル変数のoffsetをセットする リファクタリング用
    #
    for index1 in range(len(asmd.code)):
        if asmd.code[index1].kind == ND.FUNCDEF:
            # 関数にパラメータがある場合だと
            # offsetの初期値は 56
            # そうでない場合は 0
            offset = 0
            for index2 in asmd.code[index1].lvars2.keys():
                offset = asmd.align_to( offset, \
                     asmd.code[index1].lvars2[index2].ty.align)
                offset += asmd.code[index1].lvars2[index2].ty.size
                asmd.code[index1].lvars2[index2].offset = offset
                print("#offset {0} = {1}".format( asmd.code[index1].lvars2[index2].name, asmd.code[index1].lvars2[index2].offset ) )

            asmd.code[index1].offset = offset
            print("#func offset={0}".format(offset))


    #
    # アセンブリコード出力開始
    #
    # ヘッダ
    print('.intel_syntax noprefix')

    # グローバル変数のコードを出力する
    gen.gen_gvar( )

    print('.text')
    print('.global main')


    # コード生成
    for nd in asmd.code:

        asmd.offset =   nd.offset
        asmd.lvars_t = nd.lvars_t
        asmd.lvars = nd.lvars

        # 1stmt毎にループ
        gen.gen( nd )
        # 1stmtはスタックに値を残すので rax に pop する
        #print('\tpop rax')

    #エピローグ
    #最後の式の結果がRAXに残っているのでそれが返り値になる
    #print('\tmov rsp, rbp')
    #print('\tpop rbp')

    print("\tret")    


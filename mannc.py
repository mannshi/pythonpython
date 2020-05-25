from enum import Enum
import sys
from enum import IntEnum, auto
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


from enum import Enum
import sys
from enum import IntEnum, auto
import asmd
import gen
import parse
import tokenize

###############################################
tokenize.tokenize(sys.argv[1])

print('#print tkn start')
for t in asmd.tkn:
    print("#main '{0}' , '{1}', '{2}'".format(t.kind, t.val, t.str) )
print('#print tkn end')

parse.program()

#
# アセンブリコード出力開始
#
# ヘッダ
print('.intel_syntax noprefix')
print('.global main')
print('main:')

# プロローグ
print('\tpush rbp')
print('\tmov rbp, rsp')
print('\tsub rsp, 208')

# コード生成

for nd in asmd.code:
    # 1stmt毎にループ
    gen.gen( nd )
    # 1stmtはスタックに値を残すので rax に pop する
    print('\tpop rax')

#エピローグ
#最後の式の結果がRAXに残っているのでそれが返り値になる
print('\tmov rsp, rbp')
print('\tpop rbp')

print("\tret")    


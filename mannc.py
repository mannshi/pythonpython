from enum import Enum
import sys
from enum import IntEnum, auto
import asmd
import gen
import parse
import tokenize

###############################################
print('# tokenize start')
tokenize.tokenize(sys.argv[1])
print('# tokenize end')

print('#print tkn start')
for t in asmd.tkn:
    print("#'{0}' , '{1}', '{2}'".format(t.kind, t.val, t.str) )
print('#print tkn end')

print('# parse start')
parse.program()
print('# parse end')

print('.intel_syntax noprefix')
print('.global main')
print('main:')

for nd in asmd.code:
    print(  "#root kind={0} val={1}".format(nd.kind, nd.val) )
    #print( "#left kind={0} val={1}".format(nd.lhs.kind, nd.lhs.val) )
    #print( "#rght kind={0} val={1}".format(nd.rhs.kind, nd.rhs.val) )
    #print( "#left left kind={0} val={1}".format(nd.lhs.lhs.kind, nd.lhs.lhs.val) )
    #print( "#left rght kind={0} val={1}".format(nd.lhs.rhs.kind, nd.lhs.rhs.val) )
    #print( "#rght left kind={0} val={1}".format(nd.rhs.lhs.kind, nd.rhs.lhs.val) )
    #print( "#rght rght kind={0} val={1}".format(nd.rhs.rhs.kind, nd.rhs.rhs.val) )

    gen.gen( nd )
    print('\tpop rax')

print("\tret")    


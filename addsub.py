from enum import Enum
import sys

class TokenKind(Enum):
    TK_RESERVED =  1
    TK_NUM      =  2
    TK_EOF      =  3

class NodeKind(Enum):
    ND_ADD   = 1
    ND_SUB   = 1
    ND_MUL   = 1
    ND_DIV   = 1
    ND_NUM   = 1

class Token:
    def __init__(self):
        self.kind = 0
        self.val = 0
        self.str = ''

#
# トークナイザ  
#

tkn = []

def tokenize(fname):
    with open(fname, 'rb') as f:

        offset = 0
        while True:
            f.seek( offset )
            # print("offset='{0}'".format(offset))
            chb = f.read(1)
            ch = chb.decode('utf-8')
            offset += 1
            if ch == '' :
                break
            # print("readch='{0}'".format(ch) )

            if ch == '\n' or ch == ' ':
                continue
            if ch == '+' or ch == '-' :
                newtkn = Token()
                newtkn.kind = TokenKind.TK_RESERVED
                newtkn.str = ch
                
                tkn.append( newtkn )
                continue

            if ch >= '0' and ch <= '9':
                tmpnum = ''
                # print('digit')
                while ch >= '0' and ch <= '9':
                    tmpnum += ch
                    f.seek( offset )
                    chb = f.read(1)
                    ch = chb.decode('utf-8')
                    offset += 1

                newtkn = Token()
                newtkn.kind = TokenKind.TK_NUM
                newtkn.val = int( tmpnum )
                tkn.append( newtkn )

                offset -= 1
                    
                # print("number='{0}'".format(tmpnum) )

    newtkn = Token()
    newtkn.kind = TokenKind.TK_EOF
    tkn.append( newtkn )
#
# トークナイザ  完了
#

def consume(op):
    if tkn[0].kind != TokenKind.TK_RESERVED or tkn[0].str != op :
        return False
    del tkn[0]
    return True


def expect( op ):
    if tkn[0].kind != TokenKind.TK_RESERVED or tkn[0].str != op:
        print( "'{0}'ではありません".format(op) )
        sys.exit()
    del tkn[0]
    return True

def expect_number():
    if tkn[0].kind != TokenKind.TK_NUM:
        print("数ではありません")
        sys.exit()
    
    val = tkn[0].val
    del tkn[0]
    return val

tokenize('aaa.txt')

print('.intel_syntax noprefix')
print('.global main')
print('main:')
    
print(" mov rax, {0}".format(expect_number()) )

for t in tkn:
    print("#'{0}' , '{1}', '{2}'".format(t.kind, t.val, t.str) )

while tkn[0].kind != TokenKind.TK_EOF:
    if consume( '+' ):
        print(" add rax, {0}".format(expect_number()))
        continue
    if expect( '-' ):
        print(" sub rax, {0}".format(expect_number()))
        continue
        
print(" ret")    


import sys
import asmd
from asmd import TokenKind as TK
from asmd import NodeKind as ND
from asmd import typ as TYP

def declaration():
    if asmd.tkn[0].str == 'int':
        base = asmd.TypeType( TYP.INT, 4, 4, 0, 0, 0):
    elif asmd.tkn[0].str != 'char':
        base = asmd.TypeType( TYP.INT, 1, 1, 0, 0, 0):
    else:
        raise asmd.ManncError( '変数の定義が型名からはじまりません。 1' )

    del asmd.tnk[0] 

    ptype = 0
    if asmd.tnk[0].str == '*':
        ptype = asmd.TypeType( TYP.PTR, 8, 8, 0, 0, 0 )
        lastp = ptype
        del asmd.tnk[0] 
        while asmd.tnk[0].str == '*':
            lastp.base = asmd.TypeType( TYP.PTR, 8, 8, 0, 0, 0 )
            lastp = last.base
            del asmd.tnk[0] 

    del asmd.tnk[0] 

    if asmd.tkn[0].kind != TK.IDENT:
        raise asmd.ManncError( '変数の名前がありません' )
    else:
        vname = asmd.[0].str

    del asmd.tnk[0] 

    if asmd.tkn[0].str == '[':
        if asmd.tkn[0].kind != TK.NUM:
            raise asmd.ManncError( '配列の添え字が数値ではありません' )

        # そえじの処理
        
        arraysize = asmd.tkn[0].val
        arrayt = asmd.TypeType( TYP.ARY, base.size * arraysize., base.align, array_len, , 0 )
        lastp = arrayt.base
        
        if asmd.tkn[0].str != ']':
            raise asmd.ManncError( '配列の添え字の後ろに ] がありません' )

    del asmd.tnk[0] 

    if asmd.tkn[0].str != ';':
        raise asmd.ManncError( '宣言の終わりが ; ではありません' )

    if arrayt == 0 and ptype == 0:
        return  ( base, vname )

    if arrayt != 0:
        if ptype == 0:
            arrayt.base = base
            return ( arrayt, vname )
        else:
            arrayt.base = ptype
            lastp = base
            return ( arrayt, vname )
    
    lastp = base
    return ( ptype, vname )

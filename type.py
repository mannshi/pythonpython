import sys
import asmd
from asmd import TokenKind as TK
from asmd import NodeKind as ND
from asmd import typ as TYP

def declaration( mode ):
    if asmd.tkn[0].str == 'int':
        base = asmd.TypeType( TYP.INT,  4, 4, 0, 0, 0)
    elif asmd.tkn[0].str == 'char':
        base = asmd.TypeType( TYP.CHAR, 1, 1, 0, 0, 0)
    else:
        raise asmd.ManncError( '変数の定義が型名からはじまりません。 t' )

    del asmd.tkn[0] 

    ptype = 0
    if asmd.tkn[0].str == '*':
        ptype = asmd.TypeType( TYP.PTR, 8, 8, 0, 0, 0 )
        lastp = ptype
        del asmd.tkn[0] 
        while asmd.tkn[0].str == '*':
            print('loop')
            lastp.base = asmd.TypeType( TYP.PTR, 8, 8, 0, 0, 0 )
            lastp = last.base
            del asmd.tkn[0] 
        #del asmd.tkn[0] 


    if asmd.tkn[0].kind != TK.IDENT:
        raise asmd.ManncError( '変数の名前がありません {0}'.format( asmd.tkn[0].str ))
    else:
        vname = asmd.tkn[0].str

    del asmd.tkn[0] 

    arrayt=0
    if asmd.tkn[0].str == '[':
        del asmd.tkn[0] 
        if asmd.tkn[0].kind != TK.NUM:
            raise asmd.ManncError( '配列の添え字が数値ではありません' )

        # そえじの処理
        arraylen = asmd.tkn[0].val
        arrayt = asmd.TypeType( TYP.ARRAY, base.size * arraylen, base.align, arraylen,  0, 0  )
        lastp = arrayt.base
        
        arraysize = asmd.tkn[0].val
        del asmd.tkn[0] 

        if asmd.tkn[0].str != ']':
            raise asmd.ManncError( '配列の添え字の後ろに ] がありません' )

        del asmd.tkn[0] 


    if mode == 'NOTPARA':
        if asmd.tkn[0].str != ';':
            raise asmd.ManncError( '宣言の終わりが ; ではありません{0}'.format(asmd.tkn[0].str ) )
        del asmd.tkn[0] 
    if mode == 'PARA':
        if asmd.tkn[0].str != ','and asmd.tkn[0].str != ')':
            raise asmd.ManncError( 'パラメータのおわり、区切りが , )  ではありません'.format(asmd.tkn[0].str ) )
        #del しない

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
    
    lastp.base = base

    return ( ptype, vname )

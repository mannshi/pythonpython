import asmd
from asmd import TokenKind as TK

#
# トークナイザ  
#
def mytokenize(fname):

    #
    # 関数内関数
    #

    def tk_number():
        nonlocal ch
        nonlocal offset
        # 数字の場合
        if ch >= '0' and ch <= '9':
            tmpnum = ''
            # print('digit')
            while ch >= '0' and ch <= '9':
                tmpnum += ch
                f.seek( offset )
                chb = f.read(1)
                ch = chb.decode('utf-8')
                offset += 1

            newtkn = asmd.Token()
            newtkn.kind = TK.NUM
            newtkn.val = int( tmpnum )
            asmd.tkn.append( newtkn )

            offset -= 1

    def tk_alphabet():
        nonlocal ch
        nonlocal offset

        tmpstr = ''
        while ch.isalpha():
            tmpstr += ch
            f.seek( offset )
            chb = f.read(1)
            ch = chb.decode('utf-8')
            offset +=1

        newtkn = asmd.Token()
        if tmpstr == 'if' :
            newtkn.kind = TK.IF
        elif tmpstr == 'else' :
            newtkn.kind = TK.ELSE
        elif tmpstr == 'return' :
            newtkn.kind = TK.RETURN
        elif tmpstr == 'int' :
            newtkn.kind = TK.INT
        elif tmpstr == 'char' :
            newtkn.kind = TK.CHAR
        elif tmpstr == 'sizeof' :
            newtkn.kind = TK.SIZEOF
        else :
            newtkn.kind = TK.IDENT
        newtkn.str = tmpstr
        asmd.tkn.append( newtkn )

        offset -= 1

    def tk_bikkuri():
        nonlocal ch
        nonlocal offset
        f.seek( offset )
        offset += 1
        chb = f.read(1)
        ch  = chb.decode('utf-8')

        if ch == '=' : # '!=' の場合
            newtkn = asmd.Token()
            newtkn.str = '!='
            newtkn.kind = TK.RESERVED
            asmd.tkn.append( newtkn )
        else:
            offset -= 1

    def tk_less():
        nonlocal ch
        nonlocal offset

        f.seek( offset )
        offset += 1
        chb = f.read(1)
        ch  = chb.decode('utf-8')

        newtkn = asmd.Token()
        if ch == '=' : #'<=' の場合
            newtkn.str = '<='
        else: #'<' の場合
            newtkn.str = '<'
            offset -= 1
        newtkn.kind = TK.RESERVED
        asmd.tkn.append( newtkn )

    def tk_equal():
        nonlocal ch
        nonlocal offset

        f.seek( offset )
        offset += 1
        chb = f.read(1)
        ch  = chb.decode('utf-8')

        newtkn = asmd.Token()
        if ch == '=' : #'==' の場合
            newtkn.str = '=='
        else: #'=' の場合
            newtkn.str = '='
            offset -= 1
        newtkn.kind = TK.RESERVED
        asmd.tkn.append( newtkn )

    def tk_great():
        nonlocal ch
        nonlocal offset
        f.seek( offset )
        offset += 1
        chb = f.read(1)
        ch  = chb.decode('utf-8')

        newtkn = asmd.Token()
        if ch == '=' : #'>=' の場合
            newtkn.str = '>='
        else: #'>' の場合
            newtkn.str = '>'
            offset -= 1
        newtkn.kind = TK.RESERVED
        asmd.tkn.append( newtkn )

    def tk_string():
        nonlocal ch
        nonlocal offset
    
        #offset += 1
        f.seek( offset )
        chb = f.read(1)
        ch = chb.decode('utf-8')
        tmpstr = ''
        # 文字リテラル読み込みループ開始
        while True:
            if ch == '"':
                break
            #print('string={0}'.format(ch))

            #文字列中のバックスペースはエスケープシーケンス
            if ch == '\\':
                offset += 1
                f.seek( offset )
                chb = f.read(1)
                ch = chb.decode('utf-8')

                if ch == 'n' : # 改行文字
                    ch = "\n"

                if ch.isdecimal() : # '\nnn は８進数のコード
                    cnt8 = 1
                    num8 = 0
                    while ch.isdecimal() and cnt8 <= 3:
                        if 0 <= int( ch ) <= 7 :

                            num8 *= 8
                            num8 += int( ch )

                            offset += 1
                            f.seek( offset )
                            chb = f.read(1)
                            ch = chb.decode('utf-8')

                            cnt8 += 1
                        else :
                            raise asmd.ManncError('リテラルのバックスラッシュの後ろの数値は0から7までです')
                            
                    tmpstr += chr( num8 )
                    continue
                
            tmpstr += ch
            offset += 1
            f.seek( offset )
            chb = f.read(1)
            ch = chb.decode('utf-8')
        # 文字リテラル読み込みループ終了

        #string_i 文字列の通し番号
        label = ".L.LITERAL.{0}".format( asmd.string_i )
        asmd.strings[ label ] = tmpstr
        asmd.strings_i += 1

        newtkn = asmd.Token()
        newtkn.kind = TK.STRING
        newtkn.str = label # 変数名＝ラベル
        asmd.tkn.append( newtkn )

        # ダブルクォーテーションを読み捨てる
        offset += 1
        chb = f.read(1)

    def tk_comment():
        nonlocal ch
        nonlocal offset
        
        # 次の一文字を読む
        f.seek( offset )
        chb = f.read(1)
        ch = chb.decode('utf-8')
        offset += 1
        if ch == '/': # '//' 行コメントの場合
            while True:
                f.seek( offset )
                chb = f.read(1)
                ch = chb.decode('utf-8')
                offset += 1

                if ch == '\n' :
                    offset -= 1
                    return
                
        elif ch == '*': # '/*' ブロックコメントの場合
            while True:
                f.seek( offset )
                chb = f.read(1)
                ch = chb.decode('utf-8')
                offset += 1

                if ch == '*':
                    # '*/' かどうかを調べる
                    f.seek( offset )
                    chb = f.read(1)
                    ch = chb.decode('utf-8')
                    offset += 1
                    if ch == '/':
                        return

        else:
            #その他（割り算）の場合
            newtkn = asmd.Token()
            newtkn.kind = TK.RESERVED
            newtkn.str = '/'
            asmd.tkn.append( newtkn )
            offset -= 1

    #
    # 関数内関数 おわり
    #


    #
    # ファイル読み込みループ
    #
    with open(fname, 'rb') as f:

        offset = 0
        while True:
            f.seek( offset )
            chb = f.read(1)
            ch = chb.decode('utf-8')
            offset += 1
            if ch == '' : break

            if ch == '\n' or ch == ' ' : continue

            # 一文字のトークン の場合
            if ch == ';' or ch == '+' or ch == '-' or ch == '*' or \
               ch == '(' or ch == ')' or ch == '{' or ch == '}' or \
               ch == ',' or ch == '&' or ch == '[' or ch == ']' :
                newtkn = asmd.Token()
                newtkn.kind = TK.RESERVED
                newtkn.str = ch
                asmd.tkn.append( newtkn )
                continue

            # '/' の場合（ブロックコメント、一行コメント、割り算）
            if ch == '/': tk_comment(); continue

            # '=' または '==' の場合
            if ch == '=': tk_equal(); continue

            # '<' または '<=' の場合
            if ch == '<': tk_less(); continue

            # '>' または '>=' の場合
            if ch == '>': tk_great(); continue

            # '!' の場合
            if ch == '!': tk_bikkuri(); continue

            # 変数の場合
            if ch.isalpha(): tk_alphabet(); continue

            # 文字列の場合
            if ch == '"' : tk_string(); continue

            # 数字の場合    
            tk_number()

    #
    # ファイル読み込みループ 終わり
    #

    newtkn = asmd.Token()
    newtkn.kind = TK.EOF
    asmd.tkn.append( newtkn )
#
# トークナイザ  完了
#

###############################################

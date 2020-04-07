import sys

class ExitError(Exception) : pass

def bar1():
    print( 'bar1' )

def bar2():
    raise  ExitError( 'Global Exit Dayo' )

def bar3():
    print( 'bar3' )

def foo():
    bar1()
    bar2()
    bar3()

def hoge():
    try:
        foo()
        return 200
    except ExitError as err:
        print(err)
        return 100

def hogehoge():
    print(hoge())

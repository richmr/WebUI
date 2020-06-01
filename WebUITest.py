from WebUI import WebUI, WebUIHandler

def test1():
    kargs = {"requestHandler":WebUIHandler,
            "browser":"firefox"}
    test = WebUI(**kargs)
    test.go()
    # working

test1()

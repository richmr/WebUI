from WebUI import WebUI, WebUIHandler

# May need to add firefox to path in Windows


def test1():
    kargs = {"requestHandler":WebUIHandler,
            "browser":"firefox",
            "startpage":"opscheck.html"}
    test = WebUI(**kargs)
    test.go()
    # working

test1()

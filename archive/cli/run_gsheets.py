"""

Created by: Nathan Starkweather
Created on: 02/14/2016
Created in: PyCharm Community Edition


"""
import goffice.context
import goffice.worksheet

__author__ = 'Nathan Starkweather'

from db_stuff import google_loader
import lxml.etree


def main():
    g = google_loader.open_client()
    d = g.get_drive()
    wbs = d.get_workbooks()
    return wbs


def main2():
    import goffice
    fp = google_loader.load_keypath("_exp_auth_key.json")

    goffice.authorize_client(fp)
    with open("ws_feed.xml", 'rb') as f:
        content = f.read()
    root = lxml.etree.fromstring(content)
    parent = goffice.context.GSheetsAPIContext()
    for elem in root.iter("{*}entry"):
        ws = goffice.worksheet.GWorksheet.from_elem(elem, parent)
    return [ws]


def test_add_ws_xml():
    import goffice.urls as urls
    url, msg = urls.add_ws_url('mytitle', 24, 56, "foobar", "12345", 'private', 'full')
    print(url)
    print(msg)
    return url, msg


def test_add_ws():
    c = google_loader.open_client()
    d = c.get_drive()
    s = d.get_workbooks()[0]
    worksheets = s.get_worksheets()
    return worksheets.add_worksheet("myworksheet")


def test_rename_ws(ws):
    return ws.set_title('foobar')


def test_open_ws(name):
    c = google_loader.open_client()
    d = c.get_drive()
    wbs = d.get_workbooks()
    print(wbs)
    wb = wbs[0]
    wss = wb.get_worksheets()
    print(wss[name])


def test_get_list_feed():
    pass


def test_del_ws(ws):
    ws.delete()


def test_make_rename_del():
    ws = test_add_ws()
    test_rename_ws(ws)
    test_del_ws(ws)
    return ws

if __name__ == '__main__':
    # m = main()
    # print(m[0])
    # wb = m[0]
    # wss = main2()  # wb.get_worksheets()
    # print(wss)
    # ws = wss[0]
    # print(ws)
    # print(dir(ws))
    test_make_rename_del()
    test_open_ws('TTM')
    from goffice import GHTTPSession
    sdt = GHTTPSession.sdt
    import json
    with open("C:/.replcache/gsheets_mock_rsp.json", 'w') as f:
        json.dump(sdt, f, indent=4)
    pass


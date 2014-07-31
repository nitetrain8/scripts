from xml.etree.ElementTree import parse as xml_parse
from urllib.request import urlopen
from io import BytesIO


def call_hello(url):
    req = urlopen(url)
    txt = req.read()
    buf = BytesIO(txt)
    tree = xml_parse(buf)
    root = tree.getroot()
    return root


def getMainValues(ipv4='192.168.1.6'):
        url = "http://%s/webservice/interface/?&call=getMainValues" % ipv4
        return call_hello(url)

def getAdvancedValues(ipv4='192.168.1.6'):
    url = "http://%s/webservice/interface/?&call=getAdvancedValues" % ipv4
    return call_hello(url)


def dump_elem(elem):
    if len(elem) > 0:
        for e in elem:
            dump_elem(e)
        print(elem)
    else:
        print(elem, elem.text)


def _parse_adv_values_xml(root, values):
    riter = iter(root)
    reply = next(riter)
    message = next(riter)
    miter = iter(message)
    cluster = next(miter)
    citer = iter(cluster)
    name = next(citer)
    nametxt = name.text
    nelements = next(citer)
    values[nametxt] = OrderedDict()
    for e in citer:
        vname = e[0]
        vval = e[1]
        values[nametxt][vname.text] = vval.text




def _parse_main_values_xml(root, values):
    riter = iter(root)
    reply = next(riter)
    message = next(riter)
    miter = iter(message)
    cluster = next(miter)
    citer = iter(cluster)
    message2 = next(citer)
    nelements = next(citer)
    for e in citer:
        assert e.tag == 'Cluster'
        c2iter = iter(e)
        ename = next(c2iter)
        name = ename.text
        values[name] = OrderedDict()
        nelems2 = next(c2iter)
        for vtype in c2iter:
            vtiter = iter(vtype)
            vname = next(vtiter)
            val = next(vtiter)

            values[name][vname.text] = val.text


from collections import OrderedDict

values = {}
tkroot = None
labels = None
mframe = None


def init_parse(getfunc, parsefunc, ns):
    while True:
        root = getfunc()
        try:
            parsefunc(root, ns)
        except StopIteration:
            # Stopiteration indicates bad xml, try again
            # Todo non horrible way of doing this
            sleep(0.1)
            continue
        else:
            return


def showMainValues():

    global tkroot
    global labels
    global mframe
    global values

    from tkinter import Tk, N, W
    from tkinter.ttk import LabelFrame, Label

    # first run, set up the thingy
    print("Setting up Main Values...")
    init_parse(getMainValues, _parse_main_values_xml, values)

    sleep(0.5)

    print("Setting up Advanced Values...")
    init_parse(getAdvancedValues, _parse_adv_values_xml, values)

    print("initializing tkinter interface...")

    tkroot = Tk()
    mframe = LabelFrame(tkroot, text="Main Frame")
    labels = {}
    for group in values:
        lframe = LabelFrame(mframe, text=group)
        labels[group] = OrderedDict()
        labels[group]['frame'] = lframe
        for param, pv in values[group].items():
            labels[group][param] = {}
            plabel = Label(lframe, text=param)
            vlabel = Label(lframe, text=pv)
            labels[group][param]['plabel'] = plabel
            labels[group][param]['vlabel'] = vlabel

    mframe.grid()
    for i, group in enumerate(labels):
        for param in labels[group]:
            if param == 'frame':
                labels[group][param].grid(column=i, row=0, sticky=N)
            else:
                labels[group][param]['plabel'].grid(sticky=W)
                labels[group][param]['vlabel'].grid(sticky=W)

    tkroot.grid()

    print('setting up polling intervals')

    tkroot.after(500, poll_main_values)
    tkroot.after(750, poll_adv_values)

    print('Ready')

    tkroot.mainloop()
    print("afterloop")

    # while True:
    #     root = getMainValues()
    #     _parse_main_values_xml(root, values)

    # for group, group_vals in values.items():
    #     print("Group:", group)
    #     for param, pv in group_vals.items():
    #         print("", param, "=", pv)
    #
    # print()

from time import sleep


def poll_main_values():
    global mvhb
    root = getMainValues()
    try:
        _parse_main_values_xml(root, values)
    except:
        pass
    else:
        # sleep(.5)
        # root = getAdvancedValues()
        # _parse_adv_values_xml(root, values)
        mvhb += 1
        heartbeat()
        for name, groupdict in values.items():
            group = labels[name]
            for param, pv in groupdict.items():
                group[param]['vlabel'].config(text=pv)

    tkroot.after(500, poll_main_values)


mvhb = 0
avhb = 0
mflabel = "MV: %s  AV: %s"

MVHB_SUCCESS = 0x1
MVHB_FAILURE = 0x0
AVHB_SUCCESS = 0x3
AVHB_FAILURE = 0x2

def heartbeat():
    global mframe
    global avhb
    global mvhb
    global mflabel

    mframe.config(text=mflabel % (str(mvhb), str(avhb)))


def poll_adv_values():
    global avhb
    root = getAdvancedValues()
    try:
        _parse_adv_values_xml(root, values)
    except:
        pass
    else:
        avhb += 1
        heartbeat()
        for name, groupdict in values.items():
            group = labels[name]
            for param, pv in groupdict.items():
                group[param]['vlabel'].config(text=pv)

    tkroot.after(500, poll_adv_values)


if __name__ == '__main__':
    try:
        showMainValues()
    except:
        print(getMainValues()[0].text)
        raise
    # from tkinter import Tk
    # from tkinter.ttk import LabelFrame, Label
    # root = Tk()
    # frame = LabelFrame(root, text='hello world')
    # label= Label(frame, text="bye world")
    # label.grid()
    # frame.grid()
    # root.grid()
    # root.mainloop()


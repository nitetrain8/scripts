from hello import hello
from hello import hello3  
from time import sleep


# Main Gas, CO2 Request, N2 Request, O2 Request, CO2 Expected, N2 Expected, O2 expected, Air Expected
_flow_requests_v2 = {
    '15': [
        (0.5, 10, 25, 25, 0.05, 0.125, 0.125, 0.20),
        (1.0, 10, 25, 25, 0.10, 0.25, 0.25, 0.40)
    ],
    '3': [
        (0.25, 25, 25, 100, 0.063, 0.063, 0.100, 0.125),
        (0.50, 25, 25, 100, 0.10, 0.125, 0.100, 0.275)
    ],
    '80': [
        (2, 10, 25, 20, .20, .5, .4, .9),
        (5, 10, 25, 20, .5, 1.25, 1.0, 2.25),
    ]
}

_flow_requests_v3 = _flow_requests_v2.copy()
_flow_requests_v3['3'] = [
    (0.25, 25, 15, 20, 0.0625, .0375, 0.05, 0.100),
    (0.50, 25, 15, 20, 0.10, .075, 0.100, 0.225)
]

def check_float(f1, f2, mfc, prec=3):
    f1 = round(f1, prec)
    f2 = round(f2, prec)
    diff = f1 - f2
    if abs(diff / f1) > 0.05:  # 5% error after rounding
        print("%s flow: %s != %s (FAIL)" % (mfc, f1, f2))
        return True
    else:
        print("%s flow: %s == %s" % (mfc, f1, f2))
        return False

def test_flow(sz, app, version):
    _reqs = _flow_requests_v3 if version >= (3,) else _flow_requests_v2
    try:
        params = _reqs[sz]
    except (IndexError, KeyError):
        raise NotImplementedError("Don't have data for size %sL" % sz) from None
    f = 0
    for p in params:
        mg, co2r, n2r, o2r, co2a, n2a, o2a, aa = p
        app.login()
        print("Setting Main Gas to %.2f LPM" % mg)
        app.setmg(1, mg)
        print("Setting DO to %d%% N2, %d%% O2" % (n2r, o2r))
        app.setdo(1, n2r, o2r)
        print("Setting pH to %d%% CO2" % co2r)
        app.setph(1, co2r, 0)

        print("Waiting 5 seconds for gases to stabilize.")
        sleep(5)

        print("Checking values...\n")

        if version >= (3,):
            mv = app.gpmv()
            got_co2 = mv['MFCs']['co2']
            got_air = mv['MFCs']['air']
            got_n2 = mv['MFCs']['n2']
            got_o2 = mv['MFCs']['o2']
        else:
            adv = app.getadvv()
            got_co2 = adv["MFCCO2FlowFeedback(LPM)"]
            got_n2 = adv["MFCN2FlowFeedback(LPM)"]
            got_o2 = adv["MFCO2FlowFeedback(LPM)"]
            got_air = adv["MFCAirFlowFeedback(LPM)"]

        f |= check_float(co2a, got_co2, "CO2")
        f |= check_float(n2a, got_n2, "N2")
        f |= check_float(o2a, got_o2, "O2")
        f |= check_float(aa, got_air, "Air")
        print()
    if not f:
        print("ALL TESTS PASSED")
    else:
        print("TEST FAILED")

def usage():
    import os
    head = os.path.split(__file__)[1]
    print("Usage:", head, "[IP] [Size] [Version=3]")

def prompt_for_input():
    while True:
        line = input("Enter command line: ").split()
        try:
            ip = line[0]
            sz = line[1]
            try:
                version = line[2]
            except IndexError:
                version = "3"
            version = [int(i) for i in version.split(".")]
        except Exception as e:
            print("Invalid command line: %r"%str(e))
            usage()
        else:
            break
    return ip, sz, tuple(version)

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        usage()
        ip, sz, version = prompt_for_input()
    else:
        try:
            ip = sys.argv[1]
            sz = sys.argv[2]
            try:
                version = sys.argv[3]
            except IndexError:
                version = "3"
            version = [int(i) for i in version.split(".")]
            version = tuple(version)
        except ValueError:
            print("Invalid command line")
            usage()
            prompt_for_input()
    while True:
        try:
            if version >= (3,):
                app = hello3.open_hello(ip)
            else:
                app = hello.open_hello(ip)
            test_flow(sz, app, version)
        except Exception as e:
            import traceback
            traceback.print_exc()
        ip, sz, version = prompt_for_input()
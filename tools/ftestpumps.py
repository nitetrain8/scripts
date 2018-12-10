from hello import hello, hello3
from time import sleep

class Pump():
    pname = "Pump"
    def __init__(self, func_name, val2, on_sleep, off_sleep):
        self.func_name = func_name
        self.val2 = val2
        self.on_sleep = on_sleep
        self.off_sleep = off_sleep
    def turn_on(self, app, val2=None):
        val2 = val2 or self.val2
        getattr(app, self.func_name)(1, val2)
    def turn_off(self, app):
        getattr(app, self.func_name)(0, self.val2)
    def test_cycle(self, app):
        self.turn_on(app)
        sleep(self.on_sleep)
        self.turn_off(app)
        sleep(self.off_sleep)

class MediaPump(Pump):
    pname = "Media Pump"
    def __init__(self, on_time, off_time):
        super().__init__('setpumpa', 500, on_time, off_time)
        
class AddnA(Pump):
    pname = "Addition A"
    def __init__(self, on_time, off_time):
        super().__init__('setpumpb', 3, on_time, off_time)
        
class AddnB(Pump):
    pname = "Addition B"
    def __init__(self, on_time, off_time):
        super().__init__('setpumpc', 3, on_time, off_time)
        
class Sample(Pump):

    @property
    def pname(self):
        name = "Sample "
        if self.val2 == 1:
            name += "(CCW)"
        else:
            name += "(CW)"
        return name

    def __init__(self, on_time, off_time):
        super().__init__('setpumpsample', 0, on_time, off_time)   
        
media_pump_80 = MediaPump(1, 3.5)
media_pump_3 = MediaPump(1, 2)
addna = AddnA(1, 2)
addnb = AddnB(1, 2)
sample = Sample(1, 2)
        
def test_pumps(ip, sz=80, v=3, cycles=10):
    print("Connecting...")
    if v == 3:
        app = hello3.HelloApp(ip)
    elif v == 2:
        app = hello.HelloApp(ip)
    else:
        raise ValueError("Invalid hello version: '%s'"%v)
        
    app.login()
        
    if sz == 80 or sz == 15:
        media_pump = media_pump_80
    elif sz == 3:
        media_pump = media_pump_3
    else:
        raise ValueError("Invalid size: %r" % sz)
    
    sample.val2 = 0
    print("Beginning test...")
    for pump in (media_pump, addna, addnb, sample):
        for i in range(cycles):
            print("Testing %s %d of %d" % (pump.pname, i+1, cycles))
            pump.test_cycle(app)
        print()
    
    sample.val2 = 1
    
    for i in range(cycles):
        print("Testing sample (CCW) %d of %d" % (i+1, cycles))
        sample.test_cycle(app)


def usage():
    print("Usage: ftestpumps [ip] [size] [cycles]")


def get_args(l):
    try:
        ip, sz = l[:2]
    except (ValueError, IndexError):
        usage()
        return None

    try:
        version = int(l[2])
    except IndexError:
        version = 3

    try:
        cycles = int(l[3])
    except IndexError:
        cycles = 10

    try:
        return ip, int(sz), version, cycles
    except ValueError:
        print("Invalid Arguments:", l)


def main():
    import sys
    if len(sys.argv) > 1:
        ip, sz, v, cycles = get_args(sys.argv[1:])
        test_pumps(ip, sz, v, cycles)
    
    while True:
        line = input("Enter [IP] [Size] [Version=3] [Cycles=10]: ").split()
        args = get_args(line)
        if args is None:
            print("Invalid args")
            continue
        ip, sz, v, cycles = args
        test_pumps(ip, sz, v, cycles)
    

if __name__ == '__main__':
    main()

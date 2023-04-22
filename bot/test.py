a = True


def w():
    global a
    a = False


def ww():
    global a
    print(a)


w()
ww()

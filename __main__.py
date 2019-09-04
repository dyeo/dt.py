import dt

class cls1(object):
    b = None

class cls0(object):
    a = cls1()

# "a:[{a:1} {a:2} {a: [ 0 1 2 ] c: {b:[0 1.0 2]}}]"
o = dt.loadso("a:{b:'c'}", cls0)
print(o.a.b)
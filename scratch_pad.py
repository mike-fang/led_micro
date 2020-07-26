class Context:
    def __init__(self):
        print('init')
    def __enter__(self):
        print('enter')
        return self
    def __exit__(self, type, value, tb):
        print('exit')
    def f(self, a, b, c=None):
        print('a', a)
        print('b', b)
        if c:
            print('c', c)

with Context() as f:
    f.f(1 ,3)


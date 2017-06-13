

def xor(xor, data):
    while len(xor) < len(data):
        xor+=xor
    return "".join(chr(ord(x) ^ ord(y)) for x, y in zip(xor, data))

def unxor(xor, data):
    while len(xor) < len(data):
        xor+=xor
    return "".join(chr(ord(y) ^ ord(x)) for x, y in zip(xor, data))

x_key='fc23759df40c26ab'.decode('hex')
x=xor(x_key, 'hello world!')
print x
ux=unxor(x_key,x)
print ux

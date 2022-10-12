
def mystery(n):
    v = 0
    for i in range(1,n+1):
        v+=int(str(i)*i)
    return v

print(mystery(4))
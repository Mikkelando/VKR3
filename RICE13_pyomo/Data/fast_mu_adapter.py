a = input()
a_new = [1.2*float(el) for el in a.split(';')]
for el in a_new:
    print(el, end=';')
import numpy as np

l = 8
C = np.zeros([l,l])
E = np.zeros([l,l])
G = np.zeros([l,l])
L = np.zeros([l,l])
O = np.zeros([l,l])
R = np.zeros([l,l])

C[:2]    = 1
C[-2:]   = 1
C[:, :2] = 1

E[:2]     = 1
E[-2:]    = 1
E[3:5, :] = 1
E[:, :2]  = 1

G[:2]     = 1
G[-2:]    = 1
G[:, :2]  = 1
G[4, 5]   = 1
G[4:, 6:] = 1

L[:, :2] = 1
L[-2:]   = 1

O += 1
O[2:6, 2:6] = 0

R[:, :2]    = 1
R[:2, :]    = 1
R[:5, -2:]  = 1
R[4:6, :-1] = 1
R[-2, 5:7]  = 1
R[-1, -2:]  = 1


def pretty_print(x):
	colors = [ "\033[90m _", "\033[92m x"]
	fn = lambda i: colors[int(i)]
	for r in x:
		print(''.join(map(fn, r)))
	print("\033[00m")

if __name__ == '__main__':
	pretty_print(C)
	pretty_print(E)
	pretty_print(G)
	pretty_print(L)
	pretty_print(O)
	pretty_print(R)
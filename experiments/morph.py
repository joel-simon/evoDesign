def make_array(n, v=0.0):
    if type(v) == type(lambda n:n):
        return [[v() for x in range(n)] for y in range(n)]
    else:
        return [[v for x in range(n)] for y in range(n)]

def spread_morphogen(A, I, Pa, Pi, Da, Di, Ra, Ri,
                    steps=1000, saturate=False,
                    step=None):
    rows = len(A)
    cols = len(A[0])

    if type(Pa) == type(1.0):
        PA = make_array(rows, Pa)
    else:
        PA = Pa

    if type(Pi) == type(1.0):
        PI = make_array(rows, Pi)
    else:
        PI = Pi

    A_next = make_array(rows, cols)
    I_next = make_array(rows, cols)

    foo = [[ (0, -1),(1,0),(0,1),(-1, 1),(-1, 0),(-1,-1) ],
            [ (1, -1),(1,0),(1,1),(0,1),(-1, 0),(0,-1) ]]

    for s in range(steps):
        for r in range(rows):
            for c in range(cols):
                a = A[r][c]
                i = I[r][c]

                a_2 = a * a
                if saturate:
                    a_2 /= (1+.2*a_2)

                if i != 0:
                    prod_a = (a_2 / i) + PA[r][c]
                else:
                    prod_a = a_2 + PA[r][c]

                prod_i = a*a + PI[r][c]

                a_diff = 0.0
                i_diff = 0.0
                for _r, _c in foo[c%2]:
                    if (r+_r >=0 and r+_r < rows) and (c+_c >=0 and c+_c < cols):
                        a_diff += A[r+_r][c+_c] - a
                        i_diff += I[r+_r][c+_c] - i

                # Sum the production, diffusion and decay components
                A_next[r][c] = a + prod_a - (Ra * a) + Da*a_diff
                I_next[r][c] = i + prod_i - (Ri * i) + Di*i_diff

        A_next, A = A, A_next
        I_next, I = I, I_next
        if s%20 == 0:
            if step:
                step(A)
        if s%100 == 0:
            print(s)

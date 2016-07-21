cpdef make_array(n, v=0.0):
    # if type(v) == type(lambda n:n):
    return [[v for x in range(n)] for y in range(n)]
    # else:
        # return [[v for x in range(n)] for y in range(n)]

cpdef spread_morphogen(A, H, double Da, double Di, double Ra, double Ri,
                    double Pa, double Pi, short steps=1000, saturate=False,
                    step=None):

    cdef short rows, cols, s, r, c, _r, _c
    cdef double a, h, a_2, prod_a, prod_h, a_diff, h_diff

    rows = len(A)
    cols = len(A[0])

    A_next = make_array(rows, cols)
    H_next = make_array(rows, cols)

    foo = [[ (0, -1),(1,0),(0,1),(-1, 1),(-1, 0),(-1,-1) ],
            [ (1, -1),(1,0),(1,1),(0,1),(-1, 0),(0,-1) ]]

    for s in range(steps):
        for r in range(rows):
            for c in range(cols):
                a = A[r][c]
                h = H[r][c]
                a_2 = a * a
                if saturate:
                    a_2 /= (1+.2*a_2)

                if h != 0:
                    prod_a = (a_2 / h) + Pa
                else:
                    prod_a = a_2 + Pa

                prod_h = a*a + Pi

                a_diff = 0.0
                h_diff = 0.0
                for _r, _c in foo[c%2]:
                    if (r+_r >=0 and r+_r < rows) and (c+_c >=0 and c+_c < cols):
                        a_diff += A[r+_r][c+_c] - a
                        h_diff += H[r+_r][c+_c] - h

                # Sum the production, diffusion and decay components
                A_next[r][c] = a + prod_a - (Ra * a) + Da*a_diff
                H_next[r][c] = h + prod_h - (Ri * h) + Di*h_diff

        A_next, A = A, A_next
        H_next, H = H, H_next
        if s%5 == 0:
            if step:
                step(A)
        if s%100 == 0:
            print(s)

import math
def make_array(n, v=0.0):
    # if type(v) == type(lambda n:n):
    return [[v for x in range(n)] for y in range(n)]
    # else:
        # return [[v for x in range(n)] for y in range(n)]

# cpdef run(A, I, PA, PI, double Da, double Di, double Ra, double Ri,
                    # short steps=1000, saturate=False):
def run(A, I, PA, PI, Da, Di, Ra, Ri,
         steps=1000, saturate=False):

    # cdef short rows, cols, s, r, c, _r, _c
    # cdef double a, i, Pa, Pi, a_2, a_prod, i_prod, a_diff, i_diff

    rows = len(A)
    cols = len(A[0])

    A_next = make_array(rows, cols)
    I_next = make_array(rows, cols)

    foo = [[ (0, -1),(1,0),(0,1),(-1, 1),(-1, 0),(-1,-1) ],
            [ (1, -1),(1,0),(1,1),(0,1),(-1, 0),(0,-1) ]]

    for s in range(steps):
        for r in range(rows):
            for c in range(cols):
                a = A[r][c]
                i = I[r][c]
                Pa = PA[r][c]
                Pi = PI[r][c]

                a_2 = a * a
                if saturate:
                    a_2 /= (1+.2*a_2)

                if i != 0:
                    a_prod = (a_2 / i) + Pa
                else:
                    a_prod = a_2 + Pa

                i_prod = a*a + Pi

                a_diff = 0.0
                i_diff = 0.0
                for _r, _c in foo[c%2]:
                    if (r+_r >=0 and r+_r < rows) and (c+_c >=0 and c+_c < cols):
                        a_diff += A[r+_r][c+_c] - a
                        i_diff += I[r+_r][c+_c] - i

                # Sum the production, diffusion and decay components
                A_next[r][c] = a + a_prod - (Ra * a) + Da*a_diff
                I_next[r][c] = i + i_prod - (Ri * i) + Di*i_diff


        A_next, A = A, A_next
        I_next, I = I, I_next


    for r in range(rows):
        for c in range(cols):
            if math.isnan(A[r][c]):
                print('nan in A! Da=%f, Di=%f, Ra=%f, Ri=%f'%(Da, Di, Ra, Ri))
            if math.isnan(I[r][c]):
                print('nan in I! Da=%f, Di=%f, Ra=%f, Ri=%f'%(Da, Di, Ra, Ri))
            assert(not math.isnan(A[r][c]))
            assert(not math.isnan(I[r][c]))
            # i = I[r][c]

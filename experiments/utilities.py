def max_area_histogram(heights):
    """ Solve the 'largest rectangle under histogram' problem.
        http://www.geeksforgeeks.org/largest-rectangle-under-histogram/
    """
    S = [] # stack to store heights.
    max_area = 0
    i = 0

    while i < len(heights):
        if (len(S) == 0) or (heights[S[-1]] <= heights[i]):
            S.append(i)
            i += 1
        else:
            tp = S.pop()
            area_with_top = heights[tp] * (i if len(S) == 0 else i - S[-1] - 1)
            if max_area < area_with_top:
                max_area = area_with_top

    while len(S):
        tp = S.pop()
        area_with_top = heights[tp] * (i if len(S) == 0 else i - S[-1] - 1)
        if max_area < area_with_top:
            max_area = area_with_top

    return max_area

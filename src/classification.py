def f1_score(true, pred):
    assert(len(pred) == len(true))
    tp = 0 # true positives.
    fp = 0 # false positives.
    fn = 0 # false positives.
    precision = 0
    accuracy = 0

    for p, t in zip(pred, true):
        if p and t:
            tp += 1
        elif p and not t:
            fp += 1
        elif not p and t:
            fn += 1

    if tp == 0 or tp+fp == 0 or tp+fn == 0:
        return 0

    precision = tp / float(tp + fp)
    recall = tp / float(tp+fn)

    return 2 * precision * recall / (precision + recall)


if __name__ == '__main__':
    # import sklearn
    from sklearn.metrics import f1_score as sklearn_f1
    from numpy.random import randint
    true = [0,0,0]
    pred = [0,0,0]
    assert(f1_score(true, pred) == sklearn_f1(true, pred))
    for i in range(100):
        true = list(randint(0,2, (10)))
        pred = list(randint(0,2, (10)))
        assert(f1_score(true, pred) == sklearn_f1(true, pred))


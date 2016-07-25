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


def precision_recall(true, pred):
    assert(len(pred) == len(true))
    tp = 0 # true positives.
    fp = 0 # false positives.
    fn = 0 # false positives.
    precision = 0
    recall = 0

    for p, t in zip(pred, true):
        if p and t:
            tp += 1
        elif p and not t:
            fp += 1
        elif not p and t:
            fn += 1

    # if tp == 0 or tp+fp == 0 or tp+fn == 0:
    #     return 0,0
    if tp+fp != 0:
        precision = tp / float(tp + fp)

    if tp+fn != 0:
        recall = tp / float(tp+fn)

    return precision, recall

def joel_score(true, pred):
    tp = 0
    tn = 0
    # TODO use bitwise
    for p, t in zip(pred, true):
        if p and t:
            tp += 1
        elif not p and not t:
            tn += 1

    return (tn/float(len(true) - sum(true)) + tp/float(sum(true)))/2

if __name__ == '__main__':
    # import sklearn
    from sklearn.metrics import f1_score as sklearn_f1
    from sklearn.metrics import roc_auc_score, accuracy_score
    from numpy.random import randint
    # true = [1,1,0,1,1]
    # pred = [1,1,1,1,1]
    true = [0,0,1,0,1]
    pred = [0,0,0,0,1]
    # print f1_score(true, pred)
    print sklearn_f1(true, pred)
    # print accuracy_score(true,pred, sample_weight=[1,1,4,1,1])
    print joel_score(true, pred)
    # print roc_auc_score(true, pred)
    # true = [0,0,0]
    # pred = [0,0,0]
    # assert(f1_score(true, pred) == sklearn_f1(true, pred))
    # for i in range(100):
    #     true = list(randint(0,2, (10)))
    #     pred = list(randint(0,2, (10)))
    #     assert(f1_score(true, pred) == sklearn_f1(true, pred))


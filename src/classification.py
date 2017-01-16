def precision_recall(true, pred):
    assert(len(pred) == len(true))
    tp = 0 # True positives.
    fp = 0 # False positives.
    fn = 0 # False negatives.
    precision = 0
    recall = 0

    for p, t in zip(pred, true):
        if p and t:
            tp += 1
        elif p and not t:
            fp += 1
        elif not p and t:
            fn += 1

    if tp+fp != 0:
        precision = tp / float(tp + fp)

    if tp+fn != 0:
        recall = tp / float(tp+fn)

    return precision, recall

def f1_score(true, pred):
    precision, recall = precision_recall(true, pred)
    if precision + recall == 0:
        return 0
    return 2 * precision * recall / (precision + recall)

def balanced_accuracy_score(true, pred):
    true_pos = 0
    true_neg = 0

    num_pos = float(sum(true))
    num_neg = len(true) - num_pos

    for p, t in zip(pred, true):
        if p and t:
            true_pos += 1
        elif not p and not t:
            true_neg += 1

    a = true_neg / num_neg
    b = true_pos / num_pos

    return (a+b)/2

if __name__ == '__main__':
    # import sklearn
    from sklearn.metrics import f1_score as sklearn_f1
    from sklearn.metrics import roc_auc_score, accuracy_score
    from numpy.random import randint
    # true = [1,1,0,1,1]
    # pred = [1,1,1,1,1]
    true = [1,1,1,1,0,1]
    pred = [1,1,1,1,1,1]
    print sklearn_f1(true, pred)
    print roc_auc_score(true, pred)
    print(balanced_accuracy_score(true, pred))

    true = [0,0,0,0,1,0]
    pred = [0,0,0,0,0,0]
    print sklearn_f1(true, pred)
    print roc_auc_score(true, pred)
    print(balanced_accuracy_score(true, pred))


    # # print accuracy_score(true,pred, sample_weight=[1,1,4,1,1])
    # print balanced_accuracy_score(true, pred)
    # print roc_auc_score(true, pred)
    # true = [0,0,0]
    # pred = [0,0,0]
    # assert(f1_score(true, pred) == sklearn_f1(true, pred))
    # for i in range(100):
    #     true = list(randint(0,2, (10)))
    #     pred = list(randint(0,2, (10)))
    #     assert(f1_score(true, pred) == sklearn_f1(true, pred))

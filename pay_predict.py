import sys



def main():
    pass


if __name__ == '__main__':
    main()


class decisionnode(object):

    def __init__(self, col=-1, value=None, results=None, tb=None, fb=None):
        self.col = col
        self.value = value
        self.results = results
        self.tb = tb
        self.fb = fb


def divideset(rows, column, value):
    split_function = None
    if isinstance(value, int) or isinstance(value, float):
        split_function = lambda row: row[column] >= value
    else:
        split_function = lambda row: row[column] == value

    set1 = [row for row in rows if split_function(row)]
    set2 = [row for row in rows if not split_function(row)]
    return set1, set2


def uniquecounts(rows):
    results = {}
    for row in rows:
        r = row[len(row)-1]
        if r not in results:
            results[r] = 0
        results[r] += 1
    return results


def giniimpurity(rows):
    total = len(rows)
    counts = uniquecounts(rows)
    imp = 0
    for k1 in counts:
        p1 = float(counts[k1]) / total
        for k2 in counts:
            if k1 == k2: continue
            p2 = float(counts[k2]) / total
            imp += p1*p2
    return imp


def entropy(rows):
    from math import log
    log2 = lambda x: log(x) / log(2)
    results = uniquecounts(rows)
    ent = 0.
    for r in results.keys():
        p = float(results[r]) / len(rows)
        ent -= p*log2(p)
    return ent


def buildtree(rows, ex=[], scoref=entropy):
    if len(rows) == 0:
        return decisionnode()
    current_score = scoref(rows)

    best_gain = 0.
    best_criteria = None
    best_sets = None

    column_count = len(rows[0]) - 1
    for col in range(column_count):
        if col in ex:
            continue

        column_values = {}
        for row in rows:
            column_values[row[col]] = 1
        for value in column_values:
            set1, set2 = divideset(rows, col, value)
            p = float(len(set1)) / len(rows)
            gain = current_score - p*scoref(set1) - (1-p)*scoref(set2)
            if gain>best_gain and len(set1)>0 and len(set2)>0:
                best_gain = gain
                best_criteria = (col, value)
                best_sets = (set1, set2)

    if best_gain > 0:
        col = best_criteria[0]
        trueBranch = buildtree(best_sets[0], ex+[col])
        falseBranch = buildtree(best_sets[1], ex+[col])
        return decisionnode(col=best_criteria[0], value=best_criteria[1],
            tb=trueBranch, fb=falseBranch)
    return decisionnode(results=uniquecounts(rows))


def printtree(tree, indent=''):
    if tree.results != None:
        print str(tree.results)
    else:
        print str(tree.col) + ':' + str(tree.value) + '? '
        print indent + 'T->',
        printtree(tree.tb, indent+'  ')
        print indent+'F->',
        printtree(tree.fb, indent+'  ')


def getwidth(tree):
    if tree.tb == None and tree.fb == None:
        return 1
    return getwidth(tree.tb) + getwidth(tree.fb)


def getdepth(tree):
    if tree.tb == None and tree.fb == None:
        return 0
    return max(getdepth(tree.tb), getdepth(tree.fb)) + 1


def drawtree(tree, fname='tree.png', coding='PNG'):
    from PIL import Image, ImageDraw
    w = getwidth(tree)*100
    h = getdepth(tree)*100+120

    img = Image.new('RGB', (w,h), (255,255,255))
    draw = ImageDraw.Draw(img)

    drawnode(draw, tree, w/2, 20)
    img.save(fname, coding)


def leaf_text(results):
    max_k = None
    max_v = None
    s = 0
    for k, v in results.items():
        s += v
        if max_v is None or v > max_v:
            max_v = v
            max_k = k
    return '%s: %d%% %d%%' % (max_k,
                              max_v*100/s,
                              s*100/total)

def drawnode(draw, tree, x, y):
    if tree.results == None:
        w1 = getwidth(tree.fb)*100
        w2 = getwidth(tree.tb)*100

        left = x-(w1+w2)/2
        right = x+(w1+w2)/2

        draw.text((x-20,y-10), str(tree.col)+':'+str(tree.value), (0,0,0))
        draw.line((x,y,left+w1/2,y+100), fill=(255,0,0))
        draw.line((x,y,right-w2/2,y+100), fill=(255,0,0))

        drawnode(draw, tree.fb, left+w1/2, y+100)
        drawnode(draw, tree.tb, right-w2/2, y+100)
    else:
        txt = ' \n'.join(['%s:%d'%v for v in tree.results.items()])
        txt = leaf_text(tree.results)
        draw.text((x-20,y), txt, (0,0,0))


def classify(observation, tree):
    if tree.results != None:
        return tree.results
    v = observation[tree.col]
    branch = None
    if isinstance(v, int) or isinstance(v, float):
        if v >= tree.value:
            branch = tree.tb
        else:
            branch = tree.fb
    else:
        if v == tree.value:
            branch = tree.tb
        else:
            branch = tree.fb
    return classify(observation, branch)


def prune(tree, mingain):
    if tree.tb.results == None:
        prune(tree.tb, mingain)
    if tree.fb.results == None:
        prune(tree.fb, mingain)

    if tree.tb.results != None and tree.fb.results != None:
        tb, fb = [], []
        for v,c in tree.tb.results.items():
            tb += [[v]]*c
        for v,c in tree.fb.results.items():
            fb += [[v]]*c
        delta = entropy(tb+fb) - (entropy(tb)+entropy(fb))/2
        if delta < mingain:
            tree.tb, tree.fb = None, None
            tree.results = uniquecounts(tb+fb)


def prune2(tree, mincount):
    if tree.tb.results == None:
        prune2(tree.tb, mincount)
    if tree.fb.results == None:
        prune2(tree.fb, mincount)

    if tree.tb.results != None and tree.fb.results != None:
        cnt = sum(tree.tb.results.values()) + sum(tree.fb.results.values())
        if float(cnt)/total < mincount:
            tb, fb = [], []
            for v,c in tree.tb.results.items():
                tb += [[v]]*c
            for v,c in tree.fb.results.items():
                fb += [[v]]*c
            tree.tb, tree.fb = None, None
            tree.results = uniquecounts(tb+fb)


'''

if __name__ == '__main__':
    my_data = [line.rstrip().split('\t') for line in open('data/pay_cleaned.log')]
    total = len(my_data)
    tree = buildtree(my_data)
    prune(tree, .05)
    prune2(tree, .05)
    printtree(tree)
    drawtree(tree, 'treeview.png')

    sys.exit(0)
    printtree(tree)

    prune(tree, 1.)
    printtree(tree)


'''
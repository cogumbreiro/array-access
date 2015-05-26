from sklearn.feature_extraction import DictVectorizer

def next_index(data, offset=0):
    start = data.index("[", offset)
    if start == -1:
        return ValueError("Could not find start token: [")
    end = data.index("]", start)
    if end == -1:
        return ValueError("Could not find end token: ]")
    next_start = data.index("[", start)
    if next_start != -1 and next_start > end:
        return next_index(data, next_start)
    return (start + 1, end)

DIMS=3

def next_access(data, offset=0, count=DIMS):
    result = []
    for _ in range(count):
        idx1, idx2 = next_index(data, offset)
        result.append((idx1, idx2))
        offset = idx2
    return result

import arith

def parse_index(data):
    
    return {
        "$1": int("i" in data),
        "$2": int("j" in data),
        "$3": int("k" in data)}

def parse_access(data):
    result = {}
    index = 0
    for (x,y) in next_access(data):
        # flatten the dictionary, so that DictVectorizer can handle it
        for (k,v) in parse_index(data[x:y]).iteritems():
            result[str(index) + ":" + k] = v
        index += 1
    return result

def parse(lines):
    for data in lines:
        try:
            yield repr(parse_access(data))
        except ValueError:
            pass

from sklearn.feature_extraction.text import CountVectorizer

def main2(data):
    vec = CountVectorizer()
    parsed = list(parse(data))
    matrix = vec.fit_transform(parsed)
    return vec, matrix

def main(data):
    vec = DictVectorizer()
    parsed = list(parse(data))
    matrix = vec.fit_transform(parsed)
    return vec, matrix

from sklearn.cluster import KMeans

def show_graph(data,k):
    from matplotlib import pyplot
    import numpy as np
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(data)

    labels = kmeans.labels_
    centroids = kmeans.cluster_centers_

    for i in range(k):
        # select only data observations with cluster label == i
        ds = data #[np.where(labels==i)]
        # plot the data observations
        pyplot.plot(ds[:,0],ds[:,1],'o')
        # plot the centroids
        lines = pyplot.plot(centroids[i,0],centroids[i,1],'kx')
        # make the centroid x's bigger
        pyplot.setp(lines,ms=15.0)
        pyplot.setp(lines,mew=2.0)
    pyplot.show()


if __name__ == '__main__':
    import sys
    fp1 = open(sys.argv[1])
    vec1, matrix1 = main2(fp1.readlines())
    fp1.close()
    print matrix1.shape
    #km = KMeans(n_clusters=9)
    #km.fit(vec1)
    #print(matrix1.toarray())
    #print(type(matrix1))
    #show_graph(matrix1.toarray(), 9)
    #print(km.labels_, km.cluster_centers_)
    #fp2 = open(sys.argv[2])
    #vec2, matrix2 = main(fp2.readlines())
    #fp2.close()

    #print(matrix1, matrix2)

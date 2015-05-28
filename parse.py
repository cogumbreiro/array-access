from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cluster import KMeans

import json
import math

DIMS=3

def atom_tovec(expr):
    """
    >>> atom_tovec({'level': 0, 'type': 'atom', 'has_var': False, 'coef': 1})
    (1, 0)
    >>> atom_tovec({'level': 2, 'type': 'atom', 'has_var': True, 'coef': 2})
    (2, 1)
    >>> atom_tovec({"level": 1, "type": "atom", "has_var": False, "coef": 5})
    (5, 0)
    """
    lvl = expr['level']
    has_var = int(expr['has_var'])
    coef = expr['coef']
    return (coef, has_var)

def expr_tovec(expr):
    """
    >>> expr_tovec({"type": "expr", "atoms": [{"level": 1, "type": "atom", "has_var": False, "coef": 5}]})
    (0, 0, 5, 0, 0, 0, 0, 0)
    """
    atoms = {}
    for atom in expr['atoms']:
        atoms[atom['level']] = atom_tovec(atom)
        
    result = []
    for idx in range(DIMS + 1):
        try:
            result.extend(atoms[idx])
        except KeyError:
            result.extend((0, 0))
    return tuple(result)

def main(fp):
    vec = DictVectorizer()
    parsed = list(repr(x) for x in json.load(fp))
    print parsed[0]
    matrix = vec.fit_transform(parsed)
    return vec, matrix

def main2(data):
    vec = CountVectorizer()
    parsed = list(parse(data))
    matrix = vec.fit_transform(parsed)
    return vec, matrix



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


if __name__ == "__main__":
oh    import doctest
    doctest.testmod()
    
if __name__ == '__main__':
    pass
    import sys
    with open(sys.argv[1]) as fp:
        show_graph(json.load(fp), 5)
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

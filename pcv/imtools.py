import os
from PIL import Image
from pylab import *


def get_imlist(path):
    return [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.jpg')]

def imresize(im, sz):
    pil_im = Image.fromarray(uint8(im))
    return array(pil_im.resize(sz))

def histeq(im, nbr_bins=256):
    imhist, bins = histogram(im.flatten(), nbr_bins, normed=True)
    cdf = imhist.cumsum()
    cdf = 255 * cdf / cdf[-1]

    im2 = interp(im.flatten(), bins[:-1], cdf)
    return im2.reshape(im.shape), cdf

def histeq2(im):
    dim = im.shape
    hist = [0]*256
    im = im.flatten()
    for level in im:
        hist[level] += 1

    cdf = hist
    for i in range(1, len(hist)):
        cdf[i] += cdf[i-1]

    cdf_min = None
    h = cdf
    for v, cdfv in enumerate(cdf):
        if cdfv == 0:
            continue
        if cdf_min is None:
            cdf_min = cdfv
        h[v] = round(255. * (cdfv - cdf_min) / (cdf[-1] - cdf_min))

    for i, v in enumerate(im):
        im[i] = h[v]
    return im.reshape(dim)


def showim(im):
    img = Image.fromarray(im)
    img.show()
    return img


def compute_average(imlist):
    averageim = array(Image.open(imlist[0]), 'f')

    for imname in imlist[1:]:
        try:
            averageim += array(Image.open(imname))
        except:
            print imname + '...skipped'
    averageim /= len(imlist)
    return array(averageim, 'uint8')


def pca(X):
    num_data, dim = X.shape
    mean_X = X.mean(axis=0)
    X = X - mean_X

    if dim > num_data:
        M = dot(X, X.T)
        e, EV = linalg.eigh(M)
        tmp = dot(X.T, EV).T
        V = tmp[::-1]
        S = sqrt(e)[::-1]
        for i in range(V.shape[1]):
            V[:,i] /= S
    else:
        U,S,V = linalg.svd(X)
        v = V[:num_data]

    return V,S,mean_X

"""Find label boxes (the book's pale-cyan / yellow callouts) on a page rendered at 200 dpi.

Prints (color, x0, y0, x1, y1) per box. It MISSES some boxes — always eyeball the
-q image occlude.py produces and add missed boxes to the spec by hand.
Usage: .tools/.venv/bin/python .tools/detect.py .tools/cache/Anatomy-002.png
"""
import sys, numpy as np
from PIL import Image
from scipy import ndimage as nd
def boxes(path, y0=0, y1=None):
    a=np.asarray(Image.open(path).convert('RGB')).astype(int)
    R,G,B=a[...,0],a[...,1],a[...,2]
    cyan=(R>185)&(R<230)&(G>235)&(B>240)
    yellow=(R>240)&(G>225)&(B<170)
    out=[]
    for kind,m in (('cyan',cyan),('yellow',yellow)):
        m=nd.binary_closing(m,structure=np.ones((9,9)))
        lab,n=nd.label(m)
        for sl in nd.find_objects(lab):
            ys,xs=sl; h=ys.stop-ys.start; w=xs.stop-xs.start
            if 30<h<200 and w>60 and w<900 and (m[sl].mean()>0.6):
                if ys.start>=y0 and (y1 is None or ys.stop<=y1):
                    out.append((kind,xs.start,ys.start,xs.stop,ys.stop))
    return out
if __name__=='__main__':
    for b in boxes(sys.argv[1]): print(b)

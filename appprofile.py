#!flask/bin/python
import numpy as np
from werkzeug.contrib.profiler import ProfilerMiddleware
import app as appl


def profile():
    app = appl.main()

    app.config['PROFILE'] = True
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[80])
    app.run(debug=True)


def test():
    from ncls import NCLS

    import pyranges as pr
    from pyranges import PyRanges
    import pybedtools

    """

    starts = np.array([10, 20, 40, 50])
    ends = np.array([x + 12 for x in starts])
    ids = ends

    ncls = NCLS(starts, ends, ids)

    it = ncls.find_overlap(0, 100)
    for i in it:
        print(i)
    print(ncls)
    pr.PyRanges(np.array([(10 + x, 22 + x, "as") for x in range(5)]))
    print(pr)
    #print(gr.overlap(gr2))
    """
    a = pybedtools.example_bedtool('a.bed')
    b = pybedtools.example_bedtool('b.bed')
    a_and_b = a.intersect(b)
    features = a[1:3]
    print(features)
    print(a)
    print(b)
    print(a_and_b)


if __name__ == "__main__":
    profile()
    #test()

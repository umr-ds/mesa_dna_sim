import json
import numpy as np
from scipy.interpolate import interp1d, PchipInterpolator

"""
Json-Input should look like this:
{       
        data: dataset.data,
        interpolation: dataset.cubicInterpolationMode === "monotone",
        maxX: maximumX, // not enforced every time since e.g. Homopolymers > 20 might be allowed  
                        // but GC-Content > 100% does not make sense
        maxY: maximumY,
        xRound: xRoundingFactor,
        yRound: yRoundingFactor
}
"""


def remove_duplicates(data, x_round):
    """

    :param data:
    :param x_round:
    :return:
    """
    res = []
    x_set = set()
    for elem in data:
        x_val = elem["x"]
        if round(x_val, x_round) not in x_set:
            res.append(elem)
            x_set.add(x_val)
    return res


def create_error_prob_function(error_prob_dict):
    """

    :param error_prob_dict:
    :return:
    """
    if error_prob_dict is None:
        return None
    if type(error_prob_dict) is str:
        error_prob_dict = json.loads(error_prob_dict)

    use_interpolation = error_prob_dict["interpolation"]
    max_x = error_prob_dict["maxX"]
    max_y = error_prob_dict["maxY"]
    x_round = error_prob_dict["xRound"]
    y_round = error_prob_dict["yRound"]
    data = remove_duplicates(error_prob_dict["data"], x_round)

    x_list = np.asarray([round(elem["x"], x_round) for elem in data], dtype=np.float32)
    y_list = np.asarray([round(elem["y"], y_round) for elem in data], dtype=np.float32)
    if use_interpolation:
        f = PchipInterpolator(x_list, y_list)  # "Real" Cubic interpolation: interp1d(x_list, y_list, kind='cubic')
    else:
        f = interp1d(x_list, y_list)

    def func(x):
        if x < 0.0:
            x = 0
        elif x > x_list[-1]:
            x = x_list[-1]

        res = f(x).item(0)
        if res < 0.0:
            res = 0.0
        elif res > max_y:
            res = max_y
        return 1.0 * res / 100.0

    return func


def create_interpolant(xs, ys):
    length = len(xs)
    if length != len(ys):
        raise Exception('Need an equal count of xs and ys.')
    if length == 0:
        def function(x):
            return 0
        return function
    if length == 1:
        result = +ys[0]

        def function(x):
            return result
        return function

    # sort xs
    indexes = []
    for i in range(0, length):
        indexes.append(i)
    # Traverse through all array elements
    for i in range(len(indexes)):
        min_idx = i
        for j in range(i + 1, len(indexes)):
            if xs[min_idx] > xs[j]:
                min_idx = j
        indexes[i], indexes[min_idx] = indexes[min_idx], indexes[i]
    old_xs = xs
    old_ys = ys
    xs = []
    ys = []
    for i in range(0, length):
        xs.append(+old_xs[indexes[i]])
        ys.append(+old_ys[indexes[i]])

    # consecutive differences and slopes
    dys = []
    dxs = []
    ms = []
    for i in range(0, length - 1):
        dx = xs[i+1] - xs[i]
        dy = ys[i+1] - ys[i]
        dxs.append(dx)
        dys.append(dy)
        ms.append(dy/dx)

    # deg -1 coefficients
    c1s = [ms[0]]
    for i in range(0, len(dxs) - 1):
        m = ms[i]
        m_next = ms[i+1]
        if m * m_next <= 0:
            c1s.append(0)
        else:
            dx_ = dxs[i]
            dxNext = dxs[i+1]
            common = dx_ + dxNext
            c1s.append(3*common/((common + dxNext)/m + (common + dx_)/m_next))
    c1s.append(ms[len(ms) - 1])

    # deg -2/-3 coefficients
    c2s = []
    c3s = []
    for i in range(0, len(c1s) - 1):
        c1 = c1s[i]
        m_ = ms[i]
        inv_dx = 1/dxs[i]
        common_ = c1 + c1s[i+1] - m_ - m_
        c2s.append((m_ - c1 - common_) * inv_dx)
        c3s.append(common_ * inv_dx * inv_dx)

    # return interpolant function
    def function(x):
        i = len(xs) - 1
        if x == xs[i]:
            return ys[i]
        low = 0
        high = len(c3s) - 1
        while low <= high:
            mid = int(np.floor(0.5 * (low + high)))
            x_here = xs[mid]
            if x_here < x:
                low = mid + 1
            elif x_here > x:
                high = mid - 1
            else:
                return ys[mid]

        i = max(0, high)
        diff = x - xs[i]
        diff_sq = diff * diff
        return ys[i] + c1s[i] * diff + c2s[i] * diff_sq + c3s[i] * diff * diff_sq
    return function


if __name__ == "__main__":
    inter = create_interpolant([0, 40, 60, 100], [100, 0, 0, 100])
    test = inter(20)
    txt = """{"data":[{"x":0,"y":0},{"x":2,"y":0},{"x":4,"y":20},{"x":5,"y":50},{"x":6,"y":80},{"x":7,"y":100},
    {"x":20,"y":100}],"interpolation":false,"maxX":20,"maxY":100,"xRound":0,"yRound":2}"""
    inter_fun = create_error_prob_function(txt)
    print([{a: inter_fun(a)} for a in range(100)])
    print([{a: inter_fun(a)} for a in range(-10, 20)])

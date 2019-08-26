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


if __name__ == "__main__":
    txt = """{"data":[{"x":0,"y":0},{"x":2,"y":0},{"x":4,"y":20},{"x":5,"y":50},{"x":6,"y":80},{"x":7,"y":100},
    {"x":20,"y":100}],"interpolation":false,"maxX":20,"maxY":100,"xRound":0,"yRound":2}"""
    inter_fun = create_error_prob_function(txt)
    print([{a: inter_fun(a)} for a in range(100)])
    print([{a: inter_fun(a)} for a in range(-10, 20)])

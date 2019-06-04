from flask import jsonify, request, Blueprint
from math import floor
from intervaltree import IntervalTree

from api.apikey import require_apikey
from simulators.error_probability import create_error_prob_function
from simulators.synthesis.gc_content import overall_gc_content, windowed_gc_content
from simulators.synthesis.homopolymers import homopolymer
from simulators.synthesis.kmer import kmer_counting
from simulators.synthesis.undesired_subsequences import undesired_subsequences

simulator_api = Blueprint("simulator_api", __name__, template_folder="templates")


@simulator_api.route('/api/homopolymer', methods=['GET', 'POST'])
@require_apikey
def do_homopolymer():
    if request.method == 'POST':
        sequence = request.json.get('sequence')
        error_prob_func = create_error_prob_function(request.json.get('error_prob'))
        as_html = request.json.get('asHTML')
    else:
        sequence = request.args.get('sequence')
        error_prob_func = create_error_prob_function(request.args.get('error_prob'))
        as_html = request.args.get('asHTML')
    res = homopolymer(sequence, error_function=error_prob_func)
    if as_html:
        return htmlify(res, sequence)
    return jsonify(res)


@simulator_api.route('/api/gccontent', methods=['GET', 'POST'])
@require_apikey
def do_gccontent():
    if request.method == 'POST':
        sequence = request.json.get('sequence')
        window = request.json.get('gc_windowsize')
        error_prob_func = create_error_prob_function(request.json.get('error_prob'))
        as_html = request.json.get('asHTML')
    else:
        sequence = request.args.get('sequence')
        window = request.args.get('gc_windowsize')
        error_prob_func = create_error_prob_function(request.args.get('error_prob'))
        as_html = request.args.get('asHTML')
    if window:
        try:
            res = windowed_gc_content(sequence, int(window), error_function=error_prob_func)
        except:
            res = overall_gc_content(sequence, error_function=error_prob_func)
    else:
        res = overall_gc_content(sequence, error_function=error_prob_func)
    if as_html:
        return htmlify(res, sequence)
    return jsonify(res)


@simulator_api.route('/api/kmer', methods=['GET', 'POST'])
@require_apikey
def do_kmer():
    if request.method == 'POST':
        sequence = request.json.get('sequence')
        window = request.json.get('kmer_windowsize')
        as_html = request.json.get('asHTML')
    else:
        sequence = request.args.get('sequence')
        window = request.args.get('kmer_windowsize')
        as_html = request.args.get('asHTML')
    if window:
        try:
            res = kmer_counting(sequence, int(window))
        except:
            res = kmer_counting(sequence)
    else:
        res = kmer_counting(sequence)
    if as_html:
        return htmlify(res, sequence)
    return jsonify(res)


@simulator_api.route('/api/subsequences', methods=['GET', 'POST'])
# @require_apikey
def do_undesired_sequences():
    if request.method == 'POST':
        sequence = request.json.get('sequence')
        enabled_undesired_seqs = request.json.get('enabledUndesiredSeqs')
        as_html = request.json.get('asHTML')
    else:
        sequence = request.args.get('sequence')
        enabled_undesired_seqs = request.args.get('enabledUndesiredSeqs')
        as_html = request.args.get('asHTML')
    if enabled_undesired_seqs:
        try:
            undesired_sequences = {}
            for useq in enabled_undesired_seqs:
                if useq['enabled']:
                    undesired_sequences[useq['sequence']] = float(useq['error_prob'])
            res = undesired_subsequences(sequence, undesired_sequences)
        except:
            res = undesired_subsequences(sequence)
    else:
        res = undesired_subsequences(sequence)
    if as_html:
        return htmlify(res, sequence)
    return jsonify(res)


@simulator_api.route('/api/all', methods=['GET', 'POST'])
@require_apikey
def do_all():
    # TODO
    if request.method == 'POST':
        sequence = request.json.get('sequence')
        kmer_window = request.json.get('kmer_windowsize')
        gc_window = request.json.get('gc_windowsize')
        enabled_undesired_seqs = request.json.get('enabledUndesiredSeqs')
        error_prob_func = create_error_prob_function(request.json.get('error_prob'))
        as_html = request.json.get('asHTML')
    else:
        sequence = request.args.get('sequence')
        kmer_window = request.args.get('kmer_windowsize')
        gc_window = request.args.get('gc_windowsize')
        enabled_undesired_seqs = request.args.get('undesired_seqs')
        error_prob_func = create_error_prob_function(request.args.get('error_prob'))
        as_html = request.args.get('asHTML')

    if enabled_undesired_seqs:
        try:
            undesired_sequences = {}
            for useq in enabled_undesired_seqs:
                if useq['enabled']:
                    undesired_sequences[useq['sequence']] = float(useq['error_prob'])
            res = undesired_subsequences(sequence, undesired_sequences)
        except:
            res = undesired_subsequences(sequence)
    else:
        res = undesired_subsequences(sequence)
    if kmer_window:
        try:
            res.extend(kmer_counting(sequence, int(kmer_window)))
        except:
            res.extend(kmer_counting(sequence))
    else:
        res.extend(kmer_counting(sequence))
    if gc_window:
        try:
            res.extend(windowed_gc_content(sequence, int(gc_window), error_function=error_prob_func))
        except:
            res.extend(overall_gc_content(sequence, error_function=error_prob_func))
    else:
        res.extend(overall_gc_content(sequence, error_function=error_prob_func))

    res.extend(homopolymer(sequence, error_function=error_prob_func))  # TODO use different error_prob_func!!!
    if as_html:
        return htmlify(res, sequence)
    return jsonify(res)


def htmlify(input, sequence):
    resmapping = {}  # map of length | sequence | with keys [0 .. |sequence|] and value = set(error[kmer])
    error_prob = {}
    error_no = 0
    t = IntervalTree()
    for elem in input:
        t.addi(elem["startpos"], elem["endpos"] + 1,
               [{'identifier': elem.get('identifier'), 'errorprob': elem.get('errorprob')}])
    t.addi(0, len(sequence), [{"identifier": "all", "errorprob": 0.0}])
    t.split_overlaps()
    # print(t.merge_overlaps(data_reducer=lambda x, y: x + " " + y))
    t.merge_equals(data_reducer=lambda x, y: x + y)
    return build_html(sorted(t), sequence)


def build_html(interval_tree, sequence):
    res = ""
    for interval in interval_tree:
        error_prob = min(1.0, sum([x["errorprob"] for x in interval[2]]))
        if sequence[interval[0]:interval[1]] != "":
            if error_prob <= 0.000000001:
                res += "<span>" + str(sequence[interval[0]:interval[1]]) + "</span>"
            else:
                res += "<span class=\"group_" + " group_".join(
                    [str(x.get('identifier')) for x in interval[2] if str(x.get('identifier')) != "all"]) + \
                       "\" title=\"Error Probability: " + str(round(error_prob * 100, 2)) + \
                       "%\" style=\"background-color: " + colorize(error_prob) + \
                       "; color: gray; font-weight: normal;\">" + sequence[interval[0]:interval[1]] + "</span>"
    return res


def htmlify_old(input, sequence, type):
    resmapping = {}  # map of length | sequence | with keys [0 .. |sequence|] and value = set(error[kmer])
    error_prob = {}
    error_no = 0
    for error in input:
        for pos in range(error["startpos"], error["endpos"] + 1):
            if pos not in resmapping:
                resmapping[pos] = set()
                error_prob[pos] = 0
            if "kmer" in error:
                resmapping[pos].add(error["kmer"])
            else:
                resmapping[pos].add(error_no)
            error_prob[pos] += error["errorprob"]
        error_no += 1

    res = ""
    for seq_pos in range(len(sequence)):
        if seq_pos in resmapping:
            curr_err_prob = round(min(100, error_prob[seq_pos] * 100), 2)
            res += "<span class=\"group_" + type + "_" + (" group_" + type + "_").join(
                [str(x) for x in resmapping[seq_pos]]) + \
                   "\" title=\"Error Probability: " + str(curr_err_prob) + \
                   "%\" style=\"background-color: " + colorize(curr_err_prob / 100) + \
                   "; color: gray; font-weight: normal;\">" + str(sequence[seq_pos]) + "</span>"
        else:
            res += str(sequence[seq_pos])
    return res


def colorize(error_prob):
    percent_colors = [{"pct": 0.0, "color": {"r": 0x00, "g": 0xff, "b": 0}},
                      {"pct": 0.5, "color": {"r": 0xff, "g": 0xff, "b": 0}},
                      {"pct": 1.0, "color": {"r": 0xff, "g": 0x00, "b": 0}}]
    i = 0
    for x in range(len(percent_colors)):
        i = x
        if error_prob < percent_colors[x]["pct"]:
            break

    lower = percent_colors[i - 1]
    upper = percent_colors[i]
    x_range = upper["pct"] - lower["pct"]
    range_pct = (error_prob - lower["pct"]) / x_range
    pct_lower = 1.0 - range_pct
    pct_upper = range_pct
    color = {
        "r": str(floor(max(min(255, lower["color"]["r"] * pct_lower + upper["color"]["r"] * pct_upper), 0))),
        "g": str(floor(max(min(255, lower["color"]["g"] * pct_lower + upper["color"]["g"] * pct_upper), 0))),
        "b": str(floor(max(min(255, lower["color"]["b"] * pct_lower + upper["color"]["b"] * pct_upper), 0)))
    }
    return 'rgb(' + color["r"] + "," + color["g"] + "," + color["b"] + ')'

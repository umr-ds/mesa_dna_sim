import json
import uuid
import redis
from flask import jsonify, request, Blueprint, flash
from math import floor
from copy import deepcopy
from api.RedisStorage import save_to_redis, read_from_redis
from api.apikey import require_apikey
from database.models import SequencingErrorRates, SynthesisErrorRates
from simulators.error_probability import create_error_prob_function
from simulators.error_sources.gc_content import overall_gc_content, windowed_gc_content
from simulators.error_sources.homopolymers import homopolymer
from simulators.error_sources.kmer import kmer_counting
from simulators.error_sources.undesired_subsequences import undesired_subsequences
from simulators.sequencing.sequencing_error import err_rates, mutation_attributes, SequencingError
from simulators.error_graph import Graph

simulator_api = Blueprint("simulator_api", __name__, template_folder="templates")


@simulator_api.route('/api/homopolymer', methods=['GET', 'POST'])
@require_apikey
def do_homopolymer():
    if request.method == 'POST':
        r_method = request.json
    else:
        r_method = request.args

    sequence = r_method.get('sequence')
    error_prob_func = create_error_prob_function(r_method.get('homopolymer_error_prob'))
    as_html = r_method.get('asHTML')
    res = homopolymer(sequence, error_function=error_prob_func)
    if as_html:
        return htmlify(res, sequence)
    return jsonify(res)


@simulator_api.route('/api/gccontent', methods=['GET', 'POST'])
@require_apikey
def do_gccontent():
    if request.method == 'POST':
        r_method = request.json
    else:
        r_method = request.args

    sequence = r_method.get('sequence')
    window = r_method.get('gc_windowsize')
    error_prob_func = create_error_prob_function(r_method.get('gc_error_prob'))
    as_html = r_method.get('asHTML')
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
        r_method = request.json
    else:
        r_method = request.args

    sequence = r_method.get('sequence')
    window = r_method.get('kmer_windowsize')
    error_prob_func = create_error_prob_function(r_method.get('kmer_error_prob'))
    as_html = r_method.get('asHTML')
    if window:
        try:
            res = kmer_counting(sequence, int(window), error_prob_func)
        except:
            res = kmer_counting(sequence, error_function=error_prob_func)
    else:
        res = kmer_counting(sequence, error_function=error_prob_func)
    if as_html:
        return htmlify(res, sequence)
    return jsonify(res)


@simulator_api.route('/api/subsequences', methods=['GET', 'POST'])
@require_apikey
def do_undesired_sequences():
    if request.method == 'POST':
        r_method = request.json
    else:
        r_method = request.args
    sequence = r_method.get('sequence')
    enabled_undesired_seqs = r_method.get('enabledUndesiredSeqs')
    as_html = r_method.get('asHTML')

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


@simulator_api.route('/api/sequencing', methods=['GET', 'POST'])
@require_apikey
def add_sequencing_errors():
    if request.method == 'POST':
        r_method = request.json
    else:
        r_method = request.args

    sequence = r_method.get('sequence')
    seq_meth = r_method.get('sequence_method')

    # 0 = none, 7,8,9 = user defined
    if seq_meth in {"0", "7", "8", "9"}:
        res = sequence
    else:
        err_rate = SequencingErrorRates.query.filter(
            SequencingErrorRates.submethod_id == int(seq_meth)).first().err_data
        err_att = SequencingErrorAttributes.query.filter(
            SequencingErrorAttributes.submethod_id == int(seq_meth)).first().attributes
        seqerr = SequencingError(sequence, err_att, err_rate)
        res = seqerr.lit_error_rate_mutations()
    return jsonify(res)


# undesired_sub_seq = UndesiredSubsequences.query.filter(
#    or_(UndesiredSubsequences.owner_id == user_id, UndesiredSubsequences.validated == True)).order_by(
#    desc(UndesiredSubsequences.id)).all()


@simulator_api.route('/api/synthesis', methods=['GET', 'POST'])
@require_apikey
def add_synthesis_errors():
    if request.method == 'POST':
        r_method = request.json
    else:
        r_method = request.args

    sequence = r_method.get('sequence')
    synth_meth = r_method.get('synthesis_method')

    # 0 = none, 11,12,13 = user defined
    if synth_meth in {"0", "11", "12", "13"}:
        res = sequence
    else:
        tmp = SynthesisErrorRates.query.filter(
            SynthesisErrorRates.id == int(synth_meth)).first()
        err_rate = tmp.err_data
        err_att = tmp.err_attributes
        seqerr = SequencingError(sequence, err_att, err_rate)
        res = seqerr.lit_error_rate_mutations()
    return jsonify(res)


# This is dumb as it does calculate the errors new and therefore gets different errors
# Than the sequencing and synthesis by them self
@simulator_api.route('/api/modify', methods=['GET', 'POST'])
@require_apikey
def add_errors():
    if request.method == 'POST':
        r_method = request.json
    else:
        r_method = request.args

    sequence = r_method.get('sequence')
    seq_meth = r_method.get('sequence_method')
    synth_meth = r_method.get('synthesis_method')

    g = Graph(None, sequence)

    if synth_meth in {"0", "11", "12", "13"} and seq_meth in {"0", "7", "8", "9"}:
        pass
    elif synth_meth in {"0", "11", "12", "13"}:
        sequencing_error(sequence, g, seq_meth, process="sequencing")
    elif seq_meth in {"0", "7", "8", "9"}:
        synthesis_error(sequence, g, synth_meth, process="synthesis")
    else:
        synthesis_error(sequence, g, synth_meth, process="synthesis")
        synthesis_error_seq = g.graph.nodes[0]['seq']
        sequencing_error(synthesis_error_seq, g, seq_meth, process="sequencing")
    return jsonify(g.graph.nodes[0]['seq'])


@simulator_api.route('/api/all', methods=['GET', 'POST'])
@require_apikey
def do_all():
    # TODO
    if request.method == 'POST':
        r_method = request.json
    else:
        r_method = request.args
    r_uid = r_method.get('uuid')
    if r_uid is not None:
        r_res = read_from_redis(r_uid)
        if r_res is not None:
            return jsonify(json.loads(r_res))
        else:
            return jsonify({'did_succeed': False})
    sequence = r_method.get('sequence')
    kmer_window = r_method.get('kmer_windowsize')
    gc_window = r_method.get('gc_windowsize')
    enabled_undesired_seqs = r_method.get('enabledUndesiredSeqs')
    seq_meth = r_method.get('sequence_method')
    synth_meth = r_method.get('synthesis_method')
    gc_error_prob_func = create_error_prob_function(r_method.get('gc_error_prob'))
    homopolymer_error_prob_func = create_error_prob_function(r_method.get('homopolymer_error_prob'))
    kmer_error_prob_func = create_error_prob_function(r_method.get('kmer_error_prob'))
    use_error_probs = r_method.get('use_error_probs')
    seed = r_method.get('random_seed')
    seed = int(seed) if seed else None
    as_html = r_method.get('asHTML')
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
    usubseq_html = htmlify(res, sequence)
    if kmer_window:
        try:
            kmer_res = kmer_counting(sequence, int(kmer_window), error_function=kmer_error_prob_func)
        except:
            kmer_res = kmer_counting(sequence, error_function=kmer_error_prob_func)
    else:
        kmer_res = kmer_counting(sequence, error_function=kmer_error_prob_func)

    res.extend(kmer_res)
    if gc_window:
        try:
            gc_window_res = windowed_gc_content(sequence, int(gc_window), error_function=gc_error_prob_func)
        except:
            gc_window_res = overall_gc_content(sequence, error_function=gc_error_prob_func)
    else:
        gc_window_res = overall_gc_content(sequence, error_function=gc_error_prob_func)

    res.extend(gc_window_res)
    homopolymer_res = homopolymer(sequence, error_function=homopolymer_error_prob_func)
    res.extend(homopolymer_res)

    # The Graph for all types of errors
    g = Graph(None, sequence)
    # Another Graph to only show the sequencing errors, wasteful on resources and has to be done
    # again for storage
    # g_only_seq = Graph(None, sequence)

    if use_error_probs:
        manual_errors(sequence, g, [kmer_res, res, homopolymer_res, gc_window_res], seed=seed)
    else:
        seed = synthesis_error(sequence, g, synth_meth, process="synthesis", seed=seed)
        synthesis_error_seq = g.graph.nodes[0]['seq']
        # The code commented out is for visualization of sequencing and synthesis
        # methods seperated, it is inefficient - better to color the sequence
        # based on the final graph using the identifiers.
        # dc_g = deepcopy(g)
        # synth_html = htmlify(dc_g.get_lineages(), synthesis_error_seq, modification=True)
        sequencing_error(synthesis_error_seq, g, seq_meth, process="sequencing", seed=seed)
        # sequencing_error(synthesis_error_seq, g_only_seq, seq_meth, process="sequencing", seed=seed)
        # sequencing_error_seq = g_only_seq.graph.nodes[0]['seq']
        # seq_html = htmlify(g_only_seq.get_lineages(), sequencing_error_seq, modification=True)

    mod_seq = g.graph.nodes[0]['seq']
    mod_res = g.get_lineages()

    if as_html:
        kmer_html = htmlify(kmer_res, sequence)
        gc_html = htmlify(gc_window_res, sequence)
        homopolymer_html = htmlify(homopolymer_res, sequence)
        mod_html = htmlify(mod_res, mod_seq, modification=True)
        uuid_str = str(uuid.uuid4())
        res = jsonify(
            {'res': {'modify': mod_html, 'sequencing': "seq_html_placeholder", 'synthesis': "synth_html_placeholder", 'subsequences': usubseq_html,
                     'kmer': kmer_html, 'gccontent': gc_html, 'homopolymer': homopolymer_html,
                     'all': htmlify(res, sequence)}, 'uuid': uuid_str, 'sequence': sequence, 'seed': str(seed)})
        try:
            save_to_redis(uuid_str, json.dumps({'res': res.json['res'], 'query': r_method, 'uuid': uuid_str}), 31536000)
        except redis.exceptions.ConnectionError as ex:
            print('Could not connect to Redis-Server')
        return res

    return jsonify(res)


def synthesis_error(sequence, g, synth_meth, seed, process="synthesis"):
    tmp = SynthesisErrorRates.query.filter(
        SynthesisErrorRates.id == int(synth_meth)).first()
    err_rate_syn = tmp.err_data
    err_att_syn = tmp.err_attributes
    synth_err = SequencingError(sequence, g, process, err_att_syn, err_rate_syn, seed=seed)
    return synth_err.lit_error_rate_mutations()


def sequencing_error(sequence, g, seq_meth, seed, process="sequencing"):
    tmp = SequencingErrorRates.query.filter(
        SequencingErrorRates.id == int(seq_meth)).first()
    err_rate_seq = tmp.err_data
    err_att_seq = tmp.err_attributes
    seq_err = SequencingError(sequence, g, process, err_att_seq, err_rate_seq, seed=seed)
    return seq_err.lit_error_rate_mutations()


def manual_errors(sequence, g, error_res, seed, process='Calculated Error'):
    seq_err = SequencingError(sequence, g, process, seed=seed)
    for att in error_res:
        for err in att:
            seq_err.manual_mutation(err)


def htmlify(input, sequence, modification=False):
    resmapping = {}  # map of length | sequence | with keys [0 .. |sequence|] and value = set(error[kmer])
    error_prob = {}
    err_lin = {}
    # reduce the span-classes list in case we wont underline / highlight the error classes anyway:
    reducesets = len(input) > 800
    for error in input:
        for pos in range(error["startpos"], error["endpos"] + 1):
            if pos not in resmapping:
                resmapping[pos] = set()
                error_prob[pos] = 0
            if "kmer" in error:
                resmapping[pos].add(error['identifier'] + "_" + error["kmer"])
            else:
                resmapping[pos].add(error['identifier'])
            if modification:
                err_lin[pos] = error["errors"]
                # For the modifications the errorprobs are only for the identification of the process
                # in which they occured (sequencing, synthesis etc.) for the purpose of coloring, there
                # is therefore no need for additive errorprobs.
                error_prob[pos] = error["errorprob"]
            else:
                error_prob[pos] += error["errorprob"]

    res = []
    buildup = ""
    lineage = ""
    buildup_errorprob = -1.0
    buildup_resmap = []

    for seq_pos in range(len(sequence)):
        if seq_pos in resmapping:
            if modification:
                curr_err_prob = error_prob[seq_pos]
            else:
                curr_err_prob = round(min(100, error_prob[seq_pos] * 100), 2)

            if buildup_errorprob == curr_err_prob and buildup_resmap == resmapping[seq_pos]:
                # current base belongs to the same error classes as previous, just add it to our tmp string
                buildup += sequence[seq_pos]
            elif buildup_errorprob == -1.0 and buildup_resmap == []:
                # current base is the first base of a new error group
                # (either because prev base had no error class or we are at the start of our sequence)
                buildup += sequence[seq_pos]
                buildup = sequence[seq_pos]
                if modification:
                    lineage = err_lin[seq_pos]
                buildup_errorprob = curr_err_prob
                buildup_resmap = resmapping[seq_pos]
            else:
                # current base has a different error prob / error class than previous base, finish previous group
                res.append((buildup_resmap, buildup_errorprob, buildup, lineage))
                # and initialize current group with current base error classes
                buildup = sequence[seq_pos]
                buildup_errorprob = curr_err_prob
                buildup_resmap = resmapping[seq_pos]
        else:
            # current base does not have any error probability
            if buildup != "":
                # if previous base / group is still in our tmp group, write it out
                res.append((buildup_resmap, buildup_errorprob, buildup, lineage))
                # and reset tmp group
                buildup = ""
                lineage = ""
                buildup_errorprob = -1.0
                buildup_resmap = []
            # no need to write current base to tmp since it does not belong to any error group
            res.append(({}, 0.0, sequence[seq_pos], lineage))
            # res += str(sequence[seq_pos])
    # after the last base: if our tmp is still filled, write it out
    if buildup != "":
        res.append((buildup_resmap, buildup_errorprob, buildup, lineage))
    return build_html(res, reducesets)


def build_html(res_list, reducesets=True):
    res = ""
    cname_id = 0
    for elem in res_list:
        resmap, error_prob, seq, lineage = elem
        if not lineage:
            error_prob = min(100.0, error_prob)
        if seq != "":
            if error_prob <= 0.000000001:
                res += str(seq)
            else:
                if reducesets:
                    cname = 'red_' + str(cname_id)
                    cname_id += 1
                else:
                    cname = " g_".join([str(x) for x in resmap])
                if lineage == "":
                    res += "<span class=\"g_" + cname + "\" title=\"Error Probability: " + str(error_prob) + \
                           "%\" style=\"background-color: " + colorize(error_prob / 100) + ";\">" + str(seq) + "</span>"
                else:
                    res += "<span class=\"g_" + cname + "\" title=\"" + lineage + \
                           "\"style=\"background-color: " + colorize(error_prob) + ";\">" + str(seq) + "</span>"
    return res


def colorize(error_prob):
    percent_colors = [{"pct": 0.0, "color": {"r": 0x00, "g": 0xff, "b": 0, "a": 0.2}},
                      {"pct": 0.15, "color": {"r": 0x00, "g": 0xff, "b": 0, "a": 1.0}},
                      {"pct": 0.5, "color": {"r": 0xff, "g": 0xff, "b": 0, "a": 1.0}},
                      {"pct": 1.0, "color": {"r": 0xff, "g": 0x00, "b": 0, "a": 1.0}},
                      {"pct": 2.0, "color": {"r": 0xff, "g": 0x99, "b": 0xcc, "a": 1.0}},
                      {"pct": 2.3, "color": {"r": 0xff, "g": 0x00, "b": 0xff, "a": 1.0}},
                      {"pct": 2.6, "color": {"r": 0x80, "g": 0x00, "b": 0x80, "a": 1.0}},
                      {"pct": 2.9, "color": {"r": 0xcc, "g": 0x99, "b": 0xFF, "a": 1.0}},
                      {"pct": 3.0, "color": {"r": 0x99, "g": 0xcc, "b": 0xff, "a": 1.0}},
                      {"pct": 3.3, "color": {"r": 0x00, "g": 0xcc, "b": 0xff, "a": 1.0}},
                      {"pct": 3.6, "color": {"r": 0x00, "g": 0xff, "b": 0xff, "a": 1.0}},
                      {"pct": 3.9, "color": {"r": 0xcc, "g": 0x80, "b": 0x80, "a": 1.0}},
                      {"pct": 4.0, "color": {"r": 0xff, "g": 0xff, "b": 0x99, "a": 1.0}},
                      {"pct": 4.3, "color": {"r": 0x99, "g": 0xcc, "b": 0x00, "a": 1.0}},
                      {"pct": 4.6, "color": {"r": 0xff, "g": 0xff, "b": 0x00, "a": 1.0}},
                      {"pct": 4.9, "color": {"r": 0x80, "g": 0x80, "b": 0x00, "a": 0.5}}
                      ]
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
    return 'rgba(' + str(
        floor(max(min(255, lower["color"]["r"] * pct_lower + upper["color"]["r"] * pct_upper), 0))) + "," + str(
        floor(max(min(255, lower["color"]["g"] * pct_lower + upper["color"]["g"] * pct_upper), 0))) + "," + str(
        floor(max(min(255, lower["color"]["b"] * pct_lower + upper["color"]["b"] * pct_upper), 0))) + "," + str(
        round(max(min(1.0, lower["color"]["a"] * pct_lower + upper["color"]["a"] * pct_upper), 0.2), 4)) + ')'

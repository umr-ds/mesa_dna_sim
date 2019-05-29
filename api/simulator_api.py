from flask import jsonify, request, Blueprint

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
    else:
        sequence = request.args.get('sequence')
        error_prob_func = create_error_prob_function(request.args.get('error_prob'))
    res = homopolymer(sequence, error_function=error_prob_func)
    return jsonify(res)


@simulator_api.route('/api/gccontent', methods=['GET', 'POST'])
@require_apikey
def do_gccontent():
    if request.method == 'POST':
        sequence = request.json.get('sequence')
        window = request.json.get('gc_windowsize')
    else:
        sequence = request.args.get('sequence')
        window = request.args.get('gc_windowsize')
    if window:
        try:
            res = windowed_gc_content(sequence, int(window))
        except:
            res = overall_gc_content(sequence)
    else:
        res = overall_gc_content(sequence)
    return jsonify(res)


@simulator_api.route('/api/kmer', methods=['GET', 'POST'])
@require_apikey
def do_kmer():
    if request.method == 'POST':
        sequence = request.json.get('sequence')
        window = request.json.get('kmer_windowsize')
    else:
        sequence = request.args.get('sequence')
        window = request.args.get('kmer_windowsize')
    if window:
        try:
            res = kmer_counting(sequence, int(window))
        except:
            res = kmer_counting(sequence)
    else:
        res = kmer_counting(sequence)
    return jsonify(res)


@simulator_api.route('/api/subsequences', methods=['GET', 'POST'])
# @require_apikey
def do_undesired_sequences():
    if request.method == 'POST':
        sequence = request.json.get('sequence')
        enabled_undesired_seqs = request.json.get('enabledUndesiredSeqs')
    else:
        sequence = request.args.get('sequence')
        enabled_undesired_seqs = request.args.get('enabledUndesiredSeqs')

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
    return jsonify(res)


@simulator_api.route('/api/all', methods=['GET', 'POST'])
@require_apikey
def do_all():
    # TODO
    if request.method == 'POST':
        sequence = request.json.get('sequence')
        kmer_window = request.json.get('kmer_windowsize')
        gc_window = request.json.get('gc_window')
        enabled_undesired_seqs = request.json.get('enabledUndesiredSeqs')
    else:
        sequence = request.args.get('sequence')
        kmer_window = request.json.get('kmer_windowsize')
        gc_window = request.json.get('gc_window')
        enabled_undesired_seqs = request.args.get('undesired_seqs')

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
    return jsonify(res)

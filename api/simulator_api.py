from flask import jsonify, request, Blueprint

from api.apikey import require_apikey
from simulators.synthesis.gc_content import overall_gc_content, windowed_gc_content
from simulators.synthesis.homopolymers import homopolymer
from simulators.synthesis.kmer import kmer_counting
from simulators.synthesis.undesired_subsequences import undesired_subsequences

simulator_api = Blueprint("simulator_api", __name__, template_folder="templates")


@simulator_api.route('/api/homopolymer', methods=['GET', 'POST'])
@require_apikey
def do_homopolymer():
    if request.method == 'POST':
        sequence = request.form.get('sequence')
    else:
        sequence = request.args.get('sequence')
    res = homopolymer(sequence)
    return jsonify(res)


@simulator_api.route('/api/gccontent', methods=['GET', 'POST'])
@require_apikey
def do_gccontent():
    if request.method == 'POST':
        sequence = request.form.get('sequence')
        window = request.form.get('window')
    else:
        sequence = request.args.get('sequence')
        window = request.args.get('window')
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
        sequence = request.form.get('sequence')
        window = request.form.get('window')
    else:
        sequence = request.args.get('sequence')
        window = request.args.get('window')
    if window:
        try:
            res = kmer_counting(sequence, int(window))
        except:
            res = kmer_counting(sequence)
    else:
        res = kmer_counting(sequence)
    return jsonify(res)


@simulator_api.route('/api/subsequences', methods=['GET', 'POST'])
@require_apikey
def do_undesired_sequences():
    if request.method == 'POST':
        sequence = request.form.get('sequence')
        undesired_seqs = request.form.get('undesired_seqs')
    else:
        sequence = request.args.get('sequence')
        undesired_seqs = request.args.get('undesired_seqs')

    if undesired_seqs:
        try:
            undesired_sequences = {}
            for line in undesired_seqs.split(";"):
                seq, error_prob = line.split(" ")
                undesired_sequences[seq] = float(error_prob)
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
        sequence = request.form.get('sequence')
        window = request.args.get('window')
        undesired_seqs = request.form.get('undesired_seqs')
    else:
        sequence = request.args.get('sequence')
        window = request.args.get('window')
        undesired_seqs = request.args.get('undesired_seqs')

    if undesired_seqs:
        try:
            undesired_sequences = {}
            for line in undesired_seqs.split(";"):
                seq, error_prob = line.split(" ")
                undesired_sequences[seq] = float(error_prob)
            res = undesired_subsequences(sequence, undesired_sequences)
        except:
            res = undesired_subsequences(sequence)
    else:
        res = undesired_subsequences(sequence)
    return jsonify(res)

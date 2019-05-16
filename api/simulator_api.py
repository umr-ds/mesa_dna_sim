from flask import jsonify, request, Blueprint

from api.apikey import require_apikey
from simulators.synthesis.gc_content import overall_gc_content, windowed_gc_content
from simulators.synthesis.homopolymers import homopolymer
from simulators.synthesis.kmer import kmer_counting

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
    window = None
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
    window = None
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

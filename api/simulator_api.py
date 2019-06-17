from flask import jsonify, request, Blueprint

from api.apikey import require_apikey
from database.models import SequencingErrorRates, SequencingErrorAttributes, \
    SynthesisErrorRates, SynthesisErrorAttributes
from simulators.error_probability import create_error_prob_function
from simulators.error_sources.gc_content import overall_gc_content, windowed_gc_content
from simulators.error_sources.homopolymers import homopolymer
from simulators.error_sources.kmer import kmer_counting
from simulators.error_sources.undesired_subsequences import undesired_subsequences
from simulators.sequencing.sequencing_error import err_rates, mutation_attributes, SequencingError

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
        error_prob_func = create_error_prob_function(request.json.get('error_prob'))
    else:
        sequence = request.args.get('sequence')
        window = request.args.get('gc_windowsize')
        error_prob_func = create_error_prob_function(request.args.get('error_prob'))
    if window:
        try:
            res = windowed_gc_content(sequence, int(window), error_function=error_prob_func)
        except:
            res = overall_gc_content(sequence, error_function=error_prob_func)
    else:
        res = overall_gc_content(sequence, error_function=error_prob_func)
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


@simulator_api.route('/api/sequencing', methods=['GET', 'POST'])
# @require_apikey
def add_sequencing_errors():
    if request.method == 'POST':
        sequence = request.json.get('sequence')
        seq_meth = request.json.get('sequence_method')
    else:
        sequence = request.args.get('sequence')
        seq_meth = request.args.get('sequence_method')

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
# @require_apikey
def add_synthesis_errors():
    if request.method == 'POST':
        sequence = request.json.get('sequence')
        synth_meth = request.json.get('synthesis_method')
    else:
        sequence = request.args.get('sequence')
        synth_meth = request.args.get('synthesis_method')

    # 0 = none, 11,12,13 = user defined
    if synth_meth in {"0", "11", "12", "13"}:
        res = sequence
    else:
        err_rate = SynthesisErrorRates.query.filter(
            SynthesisErrorRates.id == int(synth_meth)).first().err_data
        err_att = SynthesisErrorAttributes.query.filter(
            SynthesisErrorAttributes.id == int(synth_meth)).first().err_data
        seqerr = SequencingError(sequence, err_att, err_rate)
        res = seqerr.lit_error_rate_mutations()
    return jsonify(res)


@simulator_api.route('/api/modify', methods=['GET', 'POST'])
# @require_apikey
def add_errors():
    if request.method == 'POST':
        sequence = request.json.get('sequence')
        synth_meth = request.json.get('synthesis_method')
        seq_meth = request.json.get('sequence_method')
    else:
        sequence = request.args.get('sequence')
        synth_meth = request.args.get('synthesis_method')
        seq_meth = request.args.get('sequence_method')

    if synth_meth in {"0", "11", "12", "13"} and seq_meth in {"0", "7", "8", "9"}:
        res = sequence
    elif synth_meth in {"0", "11", "12", "13"}:
        res = sequencing_error(seq_meth, sequence)
    elif seq_meth in {"0", "7", "8", "9"}:
        res = synthesis_error(synth_meth, sequence)
    else:
        synthesis_error_seq = synthesis_error(synth_meth, sequence)
        res = sequencing_error(seq_meth, synthesis_error_seq)
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
        seq_meth = request.json.get('sequence_method')
        synth_meth = request.json.get('synthesis_method')
    else:
        sequence = request.args.get('sequence')
        kmer_window = request.json.get('kmer_windowsize')
        gc_window = request.json.get('gc_window')
        enabled_undesired_seqs = request.args.get('undesired_seqs')
        seq_meth = request.args.get('sequence_method')
        synth_meth = request.json.get('synthesis_method')

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


# Helper
def synthesis_error(synth_meth, sequence):
    err_rate_syn = SynthesisErrorRates.query.filter(
        SynthesisErrorRates.id == int(synth_meth)).first().err_data
    err_att_syn = SynthesisErrorAttributes.query.filter(
        SynthesisErrorAttributes.id == int(synth_meth)).first().err_data
    synth_err = SequencingError(sequence, err_att_syn, err_rate_syn)
    return synth_err.lit_error_rate_mutations()


def sequencing_error(seq_meth, sequence):
    err_rate_seq = SequencingErrorRates.query.filter(
        SequencingErrorRates.submethod_id == int(seq_meth)).first().err_data
    err_att_seq = SequencingErrorAttributes.query.filter(
        SequencingErrorAttributes.submethod_id == int(seq_meth)).first().attributes

    seq_err = SequencingError(sequence, err_att_seq, err_rate_seq)
    return seq_err.lit_error_rate_mutations()

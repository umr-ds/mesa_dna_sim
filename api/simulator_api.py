import base64
import copy
import json
import math
import multiprocessing
import uuid
from threading import Thread
from multiprocessing.pool import ThreadPool
import os
import numpy as np

try:
    import RNAstructure

    rna_imported = True
except ModuleNotFoundError:
    rna_imported = False
import redis
from flask import jsonify, request, Blueprint, current_app, copy_current_request_context, make_response
from math import floor
from api.RedisStorage import save_to_redis, read_from_redis
from api.apikey import require_apikey
from database.models import SequencingErrorRates, SynthesisErrorRates, Apikey, User
from api.mail import send_mail
from simulators.error_probability import create_error_prob_function
from simulators.error_sources.gc_content import overall_gc_content, windowed_gc_content
from simulators.error_sources.homopolymers import homopolymer
from simulators.error_sources.kmer import kmer_counting
from simulators.error_sources.undesired_subsequences import undesired_subsequences
from simulators.sequencing.sequencing_error import SequencingError
from simulators.error_graph import Graph

simulator_api = Blueprint("simulator_api", __name__, template_folder="templates")


@simulator_api.route('/api/homopolymer', methods=['GET', 'POST'])
@require_apikey
def do_homopolymer():
    """
    Takes the parameters from an uploaded config file or the website and calculates error probabilities for every base
    of the sequence based on the occurrence of homopolymers. The error probabilities are either saved as html data or
    json file.
    :return: Jsonified homopolymer error probabilities.
    """
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
def do_gc_content():
    """
    Takes the parameters from an uploaded config file or the website and calculates error probabilities for every base
    of the sequence based on the gc content in the whole sequence and windows that are set up by the configuration. The
    error probabilities are either saved as html data or json file.
    :return: Jsonified gc_content error probabilities.
    """
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
    """
    Takes the parameters from an uploaded config file or the website and calculates error probabilities for every base
    of the sequence based on the occurrence of kmers in windows that are set up by the configuration. The error
    probabilities are either saved as html data or json file.
    :return: Jsonified kmer error probabilities.
    """
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
    """
    Takes the parameters from an uploaded config file or the website and if enabled, calculates error probabilities for
    every single base of the sequence based on the occurrence of undesired sequences that are set up by the
    configuration. The error probabilities are either saved as html data or json file.
    :return: Jsonified undersired_sequences error probabilities.
    """
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


@simulator_api.route('/api/fasta_all', methods=['GET', 'POST'])
@require_apikey
def fasta_do_all_wrapper():
    """
    This method wraps the do_multiple method (which works with multiline fasta files) to get the app context and allow
    the usage of mutliple threads to calculate the results faster. If a multiline fasta file is uploaded, the method
    gets a list with sequences and calls @do_all for every sequence in another thread. Every sequence gets a unique uuid
    to access the results and an e_mail with all uuids will be send to the user that uploaded the fasta file.
    :return:
    """

    @copy_current_request_context
    def do_multiple(lst, e_mail, host):
        with current_app.app_context():
            cores = 2
            p = multiprocessing.Pool(cores)
            res_lst = p.map(do_all, lst)
            p.close()
        urls = "Access your results at: "
        fastq_str_list = []
        for res in res_lst:
            uuid = list(res.json.values())[0]["uuid"]
            url = host + "query_sequence?uuid=" + uuid
            urls = urls + "\n" + url
            fastq_str_list.append(
                "@Your Mosla sequence at " + url + "\n" + list(res.json.values())[0]["sequence"] + "\n+\n" +
                list(res.json.values())[0]['res']['fastqOr'])
        fastq_text = "\n".join(fastq_str_list)
        send_mail("noreply@mosla.de", [e_mail], urls, subject="[MOSLA] Your DNA-Simulation finished",
                  attachment_txt=fastq_text, attachment_name="MOSLA.fastq")

    if request.method == 'POST':
        r_method = request.json
    else:
        r_method = request.args
    r_uid = r_method.get('uuid')
    if r_uid is not None:
        r_res = None
        try:
            r_res = read_from_redis(r_uid)
        except Exception as e:
            print("Error while talking to Redis-Server:", e)
        if r_res is not None:
            return jsonify(json.loads(r_res))
    # TODO estimate time needed
    apikey = Apikey.query.filter_by(apikey=r_method.get('key')).first()
    if apikey.owner_id == 0:
        return jsonify({'did_succeed': False})
    user = User.query.filter_by(user_id=apikey.owner_id).first()
    email = user.email
    sequence_list = r_method.get('sequence_list')
    del r_method['sequence_list']
    try:
        del r_method['uuid']
    except:
        pass
    tmp_lst = []
    for x in sequence_list:
        c_method = copy.deepcopy(r_method)
        c_method['sequence'] = x
        tmp_lst.append(c_method)
    thread = Thread(target=do_multiple, args=(tmp_lst, email, request.host_url))
    thread.start()
    return jsonify({"result_by_mail": True, "did_succeed": False})


@simulator_api.route('/api/max_expect', methods=['GET', 'POST'])
@require_apikey
def max_expect():
    if request.method == 'POST':
        r_method = request.json
    else:
        r_method = request.args
    sequence = r_method.get('sequence')
    return jsonify(
        create_max_expect(sequence, temperature=310.15, max_percent=10, gamma=1, max_structures=1,
                          window=3))


@simulator_api.route('/api/getIMG', methods=['GET'])
def get_max_expect_file():
    content_type = {".svg": "image/svg+xml", ".pdf": "application/pdf", ".ps": "application/postscript",
                    ".ct": "text/plain", ".dot": "text/plain", ".pfs": "application/octet-stream"}
    id = request.args.get('id')
    img_type = "." + request.args.get('type')
    if img_type not in content_type:
        return jsonify({"did_succeed": False})
    try:
        ret = json.loads(read_from_redis(id))
        if img_type in ret:
            response = make_response(base64.standard_b64decode(ret[img_type]))
            response.headers.set('Content-Type', content_type[img_type])
            response.headers.set(
                'Content-Disposition', 'attachment', filename=str(id) + img_type)
            return response
    except:
        pass
    return jsonify({"did_succeed": False}), 404


def create_max_expect(dna_str, basefilename=None, temperature=310.15, max_percent=10, gamma=1, max_structures=1,
                      window=3):
    if not rna_imported:
        return [basefilename, {
            'plain_dot': "Error: " + "RNAstructure not imported correctly. Secondary Structure calculation not supported."}]
    if len(dna_str) > 4000:
        return [basefilename, {'plain_dot': "Error: " + "Sequences longer than 4000 nt not supported"}]
    prev_wd = os.getcwd()
    os.chdir("/tmp")
    try:
        p = RNAstructure.RNA.fromString(dna_str, "dna")
    except RuntimeError as ru_e:
        return [basefilename, {'plain_dot': "Error: " + str(ru_e)}]
    p.SetTemperature(temperature=temperature)
    # MaxExpect partition.pfs MaxExpect.ct --DNA --gamma 1 --percent 10 --structures 20 --window 3
    # RNA and ProbScan objects are iterable. To iterate over the sequence:
    # for nuc in p: print(nuc)
    # It's also possible to get the pairing information and to manipulate it within python
    if basefilename is None:
        basefilename = uuid.uuid4().hex
    aaa = p.PartitionFunction(basefilename + '.pfs')
    # TODO correctly handle non-zero error code - e.g. if no structures got created!
    # TODO same for failed partition function
    if aaa != 0:
        print(p.GetErrorMessage(aaa))
        exit(aaa)
    aaa = p.MaximizeExpectedAccuracy(maxPercent=max_percent, maxStructures=max_structures, window=window, gamma=gamma)
    if aaa != 0:
        print(p.GetErrorMessage(aaa))
        return [basefilename, {'plain_dot': "Error: " + p.GetErrorMessage(aaa)}]
    basedir = "/tmp"  # + os.path.abspath(os.path.dirname(__file__))
    print(basedir)
    aaa = p.WriteCt(basedir + "/" + basefilename + ".ct")
    if aaa != 0:
        print(p.GetErrorMessage(aaa))
        return [basefilename, {'plain_dot': "Error: " + p.GetErrorMessage(aaa)}]

    aaa = p.WriteDotBracket(basedir + "/" + basefilename + ".dot")
    if aaa != 0:
        print(p.GetErrorMessage(aaa))
        return [basefilename, {'plain_dot': "Error: " + p.GetErrorMessage(aaa)}]
    pth = os.environ['DATAPATH']
    if not pth.endswith("/"):
        pth += "/"
    my_cmd = pth + '../exe/draw ' + basefilename + '.ct ' + basefilename + '.ps -p ' + basefilename + '.pfs && ps2pdf ' + \
             basefilename + '.ps && ' + pth + '../exe/draw ' + basefilename + '.ct ' + basefilename + '.svg -p ' + \
             basefilename + '.pfs --svg -N 1'
    print(os.system(my_cmd))

    file_content = {}
    for ending in [".ps", ".ct", ".svg", ".pdf", ".pfs", ".dot"]:
        with open(basefilename + ending, 'rb') as infile:
            content = infile.read()
            file_content[ending] = base64.standard_b64encode(content).decode("utf-8")
            if ending == ".dot":
                file_content['plain_dot'] = content.decode("utf-8").split("\n")[2]
    save_to_redis(basefilename, json.dumps(file_content), 31536000)
    print(os.system("rm " + basefilename + ".*"))
    os.chdir(prev_wd)
    return [basefilename, file_content]


@simulator_api.route('/api/all', methods=['GET', 'POST'])
@require_apikey
def do_all_wrapper():
    """
    The method wraps the thread_do_all method to get the app context and allow the usage of another thread for every
    request. The inner method calls @do_all with the sequence and sends an email with the uuid of the result if enabled.
    If the uuid already exists the results are taken from the redis server and if the sequence is longer than 1000 bases
    the calculation may need some time and the user will get an email and won't have to wait for it to finish.
    :return:
    """

    @copy_current_request_context
    def thread_do_all(r_method, email, host):
        res = do_all(r_method)
        uuid = list(res.json.values())[0]["uuid"]
        send_mail("noreply@mosla.de", [email],
                  "Access your result at: " + host + "query_sequence?uuid=" + uuid,
                  subject="[MOSLA] Your DNA-Simulation finished")

    if request.method == 'POST':
        r_method = request.json
    else:
        r_method = request.args
    r_uid = r_method.get('uuid')
    # if the uuid already exists load the results from redis
    if r_uid is not None:
        r_res = None
        try:
            r_res = read_from_redis(r_uid)
        except Exception as e:
            print("Error while talking to Redis-Server:", e)
        if r_res is not None:
            return jsonify(json.loads(r_res))
        elif 'sequence' not in r_method:
            return jsonify({"did_succeed": False})
    # TODO estimate time needed
    send_via_mail = r_method.get('send_mail')
    if (len(r_method.get('sequence')) > 1000 or (send_via_mail and r_uid is None)) and request:
        # spawn a thread, of do_all and send an email to the user to
        apikey = Apikey.query.filter_by(apikey=r_method.get('key')).first()
        user = User.query.filter_by(user_id=apikey.owner_id).first()
        email = user.email
        if apikey.owner_id == 0:
            # we are not really logged in, just using the free api-key!
            email = r_method.get('email')
        thread = Thread(target=thread_do_all, args=(r_method, email, request.host_url))
        thread.start()
        return jsonify({"result_by_mail": True, "did_succeed": False})
    else:
        return do_all(r_method)


# @require_apikey
def do_all(r_method):
    """
    This method collects all the parameters for the calculation of the different error probabilities for the sequence.
    It calls all the methods that are calculating error probabilities with the specified parameters and collects the
    results. Depending on @as_html the results including the sequence, uuid, error probabilities, modified sequence,
    seed and fastq quality scoring are saved either as html data or json file.
    :param r_method: Request to calculate the results for.
    :return: Jsonified results of the request.
    """

    def threaded_create_max_expect(sequence, basefilename, temp):
        return create_max_expect(sequence, basefilename=basefilename, temperature=temp, max_percent=10, gamma=1,
                                 max_structures=1, window=3)

    # TODO
    # getting the configuration of the website to calculate the error probabilities
    sequences = r_method.get('sequence')  # list
    kmer_window = r_method.get('kmer_windowsize')
    gc_window = r_method.get('gc_windowsize')
    enabled_undesired_seqs = r_method.get('enabledUndesiredSeqs')
    seq_meth = r_method.get('sequence_method')
    seq_meth_conf = r_method.get('sequence_method_conf')
    synth_meth = r_method.get('synthesis_method')
    synth_meth_conf = r_method.get('synthesis_method_conf')

    err_simulation_order = r_method.get('err_simulation_order')

    gc_error_prob_func = create_error_prob_function(r_method.get('gc_error_prob'))
    homopolymer_error_prob_func = create_error_prob_function(r_method.get('homopolymer_error_prob'))
    kmer_error_prob_func = create_error_prob_function(r_method.get('kmer_error_prob'))
    use_error_probs = r_method.get('use_error_probs')
    seed = r_method.get('random_seed')
    seed = np.uint32(np.float(seed) % 4294967296) if seed else None
    do_max_expect = bool(r_method.get('do_max_expect', False))
    temp = float(r_method.get('temperature', 310.15))
    as_html = r_method.get('asHTML', False)
    res_all = {}
    if type(sequences) == str:
        sequences = [sequences]
    # calculating all the different error probabilities and adding them to res
    for sequence in sequences:
        basefilename = uuid.uuid4().hex
        pool = ThreadPool(processes=1)
        async_res = None
        if do_max_expect:
            async_res = pool.apply_async(threaded_create_max_expect, (sequence, basefilename, temp))
        pool.close()
        if enabled_undesired_seqs:
            try:
                undesired_sequences = {}
                for useq in enabled_undesired_seqs:
                    if useq['enabled']:
                        undesired_sequences[useq['sequence']] = float(useq['error_prob']) / 100.0
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
            # Syntehsis:
            for meth in err_simulation_order['Synthesis']:
                # we want to permutate the seed because a user might want to use the same ruleset multiple times and
                # therefore expects different results for each run ( we have to make sure we are in [0,2^32-1] )
                seed = (synthesis_error(g.graph.nodes[0]['seq'], g, meth['id'], process="synthesis", seed=seed,
                                        conf=meth['conf']) + 1) % 4294967296  # + "_" + meth['name']

            # Storage / PCR:
            """
            for meth in err_simulation_order['StoragePCR']:  # TODO rename at frontend
                # we want to permutate the seed because a user might want to use the same ruleset multiple times and
                # therefore expects different results for each run ( we have to make sure we are in [0,2^32-1] )
                seed = (synthesis_error(g.graph.nodes[0]['seq'], g, meth['id'], process="synthesis", seed=seed,
                                        conf=meth['conf']) + 1) % 4294967296  # TODO rename 'process="..."'
            """
            # Storage / PCR:
            for meth in err_simulation_order['Sequencing']:
                # we want to permutate the seed because a user might want to use the same ruleset multiple times and
                # therefore expects different results for each run ( we have to make sure we are in [0,2^32-1] )
                seed = (synthesis_error(g.graph.nodes[0]['seq'], g, meth['id'], process="sequencing", seed=seed,
                                        conf=meth['conf']) + 1) % 4294967296  # + "_" + meth['name']

            # The code commented out is for visualization of sequencing and synthesis
            # methods seperated, it is inefficient - better to color the sequence
            # based on the final graph using the identifiers.
            # dc_g = deepcopy(g)
            # synth_html = htmlify(dc_g.get_lineages(), synthesis_error_seq, modification=True)
            # sequencing_error(synthesis_error_seq, g, seq_meth, process="sequencing", seed=seed, conf=seq_meth_conf)
            # sequencing_error(synthesis_error_seq, g_only_seq, seq_meth, process="sequencing", seed=seed)
            # sequencing_error_seq = g_only_seq.graph.nodes[0]['seq']
            # seq_html = htmlify(g_only_seq.get_lineages(), sequencing_error_seq, modification=True)

        mod_seq = g.graph.nodes[0]['seq']
        mod_res = g.get_lineages()
        uuid_str = str(uuid.uuid4())
        fastqOr = "".join(fastq_errors(res, sequence))
        fastqMod = "".join(fastq_errors(res, mod_seq, modified=True))
        # htmlifies the results for the website or sets the raw data as res
        plain_dot = ""
        if do_max_expect:
            plain_dot = str(async_res.get()[1]['plain_dot'])
        if as_html:
            kmer_html = htmlify(kmer_res, sequence)
            gc_html = htmlify(gc_window_res, sequence)
            homopolymer_html = htmlify(homopolymer_res, sequence)
            mod_html = htmlify(mod_res, mod_seq, modification=True)
            res = {'res': {'modify': mod_html, 'subsequences': usubseq_html,
                           'kmer': kmer_html, 'gccontent': gc_html, 'homopolymer': homopolymer_html,
                           'all': htmlify(res, sequence), 'fastqOr': fastqOr, 'fastqMod': fastqMod, 'seed': str(seed),
                           'maxexpectid': basefilename, 'dot_seq': "<pre>" + plain_dot + "</pre>"},
                   'uuid': uuid_str, 'sequence': sequence}
        elif not as_html:
            res = {
                'res': {'modify': mod_res, 'kmer': kmer_res, 'gccontent': gc_window_res, 'homopolymer': homopolymer_res,
                        'all': res, 'uuid': uuid_str, 'sequence': sequence, 'seed': str(seed),
                        'maxexpectid': basefilename, 'modified_sequence': mod_seq, 'fastqOr': fastqOr,
                        'fastqMod': fastqMod, 'dot_seq': plain_dot}}

        res_all[sequence] = res
        res = {k: r['res'] for k, r in res_all.items()}
        r_method.pop('key')  # drop key from stored fields
        try:
            r_method.pop('email')
        except:
            pass
        try:
            save_to_redis(uuid_str, json.dumps({'res': res, 'query': r_method, 'uuid': uuid_str}), 31536000)
        except redis.exceptions.ConnectionError as ex:
            print('Could not connect to Redis-Server')
    return jsonify(res_all)


def synthesis_error(sequence, g, synth_meth, seed, process="synthesis", conf=None):
    """
    Either takes an uploaded configuration or gets the selected configuration by its ID from the database to build a
    SequencingError object with the parameters. Calculates synthesis error and mutation probabilities of the sequence
    based on the configuration and returns the result.
    :param sequence: Sequence to calculate the synthesis error probabilites for.
    :param g: Graph to store the results.
    :param synth_meth: Selected synthesis method.
    :param seed: Used seed.
    :param process: "synthesis"
    :param conf: Uploaded configuration, None by default.
    :return: Synthesis error probabilities for the sequence.
    """
    if conf is None:
        tmp = SynthesisErrorRates.query.filter(
            SynthesisErrorRates.id == int(synth_meth)).first()
        err_rate_syn = tmp.err_data
        err_att_syn = tmp.err_attributes
    else:
        err_rate_syn = conf['err_data']
        err_att_syn = conf['err_attributes']
    synth_err = SequencingError(sequence, g, process, err_att_syn, err_rate_syn, seed=seed)
    return synth_err.lit_error_rate_mutations()


def sequencing_error(sequence, g, seq_meth, seed, process="sequencing", conf=None):
    """
    Either takes an uploaded configuration or gets the selected configuration by its ID from the database to build a
    SequencingError object with the parameters. Calculates sequencing error probabilities of the sequence based on the
    configuration and returns the result.
    :param sequence: Sequence to calculate the sequencing error probabilites for.
    :param g: Graph to store the results.
    :param seq_meth: Selected sequencing method.
    :param seed: Used seed.
    :param process: "sequencing"
    :param conf: Uploaded configuration, None by default.
    :return: Sequencing error probabilities for the sequence.
    """
    if conf is None:
        tmp = SequencingErrorRates.query.filter(
            SequencingErrorRates.id == int(seq_meth)).first()
        err_rate_seq = tmp.err_data
        err_att_seq = tmp.err_attributes
    else:
        err_rate_seq = conf['err_data']
        err_att_seq = conf['err_attributes']
    seq_err = SequencingError(sequence, g, process, err_att_seq, err_rate_seq, seed=seed)
    return seq_err.lit_error_rate_mutations()


def manual_errors(sequence, g, error_res, seed, process='Calculated Error'):
    """
    If 'Use Calculated Error Probabilities" is selected, this method creates a SequencingError object with the manually
    set parameters and calculates the mutation and error probabilities for the sequence.
    :param sequence: Sequence to calculate the manual error probabilites for.
    :param g: Graph to store the results.
    :param error_res: Selected errors.
    :param seed: Used seed.
    :param process: "Calculated Error"
    :return:
    """
    seq_err = SequencingError(sequence, g, process, seed=seed)
    for att in error_res:
        for err in att:
            seq_err.manual_mutation(err)


def fastq_errors(input, sequence, sanger=True, modified=False):
    """
    Calculates the fastq quality scoring for sequences by adding up all error probabilities for every single base and
    translating them to the corresponding fastq if the user wants to use the fastq format for the results. The method
    can either use the Sanger variant (default) to calculate the fastq quality scoring or the Solexa variant.
    :param input: Error probabilities for the given sequence
    :param sequence: The sequence to get the fastq quality scoring for.
    :param sanger: True: Use Sangers variant to calculate the quality. False: Use Solexa variant.
    :param modified: True: Use a modified sequence and delete whitespaces. False: Use the original sequence.
    :return: The fastq quality list for the given sequence.
    """
    tmp = []
    tmp_pos = []
    for i in range(0, len(sequence)):
        tmp.append(0.0)
        if sequence[i] == " ":
            tmp_pos.append(i)
    for error in input:
        endpos = error["endpos"]
        if endpos >= len(tmp):
            endpos = len(tmp) - 1
        for pos in range(error["startpos"], endpos + 1):
            tmp[pos] += error["errorprob"]
    res = []
    if sanger:
        for i in range(0, len(tmp)):
            if 0 < tmp[i] <= 1:
                q_score = round((-10 * math.log(tmp[i], 10)))
            elif tmp[i] > 0 and tmp[i] > 1:
                q_score = 0
            else:
                q_score = 40
            res.append(chr(q_score + 33))
    if not sanger:
        for i in range(0, len(tmp)):
            if 0 < tmp[i] <= 1:
                q_score = round((-10 * math.log((tmp[i] / (1 - tmp[i])), 10)))
            elif tmp[i] > 0 and tmp[i] > 1:
                q_score = 0
            else:
                q_score = 40
            res.append(chr(q_score + 33))
    if modified:
        cnt = 0
        for pos in tmp_pos:
            del res[pos - cnt]
            cnt += 1
    return res


def htmlify(input, sequence, modification=False):
    """
    All the calculations are done on the server to speed them up. Since the results are required to be in the html
    format to display them on the website, this methods htmlifies them. The html code contains information about the
    error classes and probabilities of every single base and the colorization displayed at the website. To colorize and
    format the results @build_html takes a list with results and returns the html formatted code for it.
    :param input: Input to htmlify. Mostly results of the error calculations.
    :param sequence: Sequence.
    :param modification: True: Add information about the process that lead to a modification.
    :return: Html code for the colorized and formatted sequence.
    """
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
                if modification:
                    lineage = err_lin[seq_pos]
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
    """
    Generates html strings for every element in a list of results to format and colorize them and returns the html code.
    @colorize is used for the colorization and is called for every single base with its error probability.
    :param res_list: List of results to build html code for.
    :param reducesets:
    :return: Html code for the res_list.
    """
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
    return "<pre>" + res + "</pre>"


def colorize(error_prob):
    """
    Colorizes the bases based on the error probabilities.
    :param error_prob: Error probability for the base.
    :return: Color for the base.
    """
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


if __name__ == "__main__":
    print(create_max_expect(
        "AACGCTGACGTCAGATCGATCAGTCGATCGTACGTACGTACGAACGCTGACGTCAGATCGATCAGTCGATCGTACGTACGTACGAACGCTGACGTCAGATCGATCAGTCGATCGTACGTACGTACGAACGCTGACGTCAGATCGATCAGTCGATCGTACGTACGTACG",
        310.15))

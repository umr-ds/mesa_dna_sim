function addMismatch(obj_id) {
    let org_seq = $('#synth_error_mismatched_org_seq_' + obj_id);
    let mismatched_seq = $('#synth_error_mismatched_seq_' + obj_id);
    let host_container = $('#mismatch_container_' + obj_id);
    let curr_id = 0;
    if (host_container[0] !== undefined) {
        curr_id = host_container[0].childNodes.length;
    }
    obj_id = obj_id + "_" + curr_id;
    host_container.append("<div class=\"columns is-full has-no-margin-bottom\" id='mismatch_" + obj_id + "'><div class=\"column\">\n" +
        "<label class=\"form-group has-float-label\">\n" +
        "<p class=\"control has-icons-right\">\n" +
        "<input style=\"width:100%\" class=\"input is-rounded\" id=\"synth_error_mismatched_org_seq_" + obj_id + "\"\n" +
        "type=\"text\" name=\"Original DNA-Sequence\" placeholder=\"DNA-Sequence\"\n" +
        "value=\"" + org_seq.val() + "\" required>\n" +
        "<span class=\"icon is-right\"><i class=\"fas fa-dna\"></i></span></p>\n" +
        "<span><nobr>DNA-Sequence</nobr></span></label></div><div class=\"column\">\n" +
        "<label class=\"form-group has-float-label\">\n" +
        "<p class=\"control has-icons-right\">\n" +
        "<input style=\"width:100%\" class=\"input is-rounded\"\n" +
        "id=\"synth_error_mismatched_seq_" + obj_id + "\"\n" +
        "type=\"text\" name=\"Mismatched DNA-Sequence\"\n" +
        "placeholder=\"Mismatched DNA-Seq.\"\n" +
        "value=\"" + mismatched_seq.val() + "\" required>\n" +
        "<span class=\"icon is-right\">\n" +
        "<i class=\"fas fa-dna\"></i></span></p>\n" +
        "<span><nobr>Mismatched DNA-Sequence</nobr></span></label></div>\n" +
        "<div class=\"column is-one-fifth button-fill\">\n" +
        "<button class=\"button button-fill\" id=\"add_mismatch_" + obj_id + "\"\n" +
        "data-balloon=\"Remove this Mismatch (Rule has to be saved for this change to take effect!)\"\n" +
        "data-balloon-pos=\"up\" onclick=\"deleteMismatch('" + obj_id + "'); return false;\">Delete\n" +
        "</button></div></div>");
    org_seq.val("");
    mismatched_seq.val("");
}

function deleteMismatch(obj_id) {
    let host_container = $('#mismatch_' + obj_id);
    host_container.remove();
}

function addSynth(host) {
    /* Collect all Input-Values*/
    const deletion_A = $('#synth_error_deletion_A_new').val();
    const deletion_C = $('#synth_error_deletion_C_new').val();
    const deletion_G = $('#synth_error_deletion_G_new').val();
    const deletion_T = $('#synth_error_deletion_T_new').val();

    const deletion_homopolymer = $('#synth_error_deletion_homopolymer_new').val();
    const deletion_random = $('#synth_error_deletion_random_new').val();

    const deletion = {
        pattern: {A: deletion_A, C: deletion_C, G: deletion_G, T: deletion_T},
        position: {homopolymer: deletion_homopolymer, random: deletion_random}
    };

    const insertion_A = $('#synth_error_insertion_A_new').val();
    const insertion_C = $('#synth_error_insertion_C_new').val();
    const insertion_G = $('#synth_error_insertion_G_new').val();
    const insertion_T = $('#synth_error_insertion_T_new').val();

    const insertion_homopolymer = $('#synth_error_insertion_homopolymer_new').val();
    const insertion_random = $('#synth_error_insertion_random_new').val();

    const insertion = {
        pattern: {A: insertion_A, C: insertion_C, G: insertion_G, T: insertion_T},
        position: {homopolymer: insertion_homopolymer, random: insertion_random}
    };


    let mismatch = {};

    let org_seq = "";
    let mismatched_seq = "";
    $('#mismatch_container_new').each(function (idx, itm) {
        org_seq = $(itm).eq(idx).find('td[id^="synth_error_mismatched_org_seq"]').val();
        mismatched_seq = $(itm).eq(idx).find('td[id^="synth_error_mismatched_seq"]').val();
        mismatch[org_seq] = mismatched_seq
    });

    const err_data_deletion = $('#synth_error_raw_rate_deletion_new').val();
    const err_data_insertion = $('#synth_error_raw_rate_insertion_new').val();
    const err_data_mismatch = $('#synth_error_raw_rate_mismatch_new').val();
    const err_data_raw_rate = $('#synth_error_raw_rate_new').val();

    const err_data = {
        deletion: err_data_deletion,
        insertion: err_data_insertion,
        mismatch: err_data_mismatch,
        raw_rate: err_data_raw_rate
    };

    const synth_name = $('#description_new').val();

    const result = {
        err_attributes: {deletion: deletion, insertion: insertion, mismatch: mismatch},
        err_data: err_data,
        name: synth_name
    };

    /* Send to the Server */
    $.post({
        url: "http://" + host + "/api/add_synth_error_probs",
        contentType: 'application/json;charset=UTF-8',
        dataType: 'json',
        data: JSON.stringify({synth_data: result, asHTML: true}),
        async: true,
        beforeSend: function (xhr) {
            if (xhr && xhr.overrideMimeType) {
                xhr.overrideMimeType('application/json;charset=utf-8');
            }
        },
        success: function (data) {
            if (data.did_succeed) {
                /* On Success: add to the List + Clear Input*/
                //TODO
                $('#synthesis_errors').append(data.new_synth);
            } else {
                /* On Failure: either dont do anything, or show error?*/
                console.log("Error while adding new Synthesis-Error");
            }
        },
        fail: function (data) {
            /* On Failure: either dont do anything, or show error?*/
            console.log("Error while adding new Synthesis-Error");
        }
    });
}

function updateSynth() {
    /* Collect all Input-Values*/

    /* Send to the Server */
    $.post({
        url: "http://" + host + "/api/delete_synth",
        data: {synth_data: synth_data},
        async: true,
        beforeSend: function (xhr) {
            if (xhr && xhr.overrideMimeType) {
                xhr.overrideMimeType('application/json;charset=utf-8');
            }
        },
        dataType: 'json',
        success: function (data) {
            if (data.did_succeed) {
                /* On Success: add to the List + Clear Input*/
                //TODO
            } else {
                /* On Failure: either dont do anything, or show error?*/
                console.log("Error while adding new Synthesis-Error");
            }
        },
        fail: function (data) {
            /* On Failure: either dont do anything, or show error?*/
            console.log("Error while adding new Synthesis-Error");
        }
    });
}

function deleteSynth(host, obj_id) {
    /* Send to the Server */
    $.post({
        url: "http://" + host + "/api/delete_synth",
        data: {synth_id: obj_id, do_delete: true},
        async: true,
        beforeSend: function (xhr) {
            if (xhr && xhr.overrideMimeType) {
                xhr.overrideMimeType('application/json;charset=utf-8');
            }
        },
        dataType: 'json',
        success: function (data) {
            if (data.did_succeed) {
                /* On Success: Remove from List*/
                let host_container = $('#synthesis_error_' + obj_id);
                host_container.remove();
            } else {
                /* On Failure: either dont do anything, or show error?*/
                console.log("Error while deleting Synthesis-Error " + obj_id);
            }
        },
        fail: function (data) {
            /* On Failure: either dont do anything, or show error?*/
            console.log("Error while deleting Synthesis-Error " + obj_id);
        }
    });
}
function addSubSeq(host) {
    let sequence = $('#addsequence').val();
    let error_prob = $('#errorprob').val() / 100.0;
    let description = $('#description').val();
    $.post({
        url: host + "api/add_subsequence",
        data: {sequence: sequence, error_prob: error_prob, description: description},
        async: true,
        beforeSend: function (xhr) {
            if (xhr && xhr.overrideMimeType) {
                xhr.overrideMimeType('application/json;charset=utf-8');
            }
        },
        dataType: 'json',
        success: function (data) {
            if (data.did_succeed) {
                let subseq_box = $('#existing_subseqs');
                let dattime = new Date(data.created * 1000).toUTCString();
                subseq_box.append("<div class=\"control has-padding-03\" id=\"subseq_" + data.id + "\">\n" +
                    "<table>\n" +
                    "<tr>\n" +
                    "<td style=\"width:53%\"><label class=\"form-group has-float-label\"><p class=\"control has-icons-right\"><input style=\"width:100%\" class=\"input is-rounded\" type=\"text\" name=\"sequence\"\n" +
                    "placeholder=\"\" size=\"50\" value=\"" + data.sequence + "\" required><span class=\"icon is-right\">\n" +
                    "<i class=\"fas fa-dna\"></i></span></p><span>Sequence</span></label></td>\n" +
                    "<td  style=\"width:15%\"><label class=\"form-group has-float-label\"><input style=\"width:100%\" class=\"input is-rounded\" type=\"number\" name=\"error_prob\"\n" +
                    "placeholder=\"\" size=\"30\" value=\"" + data.error_prob * 100.0 + "\" required\n" +
                    "min=\"0.0\"\n" +
                    "max=\"100.0\" step=\"0.01\"><span style=\"white-space: nowrap;\">Error Probability</span></label></td>\n" +
                    "<td  style=\"width:15%\"><label class=\"form-group has-float-label\"><input style=\"width:100%\" class=\"input is-rounded\" type=\"text\" name=\"description\"\n" +
                    "placeholder=\"Description\" value=\"" + data.description + "\" size=\"20\" value=\"\"\n" +
                    "required><span>Description</span></label></td>" +
                    "<td style=\"width:5%\">\n" +
                    "<button class=\"button\"\n" +
                    "data-balloon=\"Request validation\"\n" +
                    "data-balloon-pos=\"up\" id=\"validate_subseq_{{ subsequence.id }}\"\n" +
                    "onclick=\"updateSeq('" + host + "'," + data.id + "); let callback_func = function (desc) { validateSeq('" + host + "'," + data.id + ", desc) };showValidationOverlay('', callback_func); return false;\">Publish</button>\n" +
                    "</td>" +
                    "<td style=\"width:5%\"><button class=\"button\" data-balloon=\"Updating will remove the Validation!\"\n" +
                    "data-balloon-pos=\"up\" id=\"update_subseq_" + data.id + "\"\n" +
                    "onclick=\"updateSeq('" + host + "', " + data.id + "); return false;\"> Update<\/button>" +
                    "<\/td>" +
                    "<td style=\"width:5%\">\n" +
                    "<button class=\"button\" id=\"delete_subseq_" + data.id + "\" data-balloon=\"Delete this Subsequence created at: " + dattime + "\"" +
                    "data-balloon-pos=\"up\" onclick=\"deleteSeq('" + host + "', " + data.id + "); return false;\">Delete\n" +
                    "</button>\n" +
                    "</td>\n" +
                    "</tr>\n" +
                    "</table>\n" +
                    "<br/><\/div>"
                ).fadeIn(400)
                ;
                set_listener();
                $('#addsequence').val('');
                $('#errorprob').val('');
                $('#description').val('');
            } else {
                console.log("Error while adding new Sequence ");
            }
        },
        fail: function (data) {
            console.log("Error while adding new Sequence");
            //$('#text_lettering').text(data);
        }
    });
}

function updateSeq(host, id) {
    let curr_subseq = $('#subseq_' + id);
    let sequence = curr_subseq.children().find("[name='sequence']");
    let error_prob = curr_subseq.children().find("[name='error_prob']");
    let desc = curr_subseq.children().find("[name='description']");
    $.post({
        url: host + "api/update_subsequence",
        data: {
            sequence_id: id,
            sequence: sequence.val(),
            error_prob: error_prob.val() / 100.0,
            description: desc.val()
        },
        async: true,
        beforeSend: function (xhr) {
            if (xhr && xhr.overrideMimeType) {
                xhr.overrideMimeType('application/json;charset=utf-8');
            }
        },
        dataType: 'json',
        success: function (data) {
            console.log("Update successful for id=" + data.id.toString());
        },
        fail: function (data) {
            console.log("Update failed for id=" + data.id.toString());
            //$('#text_lettering').text(data);
        }
    });
}

function validateSeq(host, id, validation_desc) {
    let btn = $('#validate_subseq_' + id);
    //let curr_subseq = $('#subseq_' + id);
    //let sequence = curr_subseq.children().find("[name='sequence']");
    //let error_prob = curr_subseq.children().find("[name='error_prob']");
    //let desc = curr_subseq.children().find("[name='description']");
    $.post({
        url: host + "api/apply_for_validation_subsequence",
        data: {
            sequence_id: id,
            validation_desc: validation_desc
            /*sequence: sequence.val(),
            error_prob: error_prob.val() / 100.0,
            description: desc.val()*/
        },
        async: true,
        beforeSend: function (xhr) {
            if (xhr && xhr.overrideMimeType) {
                xhr.overrideMimeType('application/json;charset=utf-8');
            }
        },
        dataType: 'json',
        success: function (data) {
            console.log("Request for validation for id=" + data.id.toString() + " was successful.");
            btn.prop("disabled", true);
            if (data.validated) {
                btn.attr("data-balloon", "Already validated - update to remove validation!")
            } else {
                btn.attr("data-balloon", "Awaiting validation, you can still update.")
            }
        },
        fail: function (data) {
            console.log("Request for Validation for id=" + data.id.toString() + " failed.");
            //$('#text_lettering').text(data);
        }
    });
}

function deleteSeq(host, id) {
    $.post({
        url: host + "api/delete_subsequence",
        data: {sequence_id: id, do_delete: true},
        async: true,
        beforeSend: function (xhr) {
            if (xhr && xhr.overrideMimeType) {
                xhr.overrideMimeType('application/json;charset=utf-8');
            }
        },
        dataType: 'json',
        success: function (data) {
            if (data.did_succeed) {
                let toRemove = $('#subseq_' + data.deleted_id);
                toRemove.remove()
            } else {
                console.log("Error while deleting Sequence " + id);
            }
        },
        fail: function (data) {
            console.log("Error while deleting Sequence" + id);
            //$('#text_lettering').text(data);
        }
    });
}


function addMismatch(method, obj_id) {
    let dna_seq = $('#' + method + '_error_mismatched_org_seq_' + obj_id);
    let dna_seq_val = dna_seq.val();
    let noPossibleMismatches = $('#' + method + '_error_mismatched_seq_' + obj_id);
    let noPossibleMismatches_val = noPossibleMismatches.val();
    let host_container = $('#' + method + '_mismatch_container_' + obj_id);
    let curr_id = 0;
    if (host_container[0] !== undefined) {
        curr_id = host_container[0].childNodes.length;
    }
    obj_id = obj_id + "_" + curr_id;
    let buildup_html = "<div class=\"columns is-multiline is-full box has-no-padding-top has-no-padding-bottom is-marginless\" id=\"mismatch_" + obj_id + "\">\n" +
        "<div class=\"column is-two-fifths has-no-margin-bottom has-no-margin-left has-no-padding-left\">\n" +
        "    <label class=\"form-group has-float-label\">\n" +
        "        <p class=\"control has-icons-right\">\n" +
        "            <input style=\"width:100%\" class=\"input is-rounded\"\n" +
        "                   id=\"" + method + "_error_mismatched_org_seq_" + obj_id + "\"\n" +
        "                   type=\"text\" name=\"Original DNA-Sequence\"\n" +
        "                   placeholder=\"DNA-Sequence\"\n" +
        "                   value=\"" + dna_seq_val + "\"\n" +
        "                   required>\n" +
        "            <span class=\"icon is-right\">\n" +
        "    <i class=\"fas fa-dna\"></i>\n" +
        "</span>\n" +
        "        </p>\n" +
        "        <span style=\"white-space: nowrap;\">Original DNA-Sequence</span>\n" +
        "    </label>\n" +
        "</div>\n" +
        "<div class=\"column is-two-fifths has-no-margin-left has-no-padding-left\">\n" +
        "    <label class=\"form-group has-float-label\">\n" +
        "        <p class=\"control has-icons-right\">\n" +
        "            <input style=\"width:100%\" class=\"input is-rounded\"\n" +
        "                   id=\"" + method + "_error_mismatched_seq_" + obj_id + "\"\n" +
        "                   type=\"number\" name=\"# possible Mismatches\"\n" +
        "                   placeholder=\"2\" min=\"1\" max=\"25\" value=\"" + noPossibleMismatches_val + "\"\n" +
        "                   required disabled>\n" +
        "            <span class=\"icon is-right\">\n" +
        "    <i class=\"fas fa-percentage\"></i>\n" +
        "</span>\n" +
        "        </p>\n" +
        "        <span style=\"white-space: nowrap;\"># possible Mismatches</span>\n" +
        "    </label>\n" +
        "</div>\n" +
        "\n" +
        "<div class=\"column is-one-fifth button-fill has-no-margin-left has-no-padding-left\">\n" +
        "    <button class=\"button button-fill\" id=\"add_mismatch_" + method + "_" + obj_id + "\"\n" +
        "            data-balloon=\"Remove this Mismatch (Rule has to be Updated for this change to take effect!)\"\n" +
        "            data-balloon-pos=\"up\"\n" +
        "            onclick=\"deleteMismatch('" + method + "', '" + obj_id + "'); return false;\">\n" +
        "        Delete\n" +
        "    </button>\n" +
        "</div>\n" +
        "<div class=\"column is-full is-paddingless\"></div>\n" +
        "<div class=\"column is-one-fifth\" id=\"toogle-use-position\">\n" +
        "    <label data-balloon=\"Use Position based Mismatching\"\n" +
        "           data-balloon-pos=\"up\">\n" +
        "        <input type=\"checkbox\" aria-label=\"Use positional Mismatch\" id=\"" + method + "_mismatch_positioning_" + obj_id + "\"\n" +
        "               onchange=\"$('#" + method + "_error_mismatched_startpos_" + obj_id + "').attr('disabled',!$(this)[0].checked);\n" +
        "                         $('#" + method + "_error_mismatched_endpos_" + obj_id + "').attr('disabled',!$(this)[0].checked)\"\n" +
        "               class=\"switch is-rounded is-large button-fill no-outline\" name=\"" + method + "_mismatch_positioning_" + obj_id + "\" />\n" +
        "        <label for=\"" + method + "_mismatch_positioning_" + obj_id + "\" class=\"no-outline\"></label>\n" +
        "    </label>\n" +
        "</div>\n" +
        "    <div class=\"column is-two-fifths has-no-margin-bottom has-no-margin-left has-no-padding-left\">\n" +
        "    <label class=\"form-group has-float-label\">\n" +
        "        <p class=\"control has-icons-right\">\n" +
        "            <input style=\"width:100%\" class=\"input is-rounded\"\n" +
        "                   id=\"" + method + "_error_mismatched_startpos_" + obj_id + "\"\n" +
        "                   type=\"number\" name=\"Startposition\"\n" +
        "                   placeholder=\"DNA-Sequence\" min=\"1\"\n" +
        "                   disabled\n" +
        "                   value=\"1\"\n" +
        "                   required>\n" +
        "            <span class=\"icon is-right\">\n" +
        "    <i class=\"fas fa-step-backward\"></i>\n" +
        "</span>\n" +
        "        </p>\n" +
        "        <span style=\"white-space: nowrap;\">Start Position</span>\n" +
        "    </label>\n" +
        "</div>\n" +
        "    <div class=\"column is-two-fifths has-no-margin-bottom has-no-margin-left has-no-padding-left\">\n" +
        "    <label class=\"form-group has-float-label\">\n" +
        "        <p class=\"control has-icons-right\">\n" +
        "            <input style=\"width:100%\" class=\"input is-rounded\"\n" +
        "                   id=\"" + method + "_error_mismatched_endpos_" + obj_id + "\"\n" +
        "                   type=\"number\" name=\"Original DNA-Sequence\"\n" +
        "                   placeholder=\"DNA-Sequence\" min=\"1\"\n" +
        "                   disabled\n" +
        "                   value=\"1\"\n" +
        "                   required>\n" +
        "            <span class=\"icon is-right\">\n" +
        "    <i class=\"fas fa-step-forward\"></i>\n" +
        "</span>\n" +
        "        </p>\n" +
        "        <span style=\"white-space: nowrap;\">End Position</span>\n" +
        "    </label>\n" +
        "</div>";

    let mismatch_class = "";
    if (noPossibleMismatches_val > 4)
        mismatch_class = " is-one-quarter";
    for (let possible_mismatch_no = 0; possible_mismatch_no < noPossibleMismatches_val; possible_mismatch_no++) {
        buildup_html = buildup_html + "    <div class=\"column has-no-margin-left has-no-padding-left" + mismatch_class +
            "\">\n" +
            "        <label class=\"form-group has-float-label\">\n" +
            "            <p class=\"control has-icons-right\">\n" +
            "                <input style=\"width:100%\" class=\"input is-rounded mismatch_inputfield\"\n" +
            "                       id=\"" + method + "_error_mismatched_seq_" + obj_id + "_" + possible_mismatch_no + "\"\n" +
            "                       type=\"text\"\n" +
            "                       name=\"mismatch_changed_" + possible_mismatch_no + "\"\n" +
            "                       placeholder=\"Mismatched Seq. " + possible_mismatch_no + "\"\n" +
            "                       value=\"\"\n" +
            "                       required>\n" +
            "                <span class=\"icon is-right\">\n" +
            "                    <i class=\"fas fa-dna\"></i>\n" +
            "                </span>\n" +
            "            </p>\n" +
            "            <span style=\"white-space: nowrap;\">Mismatch " + possible_mismatch_no + "</span>\n" +
            "        </label>\n" +
            "    </div>\n";
    }
    if (noPossibleMismatches_val > 1) {
        let tmp_arr = new Array(noPossibleMismatches_val).fill("");
        for (let i = 0; i < noPossibleMismatches_val; i++) {
            tmp_arr[i] = '"INVALID_' + i + '":' + (1.00 / (1.0 * noPossibleMismatches_val)).toString()
        }
        let data_vals = "{" + tmp_arr.join(",") + "}";
        buildup_html = buildup_html + "<div class=\"column is-full is-paddingless\"></div>\n" +
            "<div class=\"column has-horizontal-padding-0 has-padding-03\">\n" +
            "    <div class=\"button-fill sliders noUi-target noUi-ltr noUi-horizontal\"\n" +
            "         id=\"mismatch-" + method + "-slider-" + obj_id + "\"\n" +
            "         data-eid=\"" + obj_id + "\" data-mode=\"" + method + "\"\n" +
            "         data-mid=\"" + obj_id + "\"\n" +
            "         data-etype=\"mismatch\"  data-vals='" + data_vals + "'>\n" +
            "    </div>\n" +
            "</div>\n" +
            "<div class=\"column is-full is-paddingless is-marginless\"></div>\n" +
            "\n"
    }

    for (let possible_mismatch_no = 0; possible_mismatch_no < noPossibleMismatches_val; possible_mismatch_no++) {
        buildup_html = buildup_html + "    <div class=\"column has-no-margin-left has-no-padding-left" + mismatch_class
            + "\">\n" +
            "        <label class=\"form-group has-float-label\">\n" +
            "            <p class=\"control has-icons-right\">\n" +
            "                <input style=\"width:100%\" class=\"input is-rounded mismatch_inputfield\"\n" +
            "                       id=\"" + method + "_error_mismatched_seq_prob_" + obj_id + "_" + possible_mismatch_no + "\"\n" +
            "                       type=\"number\" name=\"mismatch_" + possible_mismatch_no + "\"\n" +
            "                       min=\"0\" max=\"100\" step=\"0.01\"\n" +
            "                       placeholder=\"\"\n" +
            "                       value=\"" + 100.00 / (1.0 * noPossibleMismatches_val) + "\"\n" +
            "                       required>\n" +
            "                <span class=\"icon is-right\">\n" +
            "                    <i class=\"fas fa-percentage\"></i>\n" +
            "                </span>\n" +
            "            </p>\n" +
            "            <span style=\"white-space: nowrap;\">Mismatch " + possible_mismatch_no + "</span>\n" +
            "        </label>\n" +
            "    </div>\n";
    }
    buildup_html = buildup_html + "</div>\n";
    host_container.append(buildup_html);
    dna_seq.val("");
    noPossibleMismatches.val(2);
    if (noPossibleMismatches_val > 1)
        initMismatchSlider(method, $("#mismatch-" + method + "-slider-" + obj_id)[0])
    set_listener();
}

function clearNewRuleContainer(method) {
    $('#' + method + '-slider-deletion-new')[0].noUiSlider.set([25, 50, 75, 100]);
    $('#' + method + '-slider-insertion-new')[0].noUiSlider.set([25, 50, 75, 100]);
    $('#' + method + '-position-slider-deletion-new')[0].noUiSlider.set(50);
    $('#' + method + '-position-slider-insertion-new')[0].noUiSlider.set(50);
    $('#err_data-' + method + '-slider-new')[0].noUiSlider.set([33.33, 66.66]);
    $('#' + method + '_error_raw_rate_new').val(0.05);
    $('#' + method + '_mismatch_container_new').empty();
    $('#' + method + '_description_new').val("");
    $('#' + method + '_error_mismatched_org_seq_new').val("");
    $('#' + method + '_error_mismatched_seq_new').val(2);
}

function deleteMismatch(method, obj_id) {
    let host_container = $('#' + 'mismatch_' + obj_id);
    host_container.remove();
}

function validateCustomError(host, method, id, desc) {
    let btn = $('#validate_'+ method + '_' + id);
    $.post({
        url: host + "api/validate_custom_error",
        contentType: 'application/json;charset=UTF-8',
        dataType: 'json',
        data: JSON.stringify({id: id, method: method, validation_desc: desc}),
        async: true,
        beforeSend: function (xhr) {
            if (xhr && xhr.overrideMimeType) {
                xhr.overrideMimeType('application/json;charset=utf-8');
            }
        },
        success: function (data) {
            if (data.did_succeed) {
                console.log("Requested validation for " + method + "-Error " + data.id.toString());
                if (data.validated) {
                    btn.attr("data-balloon", "Already validated - update to remove validation!")
                } else {
                    btn.attr("data-balloon", "Awaiting validation, you can still update.")
                }
            } else {
                /* On Failure: either dont do anything, or show error?*/
                console.log("Error while requesting validation for " + method + "-Error " + data.id.toString());
            }

        },
        fail: function (data) {
            /* On Failure: either dont do anything, or show error?*/
            console.log("Error while requesting validation for " + method + "-Error");
        }
    });
}

function sendCustomError(host, method, id) {
    /* Check for required values */
    if (!$('#' + method + '_description_' + id).val()){
        return false;
    }
    /* Collect all Input-Values*/
    const deletion_A_elem = $('#' + method + '_error_deletion_A_' + id);
    const deletion_A = deletion_A_elem.val() / 100.0;
    const deletion_C_elem = $('#' + method + '_error_deletion_C_' + id);
    const deletion_C = deletion_C_elem.val() / 100.0;
    const deletion_G_elem = $('#' + method + '_error_deletion_G_' + id);
    const deletion_G = deletion_G_elem.val() / 100.0;
    const deletion_T_elem = $('#' + method + '_error_deletion_T_' + id);
    const deletion_T = deletion_T_elem.val() / 100.0;

    const deletion_homopolymer_elem = $('#' + method + '_error_deletion_homopolymer_' + id);
    const deletion_homopolymer = deletion_homopolymer_elem.val() / 100.0;
    const deletion_random_elem = $('#' + method + '_error_deletion_random_' + id);
    const deletion_random = deletion_random_elem.val() / 100.0;

    const deletion = {
        pattern: {A: deletion_A, C: deletion_C, G: deletion_G, T: deletion_T},
        position: {homopolymer: deletion_homopolymer, random: deletion_random}
    };

    const insertion_A_elem = $('#' + method + '_error_insertion_A_' + id);
    const insertion_A = insertion_A_elem.val() / 100.0;
    const insertion_C_elem = $('#' + method + '_error_insertion_C_' + id);
    const insertion_C = insertion_C_elem.val() / 100.0;
    const insertion_G_elem = $('#' + method + '_error_insertion_G_' + id);
    const insertion_G = insertion_G_elem.val() / 100.0;
    const insertion_T_elem = $('#' + method + '_error_insertion_T_' + id);
    const insertion_T = insertion_T_elem.val() / 100.0;

    const insertion_homopolymer_elem = $('#' + method + '_error_insertion_homopolymer_' + id);
    const insertion_homopolymer = insertion_homopolymer_elem.val() / 100.0;
    const insertion_random_elem = $('#' + method + '_error_insertion_random_' + id);
    const insertion_random = insertion_random_elem.val() / 100.0;

    const insertion = {
        pattern: {A: insertion_A, C: insertion_C, G: insertion_G, T: insertion_T},
        position: {homopolymer: insertion_homopolymer, random: insertion_random}
    };


    let mismatch = {};

    let org_seq = "";
    let noOfMismatches = 2;
    let doExit = false;
    let empy_mismatch = false;
    let positional_mismatch = false;
    let position_range = undefined;
    $('#' + method + '_mismatch_container_' + id).children().each(function (idx, itm) {
        org_seq = $(itm).children()[0].firstElementChild.firstElementChild.firstElementChild.value;
        noOfMismatches = $(itm).children()[1].firstElementChild.firstElementChild.firstElementChild.value;
        positional_mismatch = $(itm).children()[4].firstElementChild.firstElementChild.checked;
        if (positional_mismatch === true) {
            position_range = [parseInt($(itm).children()[5].firstElementChild.firstElementChild.firstElementChild.value),
                parseInt($(itm).children()[6].firstElementChild.firstElementChild.firstElementChild.value)];
        }
        //let positional_mismatch = $('#' + method + '_mismatch_positioning_' + obj_id).attr("checked");
        let innerMismatch = {};
        for (let i = 0; i < noOfMismatches; i++) {
            const nme = 'input[name="mismatch_changed_' + i.toString() + '"]';
            const tmp = $(itm).find(nme)[0].value;
            const num = 'input[name="mismatch_' + i.toString() + '"]';
            if (innerMismatch[tmp] !== undefined) {
                doExit = true;
                return false;
            }
            if (!tmp || !org_seq){
                empy_mismatch = true;
            }
            innerMismatch[tmp] = parseFloat($(itm).find(num)[0].value) / 100;
        }
        mismatch[org_seq] = innerMismatch;
    });
    if (empy_mismatch){
        return false;
    }
    if (doExit === true)
        return false;
    if (mismatch !== {}) {
        mismatch = {'pattern': mismatch};
        if (positional_mismatch === true)
            mismatch['position_range'] = position_range;
    }
    const err_data_deletion_elem = $('#' + method + '_error_raw_rate_deletion_' + id);
    const err_data_deletion = err_data_deletion_elem.val() / 100.0;
    const err_data_insertion_elem = $('#' + method + '_error_raw_rate_insertion_' + id);
    const err_data_insertion = err_data_insertion_elem.val() / 100.0;
    const err_data_mismatch_elem = $('#' + method + '_error_raw_rate_mismatch_' + id);
    const err_data_mismatch = err_data_mismatch_elem.val() / 100.0;
    const err_data_raw_rate_elem = $('#' + method + '_error_raw_rate_' + id);
    const err_data_raw_rate = err_data_raw_rate_elem.val() / 100.0;

    const err_data = {
        deletion: err_data_deletion,
        insertion: err_data_insertion,
        mismatch: err_data_mismatch,
        raw_rate: err_data_raw_rate
    };

    const synth_name_elem = $('#' + method + '_description_' + id);
    const synth_name = synth_name_elem.val();

    const result = {
        err_attributes: {deletion: deletion, insertion: insertion, mismatch: mismatch},
        err_data: err_data,
        name: synth_name,
        id: id,
        type: $('#' + method + '_type_' + id).val()
    };

    /* Send to the Server */
    let endpointstart = "";
    if (id === "new") {
        endpointstart = "add";
    } else {
        endpointstart = "update";
    }
    $.post({
        url: host + "api/" + endpointstart + "_" + method + "_error_probs",
        contentType: 'application/json;charset=UTF-8',
        dataType: 'json',
        data: JSON.stringify({data: result, asHTML: true}),
        async: true,
        beforeSend: function (xhr) {
            if (xhr && xhr.overrideMimeType) {
                xhr.overrideMimeType('application/json;charset=utf-8');
            }
        },
        success: function (data) {
            if (data.did_succeed) {
                //TODO visualize Success (e.g. hide spoiler?!)
                if (id === "new") {
                    result['validated'] = false;
                    result['isOwner'] = true;
                    if (method === "seq") {
                        seq_errors[data.id] = result;
                    } else if (method === "synth") {
                        synth_errors[data.id] = result;
                    } else if (method === "pcr") {
                        pcr_errors[data.id] = result;
                    } else {
                        storage_errors[data.id] = result;
                    }

                    let drawingDOM = $('#' + method + '_errors');

                    drawingDOM.append(data.content);
                    let regexstr = '[id^="' + method + '-position-slider"]';
                    drawingDOM.children().last().find($(regexstr)).each(function () {
                        initSlider(method, $(this)[0])
                    });
                    regexstr = '[id^="err_data-' + method + '-slider-"]';
                    drawingDOM.children().last().find($(regexstr)).each(function () {
                        initErrorSliders(method, $(this)[0])
                    });
                    regexstr = '[id^="' + method + '-slider"]';
                    drawingDOM.children().last().find($(regexstr)).each(function () {
                        initACGTSlider(method, $(this)[0]);
                    });
                    if (id === "new")
                        clearNewRuleContainer(method);
                }
            } else {
                /* On Failure: either dont do anything, or show error?*/
                console.log("Error while adding new " + method + "-Error");
            }
        },
        fail: function (data) {
            /* On Failure: either dont do anything, or show error?*/
            console.log("Error while adding new " + method + "-Error");
        }
    });
}

function deleteCustomError(host, method, obj_id) {
    /* Send to the Server */
    $.post({
        url: host + "api/delete_" + method,
        data: {id: obj_id, do_delete: true},
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
                let host_container = $('#' + method + '_error_' + obj_id).parent();
                host_container.remove();
            } else {
                /* On Failure: either dont do anything, or show error?*/
                console.log("Error while deleting " + method + "-Error " + obj_id);
            }
        },
        fail: function (data) {
            /* On Failure: either dont do anything, or show error?*/
            console.log("Error while deleting " + method + "-Error " + obj_id);
        }
    });
}


function initErrorSliders(method, elem) {
    let eid = elem.getAttribute('data-eid');
    let err_data = undefined;
    if (eid !== "new") {
        if (method === "seq") {
            err_data = seq_errors[eid].err_data;
        } else if (method === "synth") {
            err_data = synth_errors[eid].err_data;
        } else if (method === "pcr") {
            err_data = pcr_errors[eid].err_data;
        }else {
            err_data = storage_errors[eid].err_data;
        }
    }
    let startvar = [33.33, 66.66];
    if (err_data !== undefined) {
        startvar = [err_data.deletion * 100, (err_data.deletion + err_data.insertion) * 100]
    }
    noUiSlider.create(elem, {
        start: startvar, // T MUST be the remainder
        connect: [true, true, true],
        tooltips: [true, true],
        behaviour: 'drag',
        range: {
            'min': 0,
            'max': 100
        },
    });

    elem.noUiSlider.on('update', function (values, handle) {
        $('#' + method + '_error_raw_rate_deletion_' + eid)[0].value = round(values[0] - 0, 4);
        $('#' + method + '_error_raw_rate_insertion_' + eid)[0].value = round(values[1] - values[0], 4);
        $('#' + method + '_error_raw_rate_mismatch_' + eid)[0].value = round(100.0 - values[1], 4);
        //}
    });

    $('#' + method + '_error_raw_rate_deletion_' + eid)[0].addEventListener('change', function () {
        elem.noUiSlider.set([this.value, null]);
    });

    $('#' + method + '_error_raw_rate_insertion_' + eid)[0].addEventListener('change', function () {
        elem.noUiSlider.set([null, parseFloat(this.value) + parseFloat(elem.noUiSlider.get()[0])]);
    });

    $('#' + method + '_error_raw_rate_mismatch_' + eid)[0].addEventListener('change', function () {
        elem.noUiSlider.set([null, 100.00 - parseFloat(this.value)]);
    });


    let connect = elem.querySelectorAll('.noUi-connect');
    let classes = ['deletion-color', 'insertion-color', 'mismatch-color'];
    for (let i = 0; i < connect.length; i++) {
        connect[i].classList.add(classes[i]);
    }
}

function initSlider(method, elem) {
    let etype = elem.getAttribute('data-etype');
    let eid = elem.getAttribute('data-eid');
    let position = undefined;
    if (eid !== "new") {
        if (method === "seq") {
            position = seq_errors[eid].err_attributes[etype].position;
        } else if (method === "synth") {
            position = synth_errors[eid].err_attributes[etype].position;
        } else if (method ==="pcr") {
            position = pcr_errors[eid].err_attributes[etype].position;
        } else {
            position = storage_errors[eid].err_attributes[etype].position;
        }
    }
    let startvar = 50;
    if (position !== undefined) {
        startvar = position.homopolymer * 100;
    }
    noUiSlider.create(elem, {
        start: startvar, // T MUST be the remainder
        connect: [true, true],
        tooltips: true,
        behaviour: 'drag',
        range: {
            'min': 0,
            'max': 100
        },
    });

    elem.noUiSlider.on('update', function (values, handle) {
        //if (handle) {
        //$('#synth_error_mismatch_deletion-homopolymer_');
        $('#' + method + '_error_' + etype + "_homopolymer_" + eid)[0].value = round(values[0] - 0, 4);
        $('#' + method + '_error_' + etype + "_random_" + eid)[0].value = round(100.0 - values[0], 4);
        //}
    });

    $('#' + method + '_error_' + etype + "_homopolymer_" + eid)[0].addEventListener('change', function () {
        elem.noUiSlider.set([this.value]);
    });

    $('#' + method + '_error_' + etype + "_random_" + eid)[0].addEventListener('change', function () {
        elem.noUiSlider.set([null, null, 100.00 - parseFloat(this.value)]);
    });


    var connect = elem.querySelectorAll('.noUi-connect');
    var classes = ['homopolymer-color', 'random-color'];
    for (var i = 0; i < connect.length; i++) {
        connect[i].classList.add(classes[i]);
    }
}

function initACGTSlider(method, elem) {
    let etype = elem.getAttribute('data-etype');
    let eid = elem.getAttribute('data-eid');

    let pattern = undefined;
    if (eid !== "new") {
        if (method === "seq") {
            pattern = seq_errors[eid].err_attributes[etype].pattern;
        } else if (method === "synth") {
            pattern = synth_errors[eid].err_attributes[etype].pattern;
        } else if (method === "pcr") {
            pattern = pcr_errors[eid].err_attributes[etype].pattern;
        } else {
            pattern = storage_errors[eid].err_attributes[etype].pattern;
        }
    }
    let startvar = [25, 50, 75];
    if (pattern !== undefined) {
        startvar = [pattern.A * 100, (pattern.A + pattern.C) * 100, (pattern.A + pattern.C + pattern.G) * 100];
    }
    noUiSlider.create(elem, {
        start: startvar, // T MUST be the remainder
        connect: [true, true, true, true],
        tooltips: [true, true, true],
        behaviour: 'drag',
        range: {
            'min': 0,
            'max': 100
        },
    });


    elem.noUiSlider.on('update', function (values, handle) {
        //if (handle) {
        $('#' + method + '_error_' + etype + "_A_" + eid)[0].value = round(values[0] - 0, 4);
        $('#' + method + '_error_' + etype + "_C_" + eid)[0].value = round(values[1] - values[0], 4);
        $('#' + method + '_error_' + etype + "_G_" + eid)[0].value = round(values[2] - values[1], 4);
        $('#' + method + '_error_' + etype + "_T_" + eid)[0].value = round(100.0 - values[2], 4);
        //}
    });

    $('#' + method + '_error_' + etype + "_A_" + eid)[0].addEventListener('change', function () {
        elem.noUiSlider.set([this.value, null, null]);
    });

    $('#' + method + '_error_' + etype + "_C_" + eid)[0].addEventListener('change', function () {

        elem.noUiSlider.set([null, parseFloat(this.value) + parseFloat(elem.noUiSlider.get()[0]), null]);
    });

    $('#' + method + '_error_' + etype + "_G_" + eid)[0].addEventListener('change', function () {
        elem.noUiSlider.set([null, null, parseFloat(this.value) + parseFloat(elem.noUiSlider.get()[1])]);
    });

    $('#' + method + '_error_' + etype + "_T_" + eid)[0].addEventListener('change', function () {
        elem.noUiSlider.set([null, null, 100.00 - parseFloat(this.value)]);
    });


    var connect = elem.querySelectorAll('.noUi-connect');
    var classes = ['c-1-color', 'c-2-color', 'c-3-color', 'c-4-color', 'c-5-color'];

    for (var i = 0; i < connect.length; i++) {
        connect[i].classList.add(classes[i]);
    }
}


function initMismatchSlider(method, elem) {
    let mID = elem.getAttribute('data-mid'); // e.g. 19_0, 19_1, ...
    let mode = elem.getAttribute('data-mode'); // e.g. seq, synth...
    let dataVals = JSON.parse(elem.getAttribute('data-vals')); //json dict

    let arr = [];
    let counter = 0;
    let cnect = [];
    for (let key in dataVals) {
        if (arr.length === 0) {
            arr.push(dataVals[key] * 100);
        } else {
            arr.push(arr[arr.length - 1] + (dataVals[key] * 100));
        }
        cnect.push(true);
        if (!key.startsWith("INVALID_")) {
            $('#' + mode + '_error_mismatched_seq_' + mID + '_' + counter).val(key);
        } else {
            $('#' + mode + '_error_mismatched_seq_' + mID + '_' + counter).val("");
        }
        $('#' + mode + '_error_mismatched_seq_prob_' + mID + '_' + counter).val(dataVals[key] * 100);

        counter++;

    }
    arr.pop();
    noUiSlider.create(elem, {
        start: arr, // T MUST be the remainder
        connect: cnect,
        tooltips: true,
        behaviour: 'drag',
        range: {
            'min': 0,
            'max': 100
        },
    });

    elem.noUiSlider.on('update', function (values, handle) {
        let len = values.length;
        $('#' + method + '_error_mismatched_seq_prob_' + mID + '_0')[0].value = round(values[0] - 0, 4);
        for (let x = 1; x < len; x++) {
            $('#' + method + '_error_mismatched_seq_prob_' + mID + '_' + x)[0].value = round(values[x] - values[x - 1], 4);
        }
        $('#' + method + '_error_mismatched_seq_prob_' + mID + '_' + len)[0].value = round(100 - values[len - 1], 4);
    });

    let sze = elem.noUiSlider.get();
    if (typeof sze === 'string') {
        sze = 1;
    } else {
        sze = sze.length;
    }
    let tmp_arr = new Array(sze).fill(null);
    $('#' + method + '_error_mismatched_seq_prob_' + mID + '_0')[0].addEventListener('change', function () {
        tmp_arr[0] = this.value;
        elem.noUiSlider.set(tmp_arr);
    });

    for (let x = 1; x < sze - 1; x++) {
        tmp_arr = new Array(sze).fill(null);
        $('#' + method + '_error_mismatched_seq_prob_' + mID + '_' + x)[0].addEventListener('change', function () {
            tmp_arr[x] = parseFloat(this.value) + parseFloat(elem.noUiSlider.get()[x - 1]);
            elem.noUiSlider.set(tmp_arr);
        });
    }
    tmp_arr = new Array(sze).fill(null);
    $('#' + method + '_error_mismatched_seq_prob_' + mID + '_' + (sze - 1))[0].addEventListener('change', function () {
        tmp_arr[sze - 1] = 100.00 - parseFloat(this.value);
        elem.noUiSlider.set(tmp_arr);
    });

    let connect = elem.querySelectorAll('.noUi-connect');
    const classes = ['c-1-color', 'c-2-color', 'c-3-color', 'c-4-color', 'c-5-color', 'homopolymer-color', 'random-color', 'deletion-color'];
    for (let i = 0; i < connect.length; i++) {
        connect[i].classList.add(classes[i % classes.length]);
    }
}
let apikey = "";
let host = "";
let user_id = "";
let sorts = [];
let current_history_offset = 0;

function setApikey(hst, key) {
    apikey = key;
    host = hst;
    current_history_offset = 0;
}

function setUser(id) {
    user_id = id;
}

function makeHoverGroups(user_borders, full_border, force) {
    if (user_borders === undefined) {
        user_borders = true;
    }
    if (full_border === undefined) {
        full_border = false;
    }
    let x = 0;
    let all_groups = $('span[class^="g_" ],span[class*=" g_"]');
    if (all_groups.length > 500 && !force) {
        user_borders = false;
        full_border = false;
    }
    let lettering = $('.text_lettering');
    if (user_borders) {
        lettering.css('min-height', '70px');
        lettering.css('overflow-y', '');
    } else {
        lettering.css('min-height', '30px');
        lettering.css('overflow-y', 'hidden');
    }
    if (all_groups.length > 1000 && !force) {
        all_groups.unbind();
    } else {
        all_groups.each(function () {

                let cls = $(this).attr('class').split(" ");
                let tmp = $("." + cls[cls.length - 1]);
                if (user_borders) {
                    tmp.data('depth_id', x);
                }

                tmp.hover(function () {
                    let curr_elem = $("." + cls[cls.length - 1]);
                    if (user_borders) {
                        const i = curr_elem.data('depth_id');
                        curr_elem.css('border-bottom', '2px solid');
                        if (full_border)
                            curr_elem.css('border', '1px solid');
                        curr_elem.css('border-color', 'black');
                        curr_elem.css('padding-bottom', (i % 30) + 'px');
                    } else {
                        curr_elem.css('border-bottom', '5px solid'); // underline should be faster then bold font
                    }
                }, function () {
                    let curr_elem = $("." + cls[cls.length - 1]);
                    if (user_borders) {
                        curr_elem.css('border-bottom', '');
                        curr_elem.css('padding-bottom', '');
                        if (full_border)
                            curr_elem.css('border', '');
                    } else {
                        curr_elem.css('border-bottom', ''); // underline should be faster then bold font
                    }
                });
                x++;
            }
        );
    }
}

function extractUndesiredToJson() {
    let res = [];
    $('[id^="subseq_"]').each(function () {
        let enabled = $(this).children().find("[id^='enabled']")[0];
        if (enabled.checked) {
            let id = $(this).children().find("[id='validated']");
            let sequence = $(this).children().find("[name='sequence']");
            let error_prob = $(this).children().find("[name='error_prob']");
            let description = $(this).children().find("[name='description']");
            res.push({
                id: id.val(),
                sequence: sequence.val(),
                error_prob: error_prob.val(),
                enabled: enabled.checked,
                description: description.val()
            });
        }
    });
    return res;
}

function importUndesiredFromJson(json_in) {
    let container = $('#subseq-container');
    container.empty();
    let tmp = "";
    for (let id in json_in) {
        const elem = json_in[id];
        const sequence = elem['sequence'];
        const error_prob = elem['error_prob'];
        const description = elem['description'];
        tmp = "                    <div class=\"control\" id=\"subseq_" + id + "\">\n" +
            "                        <table>\n" +
            "                            <tr>\n" +
            "                                <td><input type=\"checkbox\"\n" +
            "                                           class=\"switch is-large is-rounded button-fill no-outline\"\n" +
            "                                           id=\"enabled" + id + "\" name=\"switchRoundedDefault\"\n" +
            "                                           aria-label=\"Enable Rule\"\n" +
            "                                           value=\"" + id + "\" checked/>\n" +
            "                                    <label class=\"no-outline\" for=\"enabled" + id + "\"></label>\n" +
            "                                </td>\n" +
            "                                <td style=\"width:50%\"><label class=\"form-group has-float-label\">\n" +
            "                                    <input class=\"input is-rounded is-grayable\" style=\"width:100%\" type=\"text\"\n" +
            "                                           name=\"sequence\"\n" +
            "                                           aria-label=\"Sequence\"\n" +
            "                                           id=\"sequence\" placeholder=\"\"\n" +
            "                                           value=\"" + sequence + "\" required>\n" +
            "                                    <span>Sequence</span></label></td>\n" +
            "                                <td style=\"width:15%\"><label class=\"form-group has-float-label\">\n" +
            "                                    <input class=\"input is-rounded is-grayable\" style=\"width:100%\" type=\"number\"\n" +
            "                                           id=\"error_prob\"\n" +
            "                                           aria-label=\"Error Probability\"\n" +
            "                                           name=\"error_prob\" placeholder=\"\"\n" +
            "                                           value=\"" + error_prob + "\"\n" +
            "                                           required min=\"0.0\" max=\"100.0\" step=\"0.01\">\n" +
            "                                    <span style=\"white-space: nowrap;\">Error Probability</span></label></td>\n" +
            "                                <td style=\"width:30%\"><label class=\"form-group has-float-label\">\n" +
            "                                    <input class=\"input is-rounded is-grayable\" style=\"width:100%\" type=\"text\"\n" +
            "                                           name=\"description\"\n" +
            "                                           aria-label=\"Description\"\n" +
            "                                           id=\"description\" placeholder=\"No Description\" size=\"30\"\n" +
            "                                           value=\"" + description + "\"\n" +
            "                                           readonly><span>Description</span></label></td>\n" +
            "                                <td><span class=\"\" style=\"white-space: nowrap;\"><label\n" +
            "                                        class=\"checkbox\">Validated: <input type=\"checkbox\"\n" +
            "                                                                           id=\"validated_" + id + "\"\n" +
            "                                                                           value=\"" + id + "\"\n" +
            "                                                                           aria-label=\"Validated\"\n" +
            "                                                                           disabled checked/></label></span></td>\n" +
            "                            </tr>\n" +
            "                        </table>\n" +
            "                    </div>";
        container.append(tmp);
    }
}


function round(value, decimals) {
    return Number(Math.round(value + 'e' + decimals) + 'e-' + decimals);
}

$(document).ready(function () {
    let seq = $("#sequence");
    let send_mail = $("#send_email");
    let do_max_expect = $('#do_max_expect');
    seq.keypress(function (e) {
        let chr = String.fromCharCode(e.which);
        let limitAlphabet = $('#limitedChars')[0].checked;
        if ("ACGTacgt".indexOf(chr) < 0 && limitAlphabet) {
            return false;
        }
        if (seq.val().length >= 1000) {
            send_mail.prop("checked", true);
            send_mail.prop("disabled", true);
        } else {
            send_mail.removeAttr("disabled");
        }
        if (seq.val().length >= 4000) {
            do_max_expect.prop("checked", false);
            do_max_expect.prop("disabled", true);
        } else {
            do_max_expect.prop("disabled", false);
        }
    });
    let add_mail = $("#emailadd");
    seq.bind("propertychange change click keyup input paste", function (e) {
        if (seq.val().length >= 4000) {
            do_max_expect.prop("checked", false);
            do_max_expect.prop("disabled", true);
            $('#limit_1').hide();
            $('#limit_2').show();
        } else {
            do_max_expect.prop("disabled", false);
            $('#limit_2').hide();
        }
        $('#temperature').prop('disabled', !do_max_expect.is(':checked'));
        if (seq.val().length >= 1000) {
            send_mail.prop("checked", true);
            send_mail.attr("disabled", true);
            if (user_id === "") {
                add_mail.show();
            }
            if(seq.val().length < 4000){
                $('#limit_1').show();
            }
        } else {
            send_mail.attr("disabled", false);
            add_mail.hide();
            add_mail.val("");
            $('#limit_1').hide();
        }
    });
    let submit_seq = $("#submit_sequence");
    submit_seq.submit(function (event) {
        event.preventDefault();
        queryServer(undefined);
    });
    $('#informationcontainer').hide();
    set_listener();
});

function set_listener(){
    $('[name="sequence"], [name = "Original DNA-Sequence"], [name^="mismatch_changed"]').each(function (e, elem) {
        $(elem).on("paste klick change keyup", function (f) {
            setTimeout(function(g){
                let data = $(elem).val();
                let data_len = data.length;
                let pos = $(elem)[0].selectionStart;
                $(elem).val(data.replace(/[^ACGT]/gi, "").toUpperCase());
                $(elem)[0].selectionStart = pos + ($(elem).val().length - data_len);
                $(elem)[0].selectionEnd = pos + ($(elem).val().length - data_len);
            });
        });
    });
    $("[name='error_prob'], [name='raw_error_rate']").each(function (e, elem) {
        $(elem).on("change", function (f) {
            let data = $(elem).val();
            $(elem).val(Math.max(0.0, Math.min(data, 100.0)));
        });
    });
    $('#temperature').on("change", function (f) {
       let data = $(this).val();
       $(this).val(Math.max(0.0, data));
    });
    let methods = [['#synthmeth', '#synthesis_sortable'], ['#seqmeth', '#sequencing_sortable'], ['#storagemeth', '#pcr_sortable'], ['#pcrmeth', '#pcr_sortable']];
    methods.forEach(function (meth) {
        $(meth[0]).bind('dbclick, keyup', function (e) {
            if(e.which === 13 || e.type === 'dbclick'){
                let clone = $(meth[0]+' :selected').clone(true).unbind();
                $(meth[1]).append(clone);
                if(meth[0] === '#storagemeth') {
                    let name = $(clone).text();
                    let mon = $('#mon').val();
                    $(clone).text(name + " (" + mon + " month(s))");
                    $(clone).data('multiplier', mon)
                }
                else if(meth[0] === '#pcrmeth'){
                    let name = $(clone).text();
                    let mon = $('#cyc').val();
                    $(clone).text(name + " (" + mon + " cycle(s))");
                    $(clone).data('multiplier', mon)
                }
            }
        });
    });
}

/* Example: download(collectSendData(2), 'mosla.json','application/json'); */
function download(text, name, type) {
    let file = new Blob([text], {type: type});
    let isIE = /*@cc_on!@*/false || !!document.documentMode;
    if (isIE) {
        window.navigator.msSaveOrOpenBlob(file, name);
    } else {
        let a = document.createElement('a');
        a.href = URL.createObjectURL(file);
        a.download = name;
        document.body.appendChild(a);
        a.style.display = 'none';
        a.click();
    }
}

function downloadImg(id, type) {
    let file = host + "api/getIMG?id=" + id + "&type=" + type;
    let isIE = /*@cc_on!@*/false || !!document.documentMode;
    if (isIE) {
        window.navigator.msSaveOrOpenBlob(file, name);
    } else {
        let a = document.createElement('a');
        a.href = file;
        a.download = name;
        document.body.appendChild(a);
        a.style.display = 'none';
        a.click();
    }
}

function handleFileChange(evt) {
    if (window.File && window.FileReader && window.FileList && window.Blob) {
        // Great success! All the File APIs are supported.
        let jseq = $("#sequence");
        let file = "";
        if (evt.type === "drop") {
            evt.stopPropagation();
            evt.preventDefault();
            file = evt.dataTransfer.files[0]
        } else {
            file = evt.target.files[0];
        }
        let reader = new FileReader();
        try {
            reader.readAsText(file);
        } catch (e) {
            return false;
        }
        reader.onload = function () {
            try {
                let text = reader.result;
                if (text.startsWith(">")) {
                    if (user_id === "") {
                        $("#emailadd").show();
                    }
                    //split into sequences and remove headlines
                    let sequences = text.split(">");
                    sequences.shift();
                    for (let i = 0; i < sequences.length; i++) {
                        sequences[i] = sequences[i].substring(sequences[i].indexOf("\n") + 1);
                        sequences[i] = sequences[i].replace("\n", "");
                    }
                    if (sequences.length === 1) {
                        jseq.val(sequences[0]);
                    } else if (sequences.length > 1) {
                        document.getElementById("send_email").checked = true;
                        document.getElementById("send_email").disabled = true;
                        document.getElementById("do_max_expect").checked = false;
                        $('#fasta_inf').show();
                        jseq.data("sequence_list", sequences);
                        jseq.val("Fasta file loaded. Your results will be send to your E-Mail");
                        //queryServer(undefined);
                    }
                } else {
                    loadSendData(JSON5.parse(text))
                }
            } catch (e) {
                jseq.val(reader.result.toUpperCase());
            }
        }
    } else {
        log('The File APIs are not fully supported in this browser.');
    }
    evt.target.removeEventListener('change', handleFileChange);
}

function upload() {
    let input = $(document.createElement("input"));
    input.attr("type", "file");
    // add onchange handler if you wish to get the file :)
    input.trigger("click"); // opening dialog
    input[0].addEventListener('change', handleFileChange, false);
}

function handleDragOver(evt) {
    try {
        evt.stopPropagation();
        evt.preventDefault();
        evt.dataTransfer.dropEffect = 'copy'; // Explicitly show this is a copy.
    } catch (e) {

    }
}

function loadSendData(dta) {
    $("#sequence").val(dta['sequence']);

    /* Select dropdown-positions for gc/kmer/homopolymer probabilities and fill window_sizes*/
    $('#kmer_window_size').val(dta['kmer_windowsize']);
    $('#gc_window_size').val(dta['gc_windowsize']);
    let gc_selection = $('#gc-dropdown option').filter(function () {
        return $(this).html() === dta['gc_name'];
    });
    let kmer_selection = $('#kmer-dropdown option').filter(function () {
        return $(this).html() === dta['kmer_name'];
    });
    let homopolymer_selection = $('#homopolymer-dropdown option').filter(function () {
        return $(this).html() === dta['homopolymer_name'];
    });
    [['gc', gc_selection], ['kmer', kmer_selection], ['homopolymer', homopolymer_selection]].forEach(function (method) {
        if (method[1].length > 0) {
            method[1].prop('selected', true)
        } else {
            let opt = new Option(dta[method[0]+'_name'] + " (CUSTOM)", dta[method[0]+'_name'], undefined, true);
            $('#gc-dropdown').append(opt);
            $('#'+method[0]+'-dropdown').append(opt);
            $('#'+method[0]+'-dropdown option:selected').data('jsonblob', dta[method[0]+'_error_prob']);
        }
    });

    /* Select or fill error methods (Sequencing, Synthesis, Storage, PCR) */
    let err_sim_order = dta['err_simulation_order'];
    let err_sim_lists = {'Synthesis': [], 'Sequencing': [], 'Storage': [], 'PCR': []};
    err_sim_lists['Synthesis'] = err_sim_order['Synthesis'];
    err_sim_lists['Sequencing'] = err_sim_order['Sequencing'];
    err_sim_order['Storage/PCR'].forEach(function (entry) {
       if(entry['conf']['type'] === 'storage'){
           err_sim_lists['Storage'].push(entry);
       }
       else if(entry['conf']['type'] === 'pcr'){
           err_sim_lists['PCR'].push(entry);
       }
    });
    if(err_sim_lists['Sequencing'].length > 1 || err_sim_lists['Synthesis'].length > 1 || err_sim_lists['Storage'].length > 1 || err_sim_lists['PCR'] > 1){
        /* Fill the advanced menu */
        document.getElementById("adv_exec").checked = true;
        $('#adv_err_settings').show();
        $('#classic_err_settings').hide();
        let meths = {'synthesis': ['#synthesis_sortable', 'Synthesis', '#synthmeth'],
                    'storage': ['#pcr_sortable', 'Storage', '#storagemeth'],
                    'pcr': ['#pcr_sortable', 'PCR', '#pcrmeth'],
                    'sequencing': ['#sequencing_sortable', 'Sequencing', '#seqmeth']};
        $('#synthesis_sortable').children().remove();
        $('#pcr_sortable').children().remove();
        $('#sequencing_sortable').children().remove();
        let tmp = err_sim_order['Synthesis'].concat(err_sim_order['Storage/PCR']).concat(err_sim_order['Sequencing']);
        tmp.forEach(function (err_meth) {
            let method = meths[err_meth['conf']['type']];
            let meth_selection;
            let tmp_selection = $(method[2] + ' option').filter(function () {
                if($(this)[0]['value'] === err_meth['id']){
                    return true;
                }
                if($(this).data('tmp_id') != undefined){
                    return $(this).data('tmp_id') === err_meth['id'];
                }
                return false;
            });
            if (JSON.stringify($(tmp_selection).data('err_data')) === JSON.stringify(err_meth['conf']['err_data']) && JSON.stringify($(tmp_selection).data('err_attributes')) === JSON.stringify(err_meth['conf']['err_attributes'])) {
                meth_selection = tmp_selection;
            }
            let sel;
            if (meth_selection !== undefined) {
                sel = $(meth_selection).clone(true).unbind();
                $(method[0]).append(sel);
            } else {
                let opt = new Option(err_meth['name'] + " (CUSTOM)", err_meth['name'], undefined, true);
                $(method[0]).append(opt);
                sel = $(method[0] + ' option:selected');
                sel.data('err_attributes', err_meth['conf']['err_attributes']);
                sel.data('err_data', err_meth['conf']['err_data']);
                sel.data('type', err_meth['conf']['type']);
                sel.data('tmp_id', err_meth['id']);
                $(method[2]).append(sel.clone(true).unbind())
            }
            if (err_meth['conf']['type'] === 'storage'){
                let name = $(sel).text();
                $(sel).text(name + " (" + err_meth['cycles'] + " month(s))");
                $(sel).data('multiplier', err_meth['cycles']);
            }
            else if (err_meth['conf']['type'] === 'pcr'){
                let name = $(sel).text();
                $(sel).text(name + " (" + err_meth['cycles'] + " cycle(s))");
                $(sel).data('multiplier', err_meth['cycles']);
            }
        });
        initListsDnD();
    }
    else {
        /* Fill the dropdowns */
        document.getElementById("adv_exec").checked = false;
        $('#adv_err_settings').hide();
        $('#classic_err_settings').show();
        let meths = [['#classic_synthmeth', 'Synthesis'], ['#classic_seqmeth', 'Sequencing'], ['#classic_pcrmeth', 'PCR'], ['#classic_storagemeth', 'Storage']];
        meths.forEach(function (method) {
            $(method[0]).val(0).prop('disabled', dta['use_error_probs']);
            if(err_sim_lists[method[1]].length === 0){
                let meth_selection = $(method[0] + ' option').filter(function () {
                    return $(this).text() === 'None';
                });
                meth_selection.prop('selected', true);
            }
            else {
                let meth_id = err_sim_lists[method[1]][0]['id'];
                let meth_selection = $(method[0] + ' option').filter(function () {
                    return $(this).val() === meth_id;
                });
                if (meth_selection.length > 0) {
                    meth_selection.prop('selected', true);
                } else {
                    let opt = new Option(err_sim_lists[method[1]][0]['name'] + "(CUSTOM)", err_sim_lists[method[1]]['name'], undefined, true);
                    $(method[0]).append(opt);
                    let sel = $(method[0] + ' option:selected');
                    sel.data('err_attributes', err_sim_lists[method[1]][0]['conf']['err_attributes']);
                    sel.data('err_data', err_sim_lists[method[1]][0]['conf']['err_data']);
                    sel.data('type', err_sim_lists[method[1]][0]['conf']['type']);
                }
                if (method[1] === 'PCR') {
                    $('#cycles').val(err_sim_lists[method[1]][0]['cycles'])
                }
                if (method[1] === 'Storage') {
                    $('#months').val(err_sim_lists[method[1]][0]['cycles'])
                }
            }
        });
    }

    /* Fill other fields */
    $("#seed").val(dta['random_seed']);
    $("#used_seed").text(dta['random_seed']);
    $('#calcprobs').prop("checked", dta['use_error_probs']);
    $('#limitedChars').prop("checked", dta['acgt_only']);
    $('#do_max_expect').prop("checked", dta['do_max_expect']);
    importUndesiredFromJson(dta['enabledUndesiredSeqs']);
}

function collectSendData(space) {
    if (space === undefined)
        space = 0;
    let sequence = $("#sequence").val().toUpperCase();

    let gc_dropdown_select = $('#gc-dropdown option:selected');
    let gc_error_prob = gc_dropdown_select.data('jsonblob');
    if (typeof (gc_error_prob) === "string")
        gc_error_prob = JSON5.parse(gc_error_prob);

    let homopolymer_dropdown_select = $('#homopolymer-dropdown option:selected');
    let homopolymer_error_prob = homopolymer_dropdown_select.data('jsonblob');
    if (typeof (homopolymer_error_prob) === "string")
        homopolymer_error_prob = JSON5.parse(homopolymer_error_prob);

    let kmer_dropdown_select = $('#kmer-dropdown option:selected');
    let kmer_error_prob = kmer_dropdown_select.data('jsonblob');
    if (typeof (kmer_error_prob) === "string")
        kmer_error_prob = JSON5.parse(kmer_error_prob);

    let adv_meth = $("#adv_exec");
    let seq_meth, synth_meth, storage_meth, pcr_meth;
    let exec_res = {};
    if(adv_meth.prop("checked")){
        /* collect all error simulation elements in correct execution order */
        let exec_order = $('#seqmeth1').children();
        exec_order.each(function (id, o_group) {
            let tmp = [];
            $(o_group).children().each(function (o_id, meth) {
                let jmeth = $(meth);
                tmp.push({
                    name: jmeth.text(),
                    id: jmeth.val(),
                    cycles: jmeth.data('multiplier'),
                    conf: {
                        err_data: jmeth.data('err_data'),
                        err_attributes: jmeth.data('err_attributes'),
                        type: jmeth.data('type')
                    }
                });
            });
            exec_res[o_group.label] = tmp;
        });
    }
    else{
        exec_res['Sequencing'] = [];
        exec_res['Synthesis'] = [];
        exec_res['Storage/PCR'] = [];
        seq_meth = $("#classic_seqmeth option:selected");
        synth_meth = $("#classic_synthmeth option:selected");
        storage_meth = $("#classic_storagemeth option:selected");
        pcr_meth = $("#classic_pcrmeth option:selected");
        [[seq_meth, 'Sequencing'], [synth_meth, 'Synthesis'], [storage_meth, 'Storage/PCR'], [pcr_meth, 'Storage/PCR']].forEach(function (meth) {
            let cycles;
            if (meth[0].data('type') === 'storage') {
                cycles = $('#months').val()
            } else if (meth[0].data('type') === 'pcr') {
                cycles = $('#cycles').val()
            } else {
                cycles = 1;
            }
            exec_res[meth[1]].push({
                name: meth[0].text(),
                id: meth[0].val(),
                cycles: cycles,
                conf: {
                    err_data: meth[0].data('err_data'),
                    err_attributes: meth[0].data('err_attributes'),
                    type: meth[0].data('type')
                }
            });
        })
    }

    let email = "";
    let send_email = $('#send_email').is(':checked');
    if (user_id === "" && send_email) {
        let email_add = $("#emailadd").val();
        if (email_add) {
            email = email_add;
        } else {
            alert("Please enter your email or deactivate send by mail!");
            return
        }
    }
    return JSON.stringify({
        sequence: sequence,
        key: apikey,
        enabledUndesiredSeqs: extractUndesiredToJson(),
        kmer_windowsize: $('#kmer_window_size').val(),
        gc_windowsize: $('#gc_window_size').val(),
        gc_name: gc_dropdown_select.text(),
        //error_prob: gc_error_prob,
        gc_error_prob: gc_error_prob,
        homopolymer_error_prob: homopolymer_error_prob,
        homopolymer_name: homopolymer_dropdown_select.text(),
        kmer_error_prob: kmer_error_prob,
        kmer_name: kmer_dropdown_select.text(),
        err_simulation_order: exec_res,
        use_error_probs: $('#calcprobs').is(":checked"),
        acgt_only: $('#limitedChars').is(":checked"),
        random_seed: $('#seed').val(),
        do_max_expect: $('#do_max_expect').is(":checked"),
        temperature: $('#temperature').val(),
        send_mail: send_email,
        email: email,
        asHTML: true
    }, undefined, space);
}

function collectSendFastQ(modified) {
    if (modified === false) {
        return '@Your Moslasequence at ' + document.getElementById("link_to_share").innerText + '\n' + document.getElementById("overall").innerText + '\n+\n' + $('#overall').data('fastq');
    } else {
        let sequence = document.getElementById("mod_seq").innerText.split(" ").join("");
        return '@Your Moslasequence at ' + document.getElementById("link_to_share").innerText + '\n' + sequence + '\n+\n' + $('#mod_seq').data('fastq');
    }
}

function queryServer(uuid) {
    let jseq = $("#sequence");
    let submit_seq_btn = $('#submit_seq_btn');
    let sequence = jseq.val().toUpperCase();
    let homopolymer = $('#homopolymer');
    let gccontent = $('#gccontent');
    let sequences = $('#subsequences');
    let kmer = $('#kmer');
    let overall = $('#overall');
    let seq_seq = $('#seq_seq');
    let synth_seq = $('#synth_seq');
    let mod_seq = $('#mod_seq');
    let fasta = false;
    let dot_seq = $('#dot_seq');
    if (jseq.data("sequence_list")) {
        fasta = true;
    }

    let endpoints = {
        "gccontent": gccontent,
        "homopolymer": homopolymer,
        "kmer": kmer,
        "subsequences": sequences,
        "all": overall,
        "sequencing": seq_seq,
        "synthesis": synth_seq,
        "modify": mod_seq,
        "dot_seq": dot_seq,
    };

    let send_data = undefined;
    if (uuid === undefined) {
        send_data = collectSendData();
    } else {
        send_data = JSON.stringify(
            {
                key: apikey,
                uuid: uuid
            });
    }
    if (send_data === undefined) {
        return
    }
    let res = $('#results');
    let resultsbymail = $('#resultsbymail');
    let mode = "all";
    if (fasta && jseq.val() === "Fasta file loaded. Your results will be send to your E-Mail") {
        mode = "fasta_all";
        let tmp_data = JSON.parse(send_data);
        delete tmp_data["sequence"];
        tmp_data["sequence_list"] = jseq.data("sequence_list");
        send_data = JSON.stringify(tmp_data);
    }
    $.post({
        url: host + "api/" + mode,
        contentType: 'application/json;charset=UTF-8',
        dataType: 'json',
        data: send_data,
        async: true,
        beforeSend: function () {
            submit_seq_btn.addClass('is-loading');
            for (let error_source in endpoints) {
                endpoints[error_source].html("");
            }
            res.css('display', 'none');
            resultsbymail.css('display', 'none');
        },
        success: function (data) {
            if (sequence !== "" && sequence in data)
                data = data[sequence];
            let recv_uuid = data['uuid'];
            if (recv_uuid !== undefined) {
                changeurl("query_sequence?uuid=" + recv_uuid);
                const shr_txt = $("#link_to_share");
                shr_txt.text(window.location.href);
            }
            if (data['did_succeed'] !== false && data['result_by_mail'] !== true) {
                if (uuid !== undefined)
                    loadSendData(data['query']);
                data = data['res'];
                if (uuid !== undefined)
                    data = data[Object.keys(data)[0]];
                dot_seq.data('id', data['maxexpectid']);
                overall.data('fastq', data['fastqOr']);
                mod_seq.data('fastq', data['fastqMod']);
                $("#used_seed").text(data['seed']);
                for (let error_source in data) {
                    if (error_source !== 'fastqOr' && error_source !== 'fastqMod' && error_source !== 'seed' && error_source !== 'maxexpectid')
                        endpoints[error_source].html(data[error_source]);
                    if (error_source === "dot_seq")
                        if (data[error_source] === "<pre></pre>")
                            $('.maxExpect').hide();
                        else if (data[error_source].startsWith("<pre>Error")) {
                            $('.maxExpect').show();
                            $(".downloadIMG").attr("disabled", true);
                        } else {
                            $('.maxExpect').show();
                            $(".downloadIMG").attr("disabled", false);
                        }
                }
                makeHoverGroups();
                res.css('display', '');
                $('html, body').animate({scrollTop: res.offset().top}, 500);
            }


            let element = document.getElementById('mod_seq');
            set_mod_seq_inf(element.innerText);
            if (data['result_by_mail'] === true) {
                //TODO show info that the result will be send via mail
                resultsbymail.css('display', 'initial');
            }
            submit_seq_btn.removeClass('is-loading');
            if (fasta && jseq.val() === "Fasta file loaded. Your results will be send to your E-Mail"){
                jseq.val("");
                document.getElementById("send_email").checked = false;
                document.getElementById("send_email").disabled = false;
                $('#fasta_inf').hide();
            }
        },
        fail: function (data) {
            console.log(data);
            submit_seq_btn.removeClass('is-loading');
        }
        ,
        error: function (jqXHR, textStatus, errorThrown) {
            console.log("Error, status = " + textStatus + ", " + "error thrown: " + errorThrown);
            if (errorThrown === "NOT FOUND")
                errorThrown ="No result found for given UUID - The result might have expired or has been removed.";
            showWarn(errorThrown, 'warning',404);
            submit_seq_btn.removeClass('is-loading');
        }
    });
    jseq.removeData("sequence_list");
}

const percentColors = [
    {pct: 0.0, color: {r: 0xff, g: 0x00, b: 0}},
    {pct: 0.5, color: {r: 0xff, g: 0xff, b: 0}},
    {pct: 1.0, color: {r: 0x00, g: 0xff, b: 0}}];

var getColorForPercentage = function (pct) {
    pct = 1.0 - pct;
    for (var i = 1; i < percentColors.length - 1; i++) {
        if (pct < percentColors[i].pct) {
            break;
        }
    }
    const lower = percentColors[i - 1];
    const upper = percentColors[i];
    const range = upper.pct - lower.pct;
    const rangePct = (pct - lower.pct) / range;
    const pctLower = 1 - rangePct;
    const pctUpper = rangePct;
    const color = {
        r: Math.floor(lower.color.r * pctLower + upper.color.r * pctUpper),
        g: Math.floor(lower.color.g * pctLower + upper.color.g * pctUpper),
        b: Math.floor(lower.color.b * pctLower + upper.color.b * pctUpper)
    };
    return 'rgb(' + [color.r, color.g, color.b].join(',') + ')';
    // or output as hex if preferred
};

function updateSynthDropdown(host_uri, api_key, type, post_success_callback) {
    $.post({
        url: host_uri + "api/get_error_probs",
        dataType: 'json',
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify({
            key: api_key,
            type: type
        }),
        async: true,
        beforeSend: function (xhr) {
            if (xhr && xhr.overrideMimeType) {
                xhr.overrideMimeType('application/json;charset=utf-8');
            }
        },
        success: function (data) {
            let methods = [['synth', '#synthmeth'], ['synth', '#classic_synthmeth'], ['seq', '#seqmeth'], ['seq', '#classic_seqmeth'], ['pcr', '#classic_pcrmeth'], ['pcr', '#pcrmeth'], ['storage', '#classic_storagemeth'], ['storage', '#storagemeth']];
            methods.forEach(function (method) {
                let el = $(method[1]);
                el.empty();
                $.each(data[method[0]], function (name) {
                    let elem = data[method[0]][name];
                    let optgroup = $("<optgroup id='"+ method + "_" + name.replace(" ","_") + "' label='" + name + "'></optgroup>");
                    optgroup.appendTo(el);
                    $.each(elem, function (inner_id) {
                        let id = elem[inner_id]['id'];
                        let id_name = "" + method + "_" + name.replace(" ","_") + "_" + id;
                        optgroup.append($("<option></option>").attr('value', id).attr('id', id_name).text(elem[inner_id]['name']).data('err_attributes', elem[inner_id]['err_attributes']).data('err_data', elem[inner_id]['err_data']).data('type', elem[inner_id]['type']));
                    });
                })
            });

            // make content draggable
            let trash = $('#trash')[0];
            [$('#synthmeth'), $('#seqmeth'), $('#pcrmeth'), $('#storagemeth')].forEach(function (elem) {
                elem.children().each(function (x) {
                    sorts.push(Sortable.create(elem.children()[x], {
                        group: {name: 'a', pull: 'clone', put: false}, sort: false, animation: 100,
                        onEnd: function (evt) {
                            if (evt.to === trash) {
                                evt.to.children[evt.newIndex].remove();
                            }
                        }
                    }));
                });
            });

            initListsDnD();
            if (post_success_callback !== undefined)
                post_success_callback(data);
        },
        fail: function (data) {
            showWarn(data, 'warning', 444);
        },
        error: function (jqXHR, textStatus, errorThrown) {
            console.log("Error, status = " + textStatus + ", " + "error thrown: " + errorThrown);
            showWarn(errorThrown, 'warning',400);
            submit_seq_btn.removeClass('is-loading');
        }
    });
}


function changeurl(new_url) {
    window.history.pushState("data", "Title", new_url);
    //document.title = url;
}


let dropZone = document.getElementById('main-body');
dropZone.addEventListener('dragover', handleDragOver, false);
dropZone.addEventListener('drop', handleFileChange, false);

function set_mod_seq_inf(sel_seq) {
    let sel_pos = getSelectionCharacterOffsetWithin(document.getElementById("mod_seq"));
    let sel_gc_con = get_gc_con(sel_seq);
    let sel_tm = calc_tm(sel_seq);
    if (isNaN(sel_gc_con)){
        sel_gc_con = 0;
    }
    if (sel_tm === -1) {
        document.getElementById("mod_seq_inf").innerHTML = "GC-Content: " + sel_gc_con + "% Tm: Select at least 6 bases. Start-Pos: " + sel_pos.start + " End-Pos: " + sel_pos.end;
    } else {
        document.getElementById("mod_seq_inf").innerHTML = "GC-Content: " + sel_gc_con + "% Tm: " + sel_tm + "°C Start-Pos: " + sel_pos.start + " End-Pos: " + sel_pos.end;
    }


}

function getSelectionCharacterOffsetWithin(element) {
    let start = 0;
    let end = 0;
    let doc = element.ownerDocument || element.document;
    let win = doc.defaultView || doc.parentWindow;
    let sel;
    if (typeof win.getSelection != "undefined") {
        sel = win.getSelection();
        if (sel.rangeCount > 0) {
            let range = win.getSelection().getRangeAt(0);
            let preCaretRange = range.cloneRange();
            preCaretRange.selectNodeContents(element);
            preCaretRange.setEnd(range.startContainer, range.startOffset);
            start = preCaretRange.toString().length;
            preCaretRange.setEnd(range.endContainer, range.endOffset);
            end = preCaretRange.toString().length;
        }
    } else if ((sel = doc.selection) && sel.type != "Control") {
        let textRange = sel.createRange();
        let preCaretTextRange = doc.body.createTextRange();
        preCaretTextRange.moveToElementText(element);
        preCaretTextRange.setEndPoint("EndToStart", textRange);
        start = preCaretTextRange.text.length;
        preCaretTextRange.setEndPoint("EndToEnd", textRange);
        end = preCaretTextRange.text.length;
    }
    return {start: start, end: end};
}

function get_gc_con(sel_seq) {
    let gc_con = ((count_char(sel_seq, 'G') + count_char(sel_seq, 'C')) / count_all(sel_seq)) * 100;
    return Math.round(gc_con * 100) / 100;
}

function count_char(sel_seq, char) {
    let count = 0;
    for (let i = 0; i < sel_seq.length; i += 1) {
        if (sel_seq[i] === char) {
            count += 1;
        }
    }
    return count;
}

function count_all(sel_seq) {
    let count = 0;
    for (let i = 0; i < sel_seq.length; i += 1) {
        let tmp = sel_seq[i];
        if (tmp === 'A' || tmp === 'T' || tmp === 'C' || tmp === 'G') {
            count += 1;
        }
    }
    return count;
}


function updateUserId(host_uri, u_id, callback) {
    if (callback === undefined)
        callback = function f() {
        };
    let new_email = $('#user_email_' + u_id).val();
    let validated = $('#validated_' + u_id).is(":checked");
    let is_admin = $('#isadmin_' + u_id).is(":checked");
    $.post({
        url: host_uri + "manage_users",
        dataType: 'json',
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify({
            do_update: true,
            user_id: u_id,
            new_email: new_email,
            validated: validated,
            is_admin: is_admin
        }),
        async: true,
        beforeSend: function (xhr) {
            if (xhr && xhr.overrideMimeType) {
                xhr.overrideMimeType('application/json;charset=utf-8');
            }
        },
        success: function (data) {
            $('#update-user_' + u_id).removeClass('is-loading');
            if (data['did_succeed'] === true)
                callback();
        },
        fail: function (data) {
            $('#update-user_' + u_id).removeClass('is-loading');
            showWarn(data, 'warning', u_id);
        }
    });
}

function deleteUserId(host_uri, u_id, callback) {
    if (callback === undefined)
        callback = function f() {
        };
    $.post({
        url: host_uri + "manage_users",
        dataType: 'json',
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify({
            do_delete: true,
            user_id: u_id
        }),
        async: true,
        beforeSend: function (xhr) {
            if (xhr && xhr.overrideMimeType) {
                xhr.overrideMimeType('application/json;charset=utf-8');
            }
        },
        success: function (data) {
            $('#delete-user_' + u_id).removeClass('is-loading');
            if (data['did_succeed'] === true)
                callback();
        },
        fail: function (data) {
            $('#delete-user_' + u_id).removeClass('is-loading');
            showWarn(data, 'warning', u_id);
        }
    });
}

/**
 * Tm_calculation
 *
 *
 *
 *
 *
 */

let TmSettings = {
    Ct: 250e-9,// DNA strand concentration
    Na: 50e-3,// Na+/K+ ion concentration. Default taken from Primer3
    Mg: 0,    // divalent salt concentration default taken from Primer3Web 2.3.6
    dNTP: 0     // dNTP (denucleotide tri phosphate) default taken from Primer3Web 2.3.6
};

let dS = {},
    dH = {},
    init_GC_dH = 0.1 * 1000,
    init_GC_dS = -2.8,
    init_AT_dH = 2.3 * 1000,
    init_AT_dS = 4.1,
    sym_dS = -1.4,
    /**
     * molar gas constant
     * R 8.314472 J mol-1 K-1
     * Divided by 4.184 J / calorie for units:
     * cal mol-1 K-1
     */
    R = 1.9872;


function calc_tm(sel_seq){
    let tm = 0;
    sel_seq = sel_seq.replace(/ /g, "");
    let seq_len = sel_seq.length;
    if(seq_len < 6){
        return -1;
    }
    else if(seq_len < 14){
        tm = (count_char(sel_seq, 'A') + count_char(sel_seq, 'T')) * 2 + (count_char(sel_seq, 'G') + count_char(sel_seq, 'C')) * 4;
    }
    else if(14 <= seq_len) {
        init();
        let self_comp = is_self_comp(sel_seq);
        let dS_sum = calc_dS(sel_seq, self_comp);
        let na_corr = TmSettings.Na + divalendToMonovalentCorrection(TmSettings.Mg, TmSettings.dNTP);
        let salt_corr = (seq_len - 1) * 0.368 * Math.log(na_corr);
        let dH_sum = calc_dH(sel_seq);
        let h = is_self_comp ? 1.0 : 0.25;
        tm = dH_sum / (dS_sum + salt_corr + R * Math.log(TmSettings.Ct * h)) - 273.15;
    }
    return Math.round(tm * 100) / 100;
}

function init() {
    h('AA', -7.9, -22.2);
    h('AT', -7.2, -20.4);
    h('TA', -7.2, -21.3);
    h('CA', -8.5, -22.7);
    h('GT', -8.4, -22.4);
    h('CT', -7.8, -21.0);
    h('GA', -8.2, -22.2);
    h('CG', -10.6, -27.2);
    h('GC', -9.8, -24.4);
    h('GG', -8.0, -19.9);
}

function h(seq, dH_val, dS_val) {
    let rev = reverse_seq(get_comp_seq(seq));
    dH[seq] = dH[rev] = dH_val * 1000;
    dS[seq] = dS[rev] = dS_val;
}

function get_comp_base(base) {
    if (base === 'A') return 'T';
    if (base === 'T') return 'A';
    if (base === 'C') return 'G';
    if (base === 'G') return 'C';
}

function get_comp_seq(seq) {
    let tmp_seq = [];
    for (let i = 0; i < seq.length; i++) {
        tmp_seq.push(get_comp_base(seq.charAt(i)));
    }
    return tmp_seq.join("");
}

function reverse_seq(seq) {
    return seq.split("").reverse().join("");
}

function is_self_comp(seq) {
    let comp_seq = get_comp_seq(seq);
    for (let i = 0; i < seq.length; i++) {
        if (seq[i] !== comp_seq[seq.length - i]) {
            return false;
        }
    }
    return true;
}

function divalendToMonovalentCorrection(divalent, monovalent) {
    return 12.0 / Math.sqrt(10) * Math.sqrt(Math.max(0, divalent - monovalent));
}

function calc_dS(seq, is_self_comp) {
    let first = seq[0];
    let tmp_dS = first === 'A' || first === 'T' ? init_AT_dS : init_GC_dS;
    for (let i = 0; i < seq.length - 1; ++i) {
        tmp_dS += dS[seq.substr(i, 2)];
    }
    let last = seq[seq.length - 1];
    tmp_dS += last === 'A' || last === 'T' ? init_AT_dS : init_GC_dS;
    if (is_self_comp) {
        tmp_dS += sym_dS;
    }
    return tmp_dS;
}

function calc_dH(seq) {
    let first = seq[0];
    let tmp_dH = first === 'A' || first === 'T' ? init_AT_dH : init_GC_dH;
    for (let i = 0; i < seq.length - 1; ++i) {
        tmp_dH += dH[seq.substr(i, 2)];
    }
    let last = seq[seq.length - 1];
    tmp_dH += last === 'A' || last === 'T' ? init_AT_dH : init_GC_dH;
    return tmp_dH;
}


function initListsDnD() {
    for (let x in sorts) {
        sorts[x].destroy();
    }
    sorts = [];
    let trash = $('#trash')[0];

    $('#seqmeth1').children().each(function (elem) {
        sorts.push(Sortable.create($('#seqmeth1').children()[elem], {
            group: {name: 'a', pull: true, put: true}, sort: true, animation: 100, scroll: false,
            onEnd: function (evt) {
                if (evt.to === trash) {
                    evt.to.children[evt.newIndex].remove();
                }
            }
        }));
    });

    [$('#synthmeth'), $('#seqmeth'), $('#pcrmeth'), $('#storagemeth')].forEach(function (elem) {
        elem.children().each(function (x) {
            sorts.push(Sortable.create(elem.children()[x], {
                group: {name: 'a', pull: 'clone', put: false}, sort: false, animation: 100,scroll: false,
                onEnd: function (evt) {
                    if (evt.to === trash) {
                        evt.to.children[evt.newIndex].remove();
                    }
                }
            }));
        });
    });
    sorts.push(Sortable.create(trash, {group: {name: 'a', put: true, pull: true}, sort: true}));
}

function showWarn(text, level, warn_id) {
    if (level === undefined)
        level = "warning";
    if (warn_id === undefined)
        warn_id = Math.floor((Math.random() * 10000) + 1);
    let content = "<article class=\"message is-" + level + "\"  id='warning-"+ warn_id + "\'>\n" +
    "<div class=\"message-header\">\n" +
    "<p>Warning</p>\n" +
    "<button class=\"delete\" aria-label=\"delete\" onclick='hideWarn(\"warning-"+ warn_id + "\")'></button>\n" +
    "</div>\n" +
    "<div class=\"message-body\">\n" +
    text + "\n" +
    "</div>\n" +
    "</article>";
    $('#error-container').append(content);
}

function hideWarn(warnId) {
    let elem = $('#' + warnId);
    elem.fadeOut(300, function() { $(this).remove(); })
}

function deleteResult(result_uuid, callback, delete_all) {
    if (delete_all === undefined)
        delete_all = false;
    if (callback === undefined)
        callback = function f() {
        };
    $.post({
        url: host + "remove_result",
        dataType: 'json',
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify({
            do_delete: true,
            uuid: result_uuid,
            delete_all: delete_all
        }),
        async: true,
        beforeSend: function (xhr) {
            if (xhr && xhr.overrideMimeType) {
                xhr.overrideMimeType('application/json;charset=utf-8');
            }
        },
        success: function (data) {
            $('#delete-res_' + result_uuid).removeClass('is-loading');
            if (data['did_succeed'] === true)
                callback();
        },
        fail: function (data) {
            $('#delete-res_' + result_uuid).removeClass('is-loading');
            console.log(data)
        }
    });
}

function getNextHistory(showId) {
        if (showId === undefined)
            showId = false;
        current_history_offset += 50;
        let next_btn = $('#next_history_btn');
        $.get({
        url: host + "history?offset=" + current_history_offset,
        contentType: 'application/json;charset=UTF-8',
        async: true,
        success: function (data) {
            next_btn.removeClass('is-loading');
            if (data.length < 50) {
                next_btn.addClass('disabled').prop('disabled', 'disabled');
            }
            for (let i in data) {
                var date = new Date(parseFloat(data[i][2]));
                let curr_elem = "<div class=\"column is-full\" id=\"prev_res_" + data[i][0] + "\">\n" +
                    "                                <div class=\"columns is-full\">\n" +
                    "                                    <div class=\"column is-one-third is-full-mobile\">\n" +
                    "                                        <a href=\"" + host + "?uuid=" + data[i][0] + "\">" + data[i][0] + "</a>\n" +
                    "                                    </div>\n" +
                    "                                    <div class=\"column is-two-sixt is-full-mobile\">\n" +
                    "                                        <label class=\"form-group has-float-label\">\n" +
                    "                                            <input style=\"width:100%\" class=\"input is-rounded\" type=\"text\"\n" +
                    "                                                   id=\"timeout_" + data[i][0] + "\" name=\"description\" disabled=\"\"\n" +
                    "                                                   placeholder=\"Time-till-expiration\"\n" +
                    "                                                   value=\"" + date.customFormat('#DDD# #MMM# #DD# #hhhh#:#mm#:#ss# #YYYY#') + "\">\n" +
                    "                                            <span style=\"white-space: nowrap;\">Valid until</span>\n" +
                    "                                        </label>\n" +
                    "                                    </div>\n";
                if (data[i][1] !== null && showId) {
                    curr_elem += "                                    <div class=\"column is-one-sixt is-full-mobile\">\n" +
                        "                                        <label class=\"form-group has-float-label\">\n" +
                        "                                            <input style=\"width:100%\" class=\"input is-rounded\" type=\"text\"\n" +
                        "                                                   id=\"user_id_{{ p_res[0] }}\" name=\"description\" disabled=\"\"\n" +
                        "                                                   placeholder=\"Owner ID\"\n" +
                        "                                                   value=\"" + data[i][1] + "\">\n" +
                        "                                            <span style=\"white-space: nowrap;\">Owner ID</span>\n" +
                        "                                        </label>\n" +
                        "                                    </div>\n";
                }
                curr_elem += "                                    <div class=\"column is-one-sixt is-full-mobile\">\n" +
                    "                                        <input class=\"button is-block button-fill\" type=\"button\"\n" +
                    "                                               id=\"delete-res_{{ p_res[0] }}\"\n" +
                    "                                               name=\"delete-res_{{ p_res[0] }}\"\n" +
                    "                                               onclick=\"deleteResult('" + data[i][0] + "');\n" +
                    "                                                       $('#prev_res_" + data[i][0] + "').remove();return false;\"\n" +
                    "                                               data-balloon=\"Delete Result\"\n" +
                    "                                               data-balloon-pos=\"up\" value=\"Delete\"/>\n" +
                    "                                    </div>\n" +
                    "                                </div>\n" +
                    "                            </div>";
                $('#uuid_res').append(curr_elem)
            }

        },
        fail: function (data) {
            $('#delete-res_' + result_uuid).removeClass('is-loading');
            console.log(data)
        }
    });
}
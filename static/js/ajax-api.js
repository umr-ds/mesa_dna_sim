let apikey = "";
let host = "";

function setApikey(hst, key) {
    apikey = key;
    host = hst;
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
        //$('#text_lettering').css('height', '80%');
    }
    if (all_groups.length > 1000 && !force) {
        all_groups.unbind();
    } else {
        all_groups.each(function () {

                let cls = $(this).attr('class').split(" ");
                let tmp = $("." + cls[cls.length - 1]);
                //user_borders = !(cls[cls.length - 1].startsWith("g_A") || cls[cls.length - 1].startsWith("g_C") || cls[cls.length - 1].startsWith("g_T") || cls[cls.length - 1].startsWith("g_G"));
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
                        //curr_elem.css('overflow-y', 'hidden');
                    } else {
                        curr_elem.css('border-bottom', '5px solid'); // underline should be faster then bold font
                        //curr_elem.css('overflow-y','initial')
                        //curr_elem.css('font-weight', "bold");
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
                        //curr_elem.css('font-weight', "normal");
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
    let container = $('#subseq_container');
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
            "                                    <span><nobr>Error Probability</nobr></span></label></td>\n" +
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
    });
    seq.bind("propertychange change click keyup input paste", function (e) {
        if (seq.val().length >= 1000) {
            send_mail.prop("checked", true);
            send_mail.attr("disabled", true);
        } else {
            send_mail.attr("disabled", false);
        }
    });
    /*seq.keyup(function () {
        var start = this.selectionStart,
            end = this.selectionEnd;
        $(this).val($(this).val().toUpperCase());
        this.setSelectionRange(start, end);
    });*/
    let submit_seq = $("#submit_sequence");
    submit_seq.submit(function (event) {
        event.preventDefault();
        queryServer(undefined);
    });
});

/* Example: download(collectSendData(2), 'mosla.json','application/json'); */
function download(text, name, type) {
    var file = new Blob([text], {type: type});
    var isIE = /*@cc_on!@*/false || !!document.documentMode;
    if (isIE) {
        window.navigator.msSaveOrOpenBlob(file, name);
    } else {
        var a = document.createElement('a');
        a.href = URL.createObjectURL(file);
        a.download = name;
        document.body.appendChild(a);
        a.style.display = 'none';
        a.click();
    }
}

function handleFileChange(evt) {
    if (window.File && window.FileReader && window.FileList && window.Blob) {
        // Great success! All the File APIs are supported.
        let file = "";
        if (evt.type === "drop") {
            evt.stopPropagation();
            evt.preventDefault();
            file = evt.dataTransfer.files[0]
        } else {
            file = evt.target.files[0];
        }
        let reader = new FileReader();
        reader.readAsText(file);
        reader.onload = () => {
            try {
                loadSendData(JSON5.parse(reader.result))
            } catch (e) {
                $("#sequence").val(reader.result.toUpperCase());
            }
        }
    } else {
        alert('The File APIs are not fully supported in this browser.');
    }
    evt.target.removeEventListener('change', handleFileChange);
}

function uploadConf() {
    let input = $(document.createElement("input"));
    input.attr("type", "file");
    // add onchange handler if you wish to get the file :)
    input.trigger("click"); // opening dialog
    input[0].addEventListener('change', handleFileChange, false);
}

function handleDragOver(evt) {
    evt.stopPropagation();
    evt.preventDefault();
    evt.dataTransfer.dropEffect = 'copy'; // Explicitly show this is a copy.
}

function loadSendData(dta) {
    $("#sequence").val(dta['sequence']);

    let seq = $('#seqmeth');
    let synth = $('#synthmeth');
    $('#kmer_window_size').val(dta['kmer_windowsize']);
    $('#gc_window_size').val(dta['gc_windowsize']);

    // find dropdown-pos to select...
    /* GC */
    let gc_selection = $('#gc-dropdown option').filter(function () {
        return $(this).html() == dta['gc_name'];
    });
    if (gc_selection.length > 0) {
        gc_selection.prop('selected', true)
    } else {
        let opt = new Option(dta['gc_name'] + " (CUSTOM)", dta['gc_name'], undefined, true);
        //opt.data('jsonblob',dta['gc_error_prob']);
        $('#gc-dropdown').append(opt);
        //opt.prop('selected', true);
        $('#gc-dropdown option:selected').data('jsonblob', dta['kmer_error_prob']);
    }
    /* KMER */
    let kmer_selection = $('#kmer-dropdown option').filter(function () {
        return $(this).html() == dta['kmer_name'];
    });
    if (kmer_selection.length > 0) {
        kmer_selection.prop('selected', true)
    } else {
        let opt = new Option(dta['kmer_name'] + " (CUSTOM)", dta['kmer_name'], undefined, true);
        //opt.data('jsonblob',dta['kmer_error_prob']);
        $('#kmer-dropdown').append(opt);
        //opt.prop('selected', true);
        $('#kmer-dropdown option:selected').data('jsonblob', dta['kmer_error_prob']);
    }
    /* Homopolymer */
    let homopolymer_selection = $('#homopolymer-dropdown option').filter(function () {
        return $(this).html() == dta['homopolymer_name'];
    });
    if (homopolymer_selection.length > 0) {
        homopolymer_selection.prop('selected', true)
    } else {
        let opt = new Option(dta['homopolymer_name'] + " (CUSTOM)", dta['homopolymer_name'], undefined, true);
        //opt.data('jsonblob',dta['homopolymer_error_prob']);
        $('#homopolymer-dropdown').append(opt);
        //opt.prop('selected', true);
        $('#homopolymer-dropdown option:selected').data('jsonblob', dta['homopolymer_error_prob']);
    }

    /*SEQ*/
    seq.val(0).prop('disabled', dta['use_error_probs']);
    let seq_selection = $('#seqmeth option').filter(function () {
        return $(this).val() == dta['sequence_method'];
    });
    if (seq_selection.length > 0) {
        seq_selection.prop('selected', true)
    } else {
        let opt = new Option(dta['sequence_method_name'] + " (CUSTOM)", dta['sequence_method_name'], undefined, true);
        $('#seqmeth').append(opt);
        //TODO
        let sm_sel = $('#seqmeth option:selected')
        sm_sel.data('err_attributes', dta['sequence_method_conf']['err_attributes']);
        sm_sel.data('err_data', dta['sequence_method_conf']['err_data']);
    }

    /* SYNTH */
    synth.val(0).prop('disabled', dta['use_error_probs']);
    let synth_selection = $('#synthmeth option').filter(function () {
        return $(this).val() == dta['synthesis_method'];
    });
    if (synth_selection.length > 0) {
        synth_selection.prop('selected', true)
    } else {
        let opt = new Option(dta['synthesis_method_name'] + " (CUSTOM)", dta['synthesis_method_name'], undefined, true);
        $('#synthmeth').append(opt);
        //TODO
        let sm_sel = $('#synthmeth option:selected');
        sm_sel.data('err_attributes', dta['synthesis_method_conf']['err_attributes']);
        sm_sel.data('err_data', dta['synthesis_method_conf']['err_data']);
    }

    $('#calcprobs').prop("checked", dta['use_error_probs']);
    $('limitedChars').prop("checked", dta['acgt_only']);
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
    let seq_meth = $("#seqmeth option:selected");
    let synth_meth = $("#synthmeth option:selected");
    return JSON.stringify({
        sequence: sequence,
        key: apikey,
        enabledUndesiredSeqs: extractUndesiredToJson(),
        kmer_windowsize: $('#kmer_window_size').val(),
        gc_windowsize: $('#gc_window_size').val(),
        gc_name: gc_dropdown_select.text(),
        error_prob: gc_error_prob,
        gc_error_prob: gc_error_prob,
        homopolymer_error_prob: homopolymer_error_prob,
        homopolymer_name: homopolymer_dropdown_select.text(),
        kmer_error_prob: kmer_error_prob,
        kmer_name: kmer_dropdown_select.text(),
        sequence_method: seq_meth.val(),
        sequence_method_conf: {
            err_data: seq_meth.data('err_data'),
            err_attributes: seq_meth.data('err_attributes')
        },
        sequence_method_name: seq_meth.text(),
        synthesis_method: synth_meth.val(),
        synthesis_method_conf: {
            err_data: synth_meth.data('err_data'),
            err_attributes: synth_meth.data('err_attributes')
        },
        synthesis_method_name: synth_meth.text(),
        use_error_probs: $('#calcprobs').is(":checked"),
        acgt_only: $('#limitedChars').is(":checked"),
        send_mail: $('#send_email').is(":checked"),
        asHTML: true
    }, undefined, space);
}

function queryServer(uuid) {
    let submit_seq_btn = $('#submit_seq_btn');
    let sequence = $("#sequence").val().toUpperCase();
    let homopolymer = $('#homopolymer');
    let gccontent = $('#gccontent');
    let sequences = $('#subsequences');
    let kmer = $('#kmer');
    let overall = $('#overall');
    let seq_seq = $('#seq_seq');
    let synth_seq = $('#synth_seq');
    let mod_seq = $('#mod_seq');

    /*for (let i = 0; i <= overall.text().length; i++) {
        let curr_char = $(".overall_char" + (i + 1));
        curr_char.data('errorprob', 0.0);
    }*/

    //var endpoints = ['gccontent', 'homopolymers'];

    //for (var mode in endpoints) {


    //endpoints.keys().forEach(function (mode) {

    let endpoints = {
        "gccontent": gccontent,
        "homopolymer": homopolymer,
        "kmer": kmer,
        "subsequences": sequences,
        "all": overall,
        "sequencing": seq_seq,
        "synthesis": synth_seq,
        "modify": mod_seq
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
    let res = $('#results');
    let resultsbymail = $('#resultsbymail');
    for (let mode in {"all": overall}) {
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

                    for (let error_source in data) {
                        endpoints[error_source].html(data[error_source]);
                    }
                    makeHoverGroups();
                    res.css('display', 'initial');
                    $('html, body').animate({scrollTop: res.offset().top}, 500);
                }
                var element = document.getElementById("mod_seq");
                set_mod_seq_inf(element.innerText, 1, element.innerText.length);
                if (data['result_by_mail'] === true) {
                    //TODO show info that the result will be send via mail
                    resultsbymail.css('display', 'initial');
                }
                submit_seq_btn.removeClass('is-loading');
            },
            fail: function (data) {
                console.log(data);
                //$('#text_lettering').text(data);
                submit_seq_btn.removeClass('is-loading');
            }
            ,
            error: function (jqXHR, textStatus, errorThrown) {
                console.log("Error, status = " + textStatus + ", " + "error thrown: " + errorThrown);
                submit_seq_btn.removeClass('is-loading');
            }
        });
    }
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

/*for (var i = 0, l = $('#text_lettering').text().length; i <= l; i++) {
    let curr_char = $(".char" + (i + 1));
    curr_char.css("background-color", getColorForPercentage(i / l));
    curr_char.css("color", "gray");
    curr_char.attr('title', (i / l));
    //$(".text_lettering").append(li);
}*/

function copyToClipboard(element) {
    var $temp = $("<input>");
    $("body").append($temp);
    $temp.val($(element).text()).select();
    document.execCommand("copy");
    $temp.remove();
}


function updateSynthDropdown(host, apikey, type) {
    $.post({
        url: host + "api/get_error_probs",
        dataType: 'json',
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify({
            key: apikey,
            type: type
        }),
        async: true,
        beforeSend: function (xhr) {
            if (xhr && xhr.overrideMimeType) {
                xhr.overrideMimeType('application/json;charset=utf-8');
            }
        },
        success: function (data) {
            let el = $('#synthmeth');
            el.empty(); // remove old options
            $.each(data['synth'], function (name) {
                let elem = data['synth'][name];
                let optgroup = $("<optgroup label='" + name + "'></optgroup>");
                optgroup.appendTo(el);
                $.each(elem, function (inner_id) {
                    let id = elem[inner_id]['id'];
                    let id_name = "" + name + "_" + id;
                    optgroup.append($("<option></option>").attr('value', id).attr('id', id_name).text(elem[inner_id]['name']).data('err_attributes', elem[inner_id]['err_attributes']).data('err_data', elem[inner_id]['err_data']));
                });
            });

            let sel = $('#seqmeth');
            sel.empty(); // remove old options
            $.each(data['seq'], function (name) {
                let elem = data['seq'][name];
                let optgroup = $("<optgroup label='" + name + "'></optgroup>");
                optgroup.appendTo(sel);
                $.each(elem, function (inner_id) {
                    let id = elem[inner_id]['id'];
                    let id_name = "" + name + "_" + id;
                    optgroup.append($("<option></option>").attr('value', id).attr('id', id_name).text(elem[inner_id]['name']).data('err_attributes', elem[inner_id]['err_attributes']).data('err_data', elem[inner_id]['err_data']));
                });
            });
        },
        fail: function (data) {
            console.log(data)
            //TODO show error message on screen
        }
    });
}


function changeurl(new_url) {
    window.history.pushState("data", "Title", new_url);
    //document.title = url;
}


var dropZone = document.getElementById('main-body');
dropZone.addEventListener('dragover', handleDragOver, false);
dropZone.addEventListener('drop', handleFileChange, false);

function set_mod_seq_inf(sel, sel_start, sel_end){
    var sel_gc_con = ((count_char(sel, 'G') + count_char(sel, 'C'))/sel.length)*100;
    sel_gc_con = Math.round(sel_gc_con * 100)/100;
    var sel_tm = get_tm(sel)
    sel_tm = Math.round(sel_tm * 100)/100;
    document.getElementById("mod_seq_inf").innerHTML = "GC-Content: "+sel_gc_con+" Tm: "+sel_tm+"°C Start-Pos: "+ sel_start+" End-Pos: "+ sel_end;
}

function count_char(sel_seq, char) {
    var count = 0;
    for (var i = 0; i < sel_seq.length; i +=1){
        if(sel_seq[i] === char){
            count += 1;
        }
    }
    return count;
}

function get_tm(sel_seq){
    var tm = 0;
    if(sel_seq.length < 14){
        tm = (count_char(sel_seq, 'A')+count_char(sel_seq, 'T'))*2 + (count_char(sel_seq, 'G')+count_char(sel_seq, 'C'))*4
    }
    else{
        tm = 64.9 + 41*(count_char(sel_seq, 'G')+count_char(sel_seq,'C')-16.4)/(sel_seq.length)
    }
    return tm;
}

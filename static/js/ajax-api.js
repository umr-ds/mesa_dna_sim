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
            res.push({
                id: id.val(),
                sequence: sequence.val(),
                error_prob: error_prob.val(),
                enabled: enabled.checked
            });
        }
    });
    return res;
}

function round(value, decimals) {
    return Number(Math.round(value + 'e' + decimals) + 'e-' + decimals);
}

$(document).ready(function () {
    let seq = $("#sequence");
    seq.keypress(function (e) {
        let chr = String.fromCharCode(e.which);
        let limitAlphabet = $('#limitedChars')[0].checked;
        if ("ACGTacgt".indexOf(chr) < 0 && limitAlphabet) {
            return false;
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
    //endpoints.keys().forEach(function (mode) {

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

    let send_data = undefined;
    if (uuid === undefined) {
        send_data = JSON.stringify({
            sequence: sequence,
            key: apikey,
            enabledUndesiredSeqs: extractUndesiredToJson(),
            kmer_windowsize: $('#kmer_window_size').val(),
            gc_windowsize: $('#gc_window_size').val(),
            error_prob: gc_error_prob,
            gc_error_prob: gc_error_prob,
            homopolymer_error_prob: homopolymer_error_prob,
            kmer_error_prob: kmer_error_prob,
            sequence_method: $("#seqmeth option:selected").val(),
            synthesis_method: $("#synthmeth option:selected").val(),
            use_error_probs: $('#calcprobs').is(":checked"),
            random_seed: $('#seed').val(),
            asHTML: true
        });
    } else {
        send_data = JSON.stringify(
            {
                key: apikey,
                uuid: uuid
            });
    }
    let res = $('#results');
    for (let mode in {"all": overall}) {
        $.post({
            url: "http://" + host + "/api/" + mode,
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
            },
            success: function (data) {
                let recv_uuid = data['uuid'];
                if (recv_uuid !== undefined) {
                    changeurl("query_sequence?uuid=" + recv_uuid);
                    const shr_txt = $("#link_to_share");
                    shr_txt.text(window.location.href);
                }
                $("#used_seed").text(data['seed']);
                if (data['did_succeed'] !== false) {
                    data = data['res'];
                    for (let error_source in data) {
                        endpoints[error_source].html(data[error_source]);
                    }
                    makeHoverGroups();
                    res.css('display', 'initial');
                    $('html, body').animate({scrollTop: res.offset().top}, 500);
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
        url: "http://" + host + "/api/get_error_probs",
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
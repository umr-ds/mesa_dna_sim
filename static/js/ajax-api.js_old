let apikey = "";
let host = "";

function setApikey(hst, key) {
    apikey = key;
    host = hst;
}

function makeHoverGroups() {
    $('span[class^="group_" ],span[class*=" group_"]').each(function () {
        let cls = $(this).attr('class').split(" ");
        $("." + cls[cls.length - 1]).hover(function () {
            $("." + cls[cls.length - 1]).css('font-weight', "bold");
        }, function () {
            $("." + cls[cls.length - 1]).css('font-weight', "normal");
        });
    });
}

function extractUndesiredToJson() {
    let res = [];
    $('[id^="subseq_"]').each(function () {
        let enabled = $(this).children().find("[id='enabled']")[0];
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
        let sequence = $("#sequence").val().toUpperCase();
        let homopolymer = $('#homopolymer');
        let gccontent = $('#gccontent');
        let sequences = $('#subsequences');
        let kmer = $('#kmer');
        let overall = $('#overall');
        homopolymer.text(sequence);
        gccontent.text(sequence);
        sequences.text(sequence);
        kmer.text(sequence);
        overall.text(sequence);

        homopolymer.lettering();
        gccontent.lettering();
        sequences.lettering();
        kmer.lettering();
        overall.lettering();

        for (let i = 0; i <= overall.text().length; i++) {
            let curr_char = $(".overall_char" + (i + 1));
            curr_char.data('errorprob', 0.0);
        }
        //var endpoints = ['gccontent', 'homopolymers'];

        //for (var mode in endpoints) {

        let endpoints = {"gccontent": gccontent, "homopolymer": homopolymer, "kmer": kmer, "subsequences": sequences};
        //endpoints.keys().forEach(function (mode) {
        for (let mode in endpoints) {
            let error_prob = undefined;
            if (mode === "gccontent") {
                let dropdown_select = $('#gc-dropdown option:selected');
                error_prob = dropdown_select.data('jsonblob');
                if (typeof (error_prob) === "string")
                    error_prob = JSON5.parse(error_prob);
            } else if (mode === "homopolymer") {
                let dropdown_select = $('#homopolymer-dropdown option:selected');
                error_prob = dropdown_select.data('jsonblob');
                if (typeof (error_prob) === "string")
                    error_prob = JSON5.parse(error_prob);
            } else {
                let dropdown_select = $('#homopolymer-dropdown option:selected');
                error_prob = dropdown_select.data('jsonblob');
                if (typeof (error_prob) === "string")
                    error_prob = JSON5.parse(error_prob);
            }
            $.post({
                url: "http://" + host + "/api/" + mode,
                dataType: 'json',
                contentType: 'application/json;charset=UTF-8',
                data: JSON.stringify({
                    sequence: sequence,
                    key: apikey,
                    enabledUndesiredSeqs: extractUndesiredToJson(),
                    kmer_windowsize: $('#kmer_window_size').val(),
                    gc_windowsize: $('#gc_window_size').val(),
                    error_prob: error_prob
                }),
                async: true,
                beforeSend: function (xhr) {
                    if (xhr && xhr.overrideMimeType) {
                        xhr.overrideMimeType('application/json;charset=utf-8');
                    }
                },
                success: function (data) {
                    //$("#spoiler3_label").click();
                    //let obj = jQuery.parseJSON(data);
                    let curr_group = 0;
                    for (let block_num in data) {
                        for (let i = data[block_num].startpos; i <= data[block_num].endpos; i++) {
                            let curr_char = $("." + mode + "_char" + (i + 1));
                            curr_char.data('errorprob', Math.min(data[block_num].errorprob, 1.0));
                            curr_char.css("background-color", getColorForPercentage(curr_char.data('errorprob')));
                            curr_char.css("color", "gray");
                            curr_char.attr('title', "Error Probability: " + round(curr_char.data('errorprob') * 100.0, 2) + " %");
                            if (mode === "kmer") {
                                curr_char.addClass('group_' + data[block_num].kmer);
                            } else {
                                curr_char.addClass('group_' + mode + '_' + curr_group);
                            }
                            let overall_curr_char = $(".overall_char" + (i + 1));
                            overall_curr_char.data('errorprob', Math.min(overall_curr_char.data('errorprob') + data[block_num].errorprob, 1.0));
                            overall_curr_char.css("background-color", getColorForPercentage(overall_curr_char.data('errorprob')));
                            overall_curr_char.css("color", "gray");
                            overall_curr_char.attr('title', "Error Probability: " + round((overall_curr_char.data('errorprob') * 100.0), 2) + " %");
                            if (mode === "kmer") {
                                overall_curr_char.addClass('group_' + data[block_num].kmer);
                            } else {
                                overall_curr_char.addClass('group_' + mode + '_' + curr_group);
                            }
                            //$('#text_lettering').text(data[i].base);
                        }
                        curr_group++;
                    }
                    makeHoverGroups();
                },
                fail: function (data) {
                    let obj = jQuery.parseJSON(data);
                    for (let i in obj) {
                        $('#text_lettering').text(data[i].base);
                    }
                    //$('#text_lettering').text(data);
                }
            });
        }
        ;
        //alert("Handler for .submit() called.");
    });
});

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
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
                contentType: 'application/json;charset=UTF-8',
                data: JSON.stringify({
                    sequence: sequence,
                    key: apikey,
                    enabledUndesiredSeqs: extractUndesiredToJson(),
                    kmer_windowsize: $('#kmer_window_size').val(),
                    gc_windowsize: $('#gc_window_size').val(),
                    error_prob: error_prob,
                    asHTML: true
                }),
                async: true,
                success: function (data) {
                    endpoints[mode].html(data);
                    makeHoverGroups();
                },
                fail: function (data) {
                    console.log(data);
                    //$('#text_lettering').text(data);
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    console.log("Error, status = " + textStatus + ", " + "error thrown: " + errorThrown);
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
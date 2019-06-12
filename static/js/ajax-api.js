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
    });
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
    let submit_seq_btn = $('#submit_seq_btn');
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

        let endpoints = {
            "gccontent": gccontent,
            "homopolymer": homopolymer,
            "kmer": kmer,
            "subsequences": sequences,
            "all": overall
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


        for (let mode in {"all": overall}) {
            $.post({
                url: "http://" + host + "/api/" + mode,
                contentType: 'application/json;charset=UTF-8',
                dataType: 'json',
                data: JSON.stringify({
                    sequence: sequence,
                    key: apikey,
                    enabledUndesiredSeqs: extractUndesiredToJson(),
                    kmer_windowsize: $('#kmer_window_size').val(),
                    gc_windowsize: $('#gc_window_size').val(),
                    error_prob: gc_error_prob,
                    gc_error_prob: gc_error_prob,
                    homopolymer_error_prob: homopolymer_error_prob,
                    kmer_error_prob: kmer_error_prob,
                    asHTML: true
                }),
                async: true,
                beforeSend: function () {
                    submit_seq_btn.addClass('is-loading');
                },
                success: function (data) {
                    for (let error_source in data) {
                        endpoints[error_source].html(data[error_source]);
                    }
                    makeHoverGroups();
                    submit_seq_btn.removeClass('is-loading');
                },
                fail: function (data) {
                    console.log(data);
                    //$('#text_lettering').text(data);
                    submit_seq_btn.removeClass('is-loading');
                },
                error: function (jqXHR, textStatus, errorThrown) {
                    console.log("Error, status = " + textStatus + ", " + "error thrown: " + errorThrown);
                    submit_seq_btn.removeClass('is-loading');
                }
            });
        }
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
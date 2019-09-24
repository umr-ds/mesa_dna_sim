jQuery(document).ready(function () {
    const gccontent = $("#gccontent");
    const homopolymer = $("#homopolymer");
    const kmer = $("#kmer");
    const sequences = $('#subsequences');
    const overall = $('#overall');
    const dot_seq = $('#dot_seq');
    //const seq_seq = $('#seq_seq');
    //const synth_seq = $('#synth_seq');
    const mod_seq = $('#mod_seq');

    const scrollList = [gccontent, homopolymer, kmer, sequences, overall, dot_seq, mod_seq]; // seq_seq, synth_seq,

    scrollList.forEach(function (scr) {
        scr.scroll(function () {
            scrollList.forEach(function (targt) {
                if (scr !== targt) {
                    targt.scrollTop(scr.scrollTop());
                    targt.scrollLeft(scr.scrollLeft());
                }
            })
        })
    });
});
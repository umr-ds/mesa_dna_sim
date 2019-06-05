jQuery(document).ready(function () {
    const gccontent = $("#gccontent");
    const homopolymer = $("#homopolymer");
    const kmer = $("#kmer");
    const sequences = $('#subsequences');
    const overall = $('#overall');
    kmer.scroll(function () {
        homopolymer.scrollTop(kmer.scrollTop());
        homopolymer.scrollLeft(kmer.scrollLeft());
        gccontent.scrollTop(kmer.scrollTop());
        gccontent.scrollLeft(kmer.scrollLeft());
        overall.scrollTop(kmer.scrollTop());
        overall.scrollLeft(kmer.scrollLeft());
        sequences.scrollTop(kmer.scrollTop());
        sequences.scrollLeft(kmer.scrollLeft());

    });
    overall.scroll(function () {
        homopolymer.scrollTop(overall.scrollTop());
        homopolymer.scrollLeft(overall.scrollLeft());
        gccontent.scrollTop(overall.scrollTop());
        gccontent.scrollLeft(overall.scrollLeft());
        kmer.scrollTop(overall.scrollTop());
        kmer.scrollLeft(overall.scrollLeft());
        sequences.scrollTop(overall.scrollTop());
        sequences.scrollLeft(overall.scrollLeft());
    });
    gccontent.scroll(function () {
        homopolymer.scrollTop(gccontent.scrollTop());
        homopolymer.scrollLeft(gccontent.scrollLeft());
        overall.scrollLeft(gccontent.scrollLeft());
        overall.scrollTop(gccontent.scrollTop());
        kmer.scrollTop(gccontent.scrollTop());
        kmer.scrollLeft(gccontent.scrollLeft());
        sequences.scrollTop(gccontent.scrollTop());
        sequences.scrollLeft(gccontent.scrollLeft());
    });
    sequences.scroll(function () {
        homopolymer.scrollTop(sequences.scrollTop());
        homopolymer.scrollLeft(sequences.scrollLeft());
        overall.scrollLeft(sequences.scrollLeft());
        overall.scrollTop(sequences.scrollTop());
        kmer.scrollTop(sequences.scrollTop());
        kmer.scrollLeft(sequences.scrollLeft());
        gccontent.scrollTop(sequences.scrollTop());
        gccontent.scrollLeft(sequences.scrollLeft());
    });
    homopolymer.scroll(function () {
        gccontent.scrollTop(homopolymer.scrollTop());
        gccontent.scrollLeft(homopolymer.scrollLeft());
        overall.scrollLeft(homopolymer.scrollLeft());
        overall.scrollTop(homopolymer.scrollTop());
        kmer.scrollTop(homopolymer.scrollTop());
        kmer.scrollLeft(homopolymer.scrollLeft());
        sequences.scrollTop(homopolymer.scrollTop());
        sequences.scrollLeft(homopolymer.scrollLeft());
    });
});
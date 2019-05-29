let curr_chart, element, datasetIndex, index, scale, org_pos, org_data, org_options;
let useCubicInterpolation = true;
let toogleDragXaxis = false;
let dragXcol = '#209cee';
let interpolcol = '#50ee0a';

const xRoundingFactor = 0;
const yRoundingFactor = 2;
const maximumY = 100;
const maximumX = 20;

function serializeData() {
    if (curr_chart === undefined)
        drawGraph(); // just to initialize everything...
    let dataset = curr_chart.data.datasets[0];
    return JSON.stringify({
        data: dataset.data,
        interpolation: dataset.cubicInterpolationMode === "monotone",
        maxX: maximumX,
        maxY: maximumY,
        xRound: xRoundingFactor,
        yRound: yRoundingFactor
    });
}

function toogleCubicInterpolation() {
    useCubicInterpolation = !useCubicInterpolation;
    curr_chart.data.datasets.forEach((dataset) => {
        if (useCubicInterpolation) {
            dataset['cubicInterpolationMode'] = 'monotone';
            dataset['lineTension'] = 1.0;
        } else {
            dataset['cubicInterpolationMode'] = 'default';
            dataset['lineTension'] = 0.0;
        }
    });
    curr_chart.update();
    if (useCubicInterpolation) {
        interpolcol = '#50ee0a';
    } else {
        interpolcol = '#209cee';
    }
    $('#toogleinterpolation').css('background-color', interpolcol);
}

function removePoint(x_val) {
    curr_chart.data.datasets.forEach((dataset) => {
        var found = dataset.data.findIndex(function (element) {
            return element.x === Number(x_val);
        });
        if (found < 0) {
            return false; // x_val not found in points.
        } else {
            for (let tmp = found; tmp < dataset.data.length - 1; tmp++) {
                dataset.data[tmp] = dataset.data[tmp + 1]; //update
            }
            dataset.data.pop();
        }
    });
    curr_chart.update();
}

function findDuplicateX() {
    let duplicates = new Set();
    curr_chart.data.datasets.forEach((dataset) => {
        let unique = new Set();
        for (let tmp = 0; tmp < dataset.data.length; tmp++) {
            const currElem = dataset.data[tmp].x;
            if (unique.has(currElem)) {
                duplicates.add(currElem);
            } else {
                unique.add(currElem);
            }
        }
    });
    return duplicates;
}

function removeDuplicatesX() {
    findDuplicateX().forEach(function (dup) {
        removePoint(dup);
    });
}

function toogleDragX() {
    toogleDragXaxis = !toogleDragXaxis;
    curr_chart.options.dragX = toogleDragXaxis;
    curr_chart.update();
    if (toogleDragXaxis) {
        dragXcol = '#50ee0a';
    } else {
        dragXcol = '#209cee';
    }
    $('#toogleDragX').css('background-color', dragXcol);
}

function addPoint(x_val, y_val) {
    x_val = Math.min(round(Number(x_val), xRoundingFactor), maximumX);
    y_val = Math.min(round(Number(y_val), yRoundingFactor), maximumY);
    curr_chart.data.datasets.forEach((dataset) => {
        var found = dataset.data.findIndex(function (element) {
            return element.x === Number(x_val);
        });
        if (found < 0) {
            dataset.data.push({x: x_val, y: y_val});
        } else {
            dataset.data[found] = {x: x_val, y: y_val}; //update
        }
    });
    sortData();
}

function setYValueBeforeX(lim, value) {
    /**
     * sets the value to "value" for all data-points in x-range [0..lim)
     */
    value = Math.max(Math.min(round(Number(value), yRoundingFactor), maximumY), 0);
    curr_chart.data.datasets.forEach((dataset) => {
        for (let v in dataset.data) {
            if (dataset.data[v].x < lim) {
                dataset.data[v].y = value;
            }
        }
    });
    curr_chart.update();
}

function setYValueAfterX(lim, value) {
    /**
     * sets the value to "value" for all data-points in x-range (lim..end]
     */
    value = Math.max(Math.min(round(Number(value), yRoundingFactor), maximumY), 0);
    curr_chart.data.datasets.forEach((dataset) => {
        for (let v in dataset.data) {
            if (dataset.data[v].x > lim) {
                dataset.data[v].y = value;
            }
        }
    });
    curr_chart.update();
}

function resetChanges() {
    curr_chart.data.datasets = $.extend(true, [], org_data);
    curr_chart.options = $.extend(true, {}, org_options);
    curr_chart.update();
}

function constructDataset(datalist, lbl, useInterpolation) {
    const newdataset = {
        label: lbl,
        data: datalist,
        showLine: true,
        borderColor: "#3e95cd",
        cubicInterpolationMode: 'monotone',
        lineTension: 1.0,
        fill: true
    };
    if (!useInterpolation) {
        newdataset['cubicInterpolationMode'] = 'default';
        newdataset['lineTension'] = 0.0;
    }
    if (useInterpolation === !useCubicInterpolation) {
        // update color and global var!
        useCubicInterpolation = useInterpolation;
        if (useCubicInterpolation) {
            interpolcol = '#50ee0a';
        } else {
            interpolcol = '#209cee';
        }
        $('#toogleinterpolation').css('background-color', interpolcol);
    }
    return newdataset;
}

function drawGraph() {
    if (curr_chart !== undefined) {
        org_data = $.extend(true, [], curr_chart.data.datasets);
        org_options = $.extend(true, {}, curr_chart.options);
        return curr_chart.update();
    }
    let curr_dataset = constructDataset([{x: 0.0, y: 0.0}, {x: 2.0, y: 0.0}, {x: 4.0, y: 20.0}, {x: 5.0, y: 50.0},
        {x: 6.0, y: 80.0}, {x: 7.0, y: 100.0}, {x: 20.0, y: 100.0}], "Error Probability", true);

    /*var homopolymer_dataset = {
        label: "Error Probability",
        data: [{x: 0.0, y: 0.0}, {x: 2.0, y: 0.0}, {x: 4.0, y: 20.0}, {x: 5.0, y: 50.0}, {x: 6.0, y: 80.0},
            {x: 7.0, y: 100.0}, {x: 20.0, y: 100.0}],
        showLine: true, // disable for a single dataset
        borderColor: "#3e95cd",
        cubicInterpolationMode: 'monotone',
        //lineTension: 0,
        fill: false
    };*/

    var ctx = document.getElementById("myChart");

    Chart.platform.disableCSSInjection = true;


    curr_chart = new Chart(ctx, {
        type: 'line',
        data: {
            //labels: years,
            datasets: [curr_dataset]
        },
        options: {
            legend: {
                display: false
            },
            showLines: false, // disable for all datasets
            dragData: true,
            dragX: false,
            dragDataRound: yRoundingFactor, // set to 1,2,3,4... for float values
            scales: {
                xAxes: [{
                    type: 'linear',
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Homopolymer length',
                        fontStyle: 'bold'
                    },
                    ticks: {
                        beginAtZero: true,
                        suggestedMax: maximumX,

                        callback: function (value, index, values) {
                            return parseFloat(value).toFixed(xRoundingFactor);
                        },
                        autoSkip: false,
                        stepSize: 1.0 //set to .5 for half steps
                    }
                    // ...
                }
                ], yAxes: [{
                    type: 'linear',
                    display: true,

                    scaleLabel: {
                        display: true,
                        labelString: 'Error Probabilty (%)',
                        fontStyle: 'bold'
                    },
                    ticks: {
                        beginAtZero: true,
                        max: maximumY,
                        callback: function (value, index, values) {
                            return parseFloat(value).toFixed(2);
                        },
                        autoSkip: true
                    }
                    // ...
                }
                ]
            },
            onDragStart: function (e, datasetIndex, index, value) {
                element = curr_chart.getElementAtEvent(e)[0];
                scale = element['_yScale'].id;
                datasetIndex = element['_datasetIndex'];
                index = element['_index'];
                org_pos = curr_chart.data.datasets[datasetIndex].data[index];

            },
            onDrag: function (e, datasetIndex, index, value) {
                for (var scaleName in curr_chart.scales) {
                    let scale = curr_chart.scales[scaleName];
                    if (scale.isHorizontal()) {
                        var valueX = round(scale.getValueForPixel(e.offsetX), xRoundingFactor);
                        if (!toogleDragXaxis)
                            valueX = org_pos.x;
                    } else {
                        var valueY = round(scale.getValueForPixel(e.offsetY), yRoundingFactor);
                    }
                }
                if (toogleDragXaxis) {
                    var found = curr_chart.data.datasets[datasetIndex].data.findIndex(function (element) {
                        return element.x === Number(valueX);
                    });
                    if (found < 0) {
                        curr_chart.data.datasets[datasetIndex].data[index] = {x: valueX, y: valueY};

                    } else {
                        curr_chart.data.datasets[datasetIndex].data[index] = org_pos;
                        curr_chart.data.datasets[datasetIndex].data[found] = {x: valueX, y: valueY}; //update
                    }
                    //console.log(curr_chart.data.datasets[datasetIndex].data[index]);
                } else {
                    curr_chart.data.datasets[datasetIndex].data[index] = {x: valueX, y: valueY};
                }
                sortData();
                /*for (var elem = 0; elem < curr_chart.data.datasets[datasetIndex].data.length - 1; elem++) {
                    if (curr_chart.data.datasets[datasetIndex].data[elem].x < valueX && curr_chart.data.datasets[datasetIndex].data[elem + 1] >= valueX) {
                        element['_index'] = elem + 1
                    }
                }*/
            }
            ,
            onDragEnd: function (e, datasetIndex, index, value) {
                //console.log(datasetIndex, index, value);
                const curr_dta = curr_chart.data.datasets[datasetIndex].data[index];
                curr_chart.data.datasets[datasetIndex].data[index] = {
                    x: round(curr_dta.x, xRoundingFactor), y: round(curr_dta.y, yRoundingFactor)
                };
                //console.log(curr_chart.data.datasets[datasetIndex].data[index]);
                //updateData(e);
                sortData();
                removeDuplicatesX();
            }
        }
    });
    org_data = $.extend(true, [], curr_chart.data.datasets);
    org_options = $.extend(true, {}, curr_chart.options);
    $('#toogleinterpolation').css('background-color', interpolcol);
    $('#toogleDragX').css('background-color', dragXcol);
}

function sortData() {
    curr_chart.data.datasets.forEach((dataset) => {
        dataset.data.sort(function (a, b) {
            return a.x - b.x;
        });
    });
    curr_chart.update();
}
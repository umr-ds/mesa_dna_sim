let curr_chart;

function updateChart(chart, useCubicInterpolation) {
    chart.data.datasets.forEach((dataset) => {
        if (useCubicInterpolation) {
            dataset['cubicInterpolationMode'] = 'monotone';
            dataset['lineTension'] = 1.0;
        } else {
            dataset['cubicInterpolationMode'] = 'default';
            dataset['lineTension'] = 0.0;
        }
    });
    chart.update();
}

function addPoint(x_val, y_val) {
    curr_chart.data.datasets.forEach((dataset) => {
        var found = dataset.data.findIndex(function (element) {
            return element.x === x_val;
        });
        if (found < 0) {
            dataset.data.push({x: x_val, y: y_val});
        } else {
            dataset.data[found] = {x: x_val, y: y_val}; //update
        }
    });
    sortData();
}

function setYValueBeforeX(chart, value, lim) {
    /**
     * sets the value to "value" for all data-points in x-range [0..lim)
     */
    chart.data.datasets.forEach((dataset) => {
        for (let v in dataset.data) {
            if (dataset.data[v].x < lim) {
                dataset.data[v].y = value;
            }
        }
    });
    chart.update();
}

function setYValueAfterX(chart, value, lim) {
    /**
     * sets the value to "value" for all data-points in x-range (lim..end]
     */
    chart.data.datasets.forEach((dataset) => {
        for (let v in dataset.data) {
            if (dataset.data[v].x < lim) {
                dataset.data[v].y = value;
            }
        }
    });
    chart.update();
}

function drawGraph(useCubicInterpolation) {
    if (curr_chart !== undefined)
        return true; //updateChart(curr_chart, useCubicInterpolation);

    var africa_dataset = {
        label: "Africa",
        data: [{x: 1.0, y: 41}, {x: 2.0, y: 20}, {x: 4.0, y: 30}, {x: 8.0, y: 40}],
        showLine: true, // disable for a single dataset
        borderColor: "#3e95cd",
        cubicInterpolationMode: 'monotone',
        //lineTension: 0,
        fill: false
    };

    var ctx = document.getElementById("myChart");

    Chart.platform.disableCSSInjection = true;


    curr_chart = new Chart(ctx, {
            type: 'line',
            data: {
                //labels: years,
                datasets: [africa_dataset]
            },
            options: {
                showLines: false, // disable for all datasets
                dragData: true,
                dragX: true,
                dragDataRound: 0, // set to 1,2,3,4... for float values
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
                            callback: function (value, index, values) {
                                return parseFloat(value).toFixed(2);
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
                            labelString: 'Error Probabilty',
                            fontStyle: 'bold'
                        },
                        ticks: {
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

                }
                ,
                onDrag: function (e, datasetIndex, index, value) {
                    for (var scaleName in curr_chart.scales) {
                        let scale = curr_chart.scales[scaleName];
                        if (scale.isHorizontal()) {
                            var valueX = round(scale.getValueForPixel(e.offsetX), 0);
                        } else {
                            var valueY = scale.getValueForPixel(e.offsetY);
                        }
                    }

                    var found = curr_chart.data.datasets[datasetIndex].data.findIndex(function (element) {
                        return element.x === valueX;
                    });
                    if (found < 0) {
                        curr_chart.data.datasets[datasetIndex].data[index] = {x: valueX, y: valueY};
                    } else {
                        curr_chart.data.datasets[datasetIndex].data[index] = org_pos;
                        curr_chart.data.datasets[datasetIndex].data[found] = {x: valueX, y: valueY}; //update
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
                    console.log(datasetIndex, index, value);
                    //updateData(e);
                    sortData();
                }
            }
        }
    )
    ;
}

var element, datasetIndex, index, scale, org_pos;

function sortData() {
    curr_chart.data.datasets.forEach((dataset) => {
        dataset.data.sort(function (a, b) {
            return a.x - b.x;
        });
    });
    curr_chart.update();
}
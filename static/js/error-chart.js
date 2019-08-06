let curr_chart, curr_dataset, element, datasetIndex, index, scale, org_pos, org_data, org_options;
let useCubicInterpolation = true;
let toogleDragXaxis = false;
let offColor = '#baa861';
let onColor = '#50ee0a';
let dragXcol = offColor;
let interpolcol = onColor;
let xLabelString = 'Homopolymer length';

let default_graph_name = "Default Graph"; //"New Graph";

let xRoundingFactor = 0;
let yRoundingFactor = 2;
let maximumY = 100;
let maximumX = 20;


let default_homopolymer_data = "{\"data\":[{\"x\":0,\"y\":0},{\"x\":2,\"y\":0},{\"x\":4,\"y\":20},{\"x\":5,\"y\":50}," +
    "{\"x\":6,\"y\":80},{\"x\":7,\"y\":100},{\"x\":20,\"y\":100}],\"interpolation\":true,\"maxX\":20," +
    "\"maxY\":100,\"xRound\":0,\"yRound\":2,\"label\":\"Error Probability\",\"xLabel\":\"Homopolymer length\"}";

let default_kmer_data = "{\"data\":[{\"x\":0,\"y\":0},{\"x\":6,\"y\":0.15},{\"x\":12,\"y\":0.85},{\"x\":22,\"y\":4.73}," +
    "{\"x\":40,\"y\":18.2},{\"x\":60,\"y\":40.7},{\"x\":79,\"y\":67.36},{\"x\":100,\"y\":100}],\"interpolation\":true," +
    "\"maxX\":20,\"maxY\":100,\"xRound\":0,\"yRound\":2,\"label\":\"Error Probability\",\"xLabel\":\"Kmer repeats\"}";

let default_gc_content_data = "{\"data\":[{\"x\":0,\"y\":100},{\"x\":30,\"y\":100},{\"x\":40,\"y\":0},{\"x\":60.17,\"y\":0}," +
    "{\"x\":70,\"y\":100},{\"x\":100,\"y\":100}],\"interpolation\":true,\"maxX\":100,\"maxY\":100,\"xRound\":0," +
    "\"yRound\":2,\"label\":\"Error Probability\",\"xLabel\":\"GC-Percentage\"}";

let default_gc_content_data_obj = {
    "data": [{"x": 0, "y": 100}, {"x": 30, "y": 100}, {"x": 40, "y": 0}, {"x": 60.17, "y": 0}, {"x": 70, "y": 100},
        {"x": 100, "y": 100}], "interpolation": true, "maxX": 100, "maxY": 100, "xRound": 2, "yRound": 2,
    "label": "Error Probability", "xLabel": "GC-Percentage"
};


const default_homopolymer_data_obj = {
    "data": [{"x": 0, "y": 0}, {"x": 2, "y": 0}, {"x": 4, "y": 20}, {"x": 5, "y": 50},
        {"x": 6, "y": 80}, {"x": 7, "y": 100}, {"x": 20, "y": 100}], "interpolation": true, "maxX": 20,
    "maxY": 100, "xRound": 0, "yRound": 2, "label": "Error Probability", "xLabel": "Homopolymer length"
};

const default_kmer_data_obj = {
    "data": [{"x": 0, "y": 0}, {"x": 6, "y": 0.15}, {"x": 12, "y": 0.85}, {"x": 22, "y": 4.73}, {"x": 40, "y": 18.2},
        {"x": 60, "y": 40.7}, {"x": 79, "y": 67.36}, {"x": 100, "y": 100}], "interpolation": true, "maxX": 20,
    "maxY": 100, "xRound": 0, "yRound": 2, "label": "Error Probability", "xLabel": "Homopolymer length"
};

const default_data_obj = {
    'gc': default_gc_content_data_obj,
    'homopolymer': default_homopolymer_data_obj,
    'kmer': default_kmer_data_obj
};

const defaults = {
    "homopolymer": default_homopolymer_data,
    "gc": default_gc_content_data,
    'kmer': default_kmer_data,
    undefined: default_gc_content_data
};

/**
 * loads ne Data and draws the graph into the canvas
 * @param data list of dicts ( e.g.: [{x:0.0, y:0.0},{x:1.0,y:10.5}, ...]
 * @param useInterpolation flag (true | false) if (monotone!) interpolation should be used
 * @param label Name of the Data! (shown on mouse-over)
 * @param xRoundF digits after , to round to for X-Axis
 * @param yRoundF digits after , to round to for Y-Axis
 * @param maxX maximum value for X-Axis (this is not enforced, a user can manually add points outside and the graph will be extended accordingly)
 * @param maxY maximum value for Y-Axis (this IS enforced and will be used to clip values!)
 * @param xLabel Label of the X-Axis (e.g.: "Homopolymer length", "GC-Percentage", ...)
 */
function loadAndDrawData(data, useInterpolation, label, xRoundF, yRoundF, maxX, maxY, xLabel) {
    if (curr_chart !== undefined) {
        curr_chart.destroy();
        curr_chart = undefined;
    }
    curr_dataset = constructDataset(data, label, useInterpolation);
    xRoundingFactor = xRoundF;
    yRoundingFactor = yRoundF;
    maximumX = maxX;
    maximumY = maxY;
    xLabelString = xLabel;
    drawGraph();
    if (useCubicInterpolation !== useInterpolation)
        toogleCubicInterpolation();
}

/**
 * dropdown_select.data('jsonblob'),
 dropdown_select.data('type'), dropdown_select.data('validated'),
 dropdown_select.data(id), dropdown_select.text()
 * @param serial_data
 * @param type
 */
function deserializeDataAndLoadDraw(serial_data, type) {

    if (serial_data === undefined) {
        serial_data = defaults[type];
    }
    if (typeof serial_data === "string") {
        serial_data = serial_data.replace(/True/g, 'true');
        serial_data = JSON5.parse(serial_data);
    }
    const json_dict = serial_data;
    return loadAndDrawData(json_dict["data"], json_dict["interpolation"], json_dict["label"], json_dict["xRound"],
        json_dict["yRound"], json_dict["maxX"], json_dict["maxY"], json_dict["xLabel"]);
}

function serializeData() {
    if (curr_chart === undefined)
        drawGraph(); // just to initialize everything...
    let dataset = curr_chart.data.datasets[0];
    return {
        "data": dataset.data,
        "interpolation": dataset.cubicInterpolationMode === "monotone",
        "maxX": maximumX,
        "maxY": maximumY,
        "xRound": xRoundingFactor,
        "yRound": yRoundingFactor,
        "label": dataset.label,
        "xLabel": xLabelString
    };
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
        interpolcol = onColor;
    } else {
        interpolcol = offColor; //'#209cee';
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
        dragXcol = onColor;
    } else {
        dragXcol = offColor; //'#209cee';
    }
    $('#toogleDragX').css('background-color', dragXcol);
}

function addPoint(x_val, y_val) {
    x_val = round(Number(x_val), xRoundingFactor); // we might want to enforce using Math.min(maximumX, ...)
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
            interpolcol = onColor;
        } else {
            interpolcol = offColor; //'#209cee';
        }
        $('#toogleinterpolation').css('background-color', interpolcol);
    }
    return newdataset;
}

function drawGraph() {
    if (curr_dataset === undefined)
        curr_dataset = constructDataset([{x: 0.0, y: 0.0}, {x: 2.0, y: 0.0}, {x: 4.0, y: 20.0}, {x: 5.0, y: 50.0},
            {x: 6.0, y: 80.0}, {x: 7.0, y: 100.0}, {x: 20.0, y: 100.0}], "Error Probability", true);
    if (curr_chart !== undefined) {
        org_data = $.extend(true, [], curr_chart.data.datasets);
        org_options = $.extend(true, {}, curr_chart.options);
        return curr_chart.update();
    }
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
                        labelString: xLabelString,
                        fontStyle: 'bold'
                    },
                    ticks: {
                        beginAtZero: true,
                        suggestedMax: maximumX,

                        callback: function (value, index, values) {
                            return parseFloat(value).toFixed(xRoundingFactor);
                        },
                        autoSkip: false
                        //stepSize: 1.0 //set to .5 for half steps
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


function buildDropdown(result, dropdown, emptyMessage) {
    // Remove current options
    dropdown.html('');
    // Add the empty option with the empty message
    dropdown.append('<option value="">' + emptyMessage + '</option>');
    // Check result isn't empty
    if (result !== '') {
        // Loop through each of the results and append the option to the dropdown
        $.each(result, function (k, v) {
            dropdown.append('<option data-editable="' + v.editable + '" data-jsonblob="' + v.content + '">' +
                v.name + '</option>');
        });
    }
}

/* Overlay / Chart-Display */

function closeOverlay() {
    let overlay = $("#overlay");
    /*$("#overlay").css({
        "opacity": "0",
        "display": "none",
    }).show().animate({opacity: 0}, 100).hide()*/
    //todo save values to the corresponding array
    overlay.fadeOut(175, "linear");
    //overlay.css("display", "none");
}

function showOverlay(validated, editable, id, text, type) {
    let overlay = $("#overlay");
    let chartName = $("#chart-name");
    /*$("#overlay").css({
        "opacity": "1",
        "display": "block",
    }).show().animate({opacity: 1}, 100)*/
    /*
     * if editable == false, we can only safe a copy via "Save as ________"
     * otherwise we want an "Update" Button +  "Delete" Buttton as well as an Option for "Save as ________"
     * additinally we want to show Validated true false
     */

    $("#update-chart").prop('disabled', !editable);
    $("#delete-chart").prop('disabled', !editable);
    chartName.val(text);
    chartName.data("id", id);
    chartName.data("validated", validated);
    chartName.data("type", type);

    overlay.fadeIn(100, "linear");
    //overlay.css("display", "block");
    //setYValueAfterX(curr_chart, 0, 3);
}

function saveChart(host, apikey, create_copy) {
    const chart_name = $('#chart-name');
    $.post({
        url: host + "api/update_error_prob_charts",
        dataType: 'json',
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify({
            name: chart_name.val(),
            key: apikey,
            chart_id: chart_name.data('id'),
            jsonblob: serializeData(),
            copy: create_copy,
            type: chart_name.data('type')
        }),
        async: true,
        beforeSend: function (xhr) {
            if (xhr && xhr.overrideMimeType) {
                xhr.overrideMimeType('application/json;charset=utf-8');
            }
        },
        success: function (data) {
            if (data["did_succeed"] === true) {
                updateDropdown(host, apikey, chart_name.data('type'));
                showOverlay(data["validated"], true, data["id"], data["name"], data["type"])
            } else {
                console.log(data)
                //TODO show error
            }
        },
        fail: function (data) {
            console.log(data)
            //TODO show error message on screen
        }
    });
}

function deleteChart(host, apikey) {
    const chart_name = $('#chart-name');
    $.post({
        url: host + "api/delete_error_prob_charts",
        dataType: 'json',
        contentType: 'application/json;charset=UTF-8',
        data: JSON.stringify({
            name: chart_name.val(),
            key: apikey,
            chart_id: chart_name.data('id'),
            type: chart_name.data('type')
        }),
        async: true,
        beforeSend: function (xhr) {
            if (xhr && xhr.overrideMimeType) {
                xhr.overrideMimeType('application/json;charset=utf-8');
            }
        },
        success: function (data) {
            if (data["did_succeed"] === true) {
                updateDropdown(host, apikey, chart_name.data('type'));
                deserializeDataAndLoadDraw(undefined, chart_name.data('type'));
                showOverlay(true, false, -1, default_graph_name, chart_name.data('type'));
            } else {
                console.log(data)
                //TODO show error
            }
        },
        fail: function (data) {
            console.log(data)
            //TODO show error message on screen
        }
    });
}

function updateDropdown(host, apikey, type) {
    $.post({
        url: host + "api/get_error_prob_charts",
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
            let el = $('#' + type + '-dropdown');
            el.empty(); // remove old options
            $.each(data['charts'], function (id) {
                let elem = data['charts'][id];
                el.append($("<option></option>").text(elem['name']).data('jsonblob', elem['jsonblob'])
                    .data('id', elem['id']).data('validated', elem['validated'])
                    .data('isowner', elem['isowner']).data('type', elem['type']));
            });
            el.append($("<option></option>").text(default_graph_name).data('id', -1).data('validated', true)
                .data('isowner', false).data('type', type).data('jsonblob', default_data_obj[type]));
        },
        fail: function (data) {
            console.log(data)
            //TODO show error message on screen
        }
    });
}
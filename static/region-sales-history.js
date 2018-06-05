let options = {
                    responsive: true,
                    hoverMode: 'index',
                    stacked: false,
                    title: {
                        display: true,
                        // text: 'Chart.js Line Chart - Multi Axis'
                    },
                    scales: {
                        yAxes: [{
                            type: 'linear', // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                            display: true,
                            position: 'left',
                            ticks: {
                                callback: function(label, index, labels) {
                                    return "$" + parseInt(label/1000)+'k';
                                }
                            },
                            scaleLabel: {
                                display: true,
                                labelString: '1k = 1000'
                            },
                            id: 'y-axis-1',
                        }, {
                            type: 'linear', // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                            display: true,
                            position: 'right',
                            id: 'y-axis-2',

                            // grid line settings
                            gridLines: {
                                drawOnChartArea: false, // only want the grid lines for one axis to show up
                            },
                        }],
                    }
                }
let options1 = { responsive: true,
                scales: {
                    yAxes: [
                        {
                            ticks: {
                                callback: function(label, index, labels) {
                                    return "$" + parseInt(label/1000)+'k';
                                }
                            },
                            scaleLabel: {
                                display: true,
                                labelString: '1k = 1000'
                            }
                        }
                    ]
                }
 };




let ctx = $("#lineChart").get(0).getContext("2d");

let region_history_data = document.getElementById("region_sales").getAttribute("value");
console.log(region_history_data)
 $.get("/region-sales-history.json", 
    {"region_history_data" : region_history_data},
    function (data, status) {
    console.log("got data") 
let myLineChart = new Chart(ctx, {
                                        type: 'bar',
                                        data: data,
                                        options: options,
                                    })
});

let ctx1 = $("#lineChart1").get(0).getContext("2d");

let rand_sales_info = document.getElementById("rand_sales_info").getAttribute("value");
let percentile_25 = document.getElementById("25_percent").getAttribute("value");
let percentile_75 = document.getElementById("75_percent").getAttribute("value");
console.log(rand_sales_info)
 $.get('/region-prop-info.json', 
    {"rand_sales_info" : rand_sales_info},
    function (data, status) {
    console.log("got data")

    data['datasets'].push({
            "type": "line",
            "label": "25 percentile Price",
            "data": Array(data['labels'].length).fill(percentile_25),
            "fill": false
            //"data": [1400000]*data['labels'].length
            },
            {
            "type": "line",
            "label": "75 percentile Price",
            "data": Array(data['labels'].length).fill(percentile_75),
            "fill": false
            })
let myLineChart1 = new Chart(ctx1, {
                                        type: 'line',
                                        data: data,
                                        options: options1,
                                    })
});
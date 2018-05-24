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
                                        // annotation: {
                                        //              drawTime: 'afterDatasetsDraw',
                                        //               annotations: [{
                                        //                 type: 'bar',
                                        //                 drawTime: 'afterDraw',
                                        //                 mode: 'horizontal',
                                        //                 scaleID: 'y-axis-0',
                                        //                 value: 3812500.0,
                                        //                 borderColor: 'rgb(255, 99, 132)',
                                        //                 borderWidth: 4,
                                        //                 borderDash: [2, 2],
                                        //                 borderDashOffset: 5,
                                        //                 label: {
                                        //                     enabled: false,
                                        //                     content: 'Test label'
                                        //                         }
                                        //                         }]
                                        //             }
                                    }
    //                                 ,
    //                                 {
      
    //   "type": "bar",
      
      
    // }
                                    )
$('#lineLegend').html(myLineChart.generateLegend());

});
let options = { responsive: true,
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
                                        type: 'line',
                                        data: data,
                                        options: options,
                                        annotation: {
                                                     drawTime: 'afterDatasetsDraw',
                                                      annotations: [{
                                                        type: 'line',
                                                        drawTime: 'afterDraw',
                                                        mode: 'horizontal',
                                                        scaleID: 'y-axis-0',
                                                        value: 3812500.0,
                                                        borderColor: 'rgb(255, 99, 132)',
                                                        borderWidth: 4,
                                                        borderDash: [2, 2],
                                                        borderDashOffset: 5,
                                                        label: {
                                                            enabled: false,
                                                            content: 'Test label'
                                                                }
                                                                }]
                                                    }
                                    }
    //                                 ,
    //                                 {
      
    //   "type": "bar",
      
      
    // }
                                    )
$('#lineLegend').html(myLineChart.generateLegend());

});
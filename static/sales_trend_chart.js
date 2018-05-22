// let salesHistory = $("#saleshistory").val();
// console.log(salesHistory)

// console.log(sales);

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



// 


let ctx = $("#lineChart").get(0).getContext("2d");

let sales_trend_data = document.getElementById("sale_history").getAttribute("value");
 $.get("/sales-trend.json", 
    {"sales_data" : sales_trend_data},
    function (data, status) {
    console.log("got data")
let myLineChart = new Chart(ctx, {
                                        type: 'line',
                                        data: data,
                                        options: options
                                    })
$('#lineLegend').html(myLineChart.generateLegend());

});


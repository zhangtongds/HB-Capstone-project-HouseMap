let options = { responsive: true };

let ctx_donut = $("#donutChart").get(0).getContext("2d");

$.get("/melon-types.json", function (data) {
    let myDonutChart = new Chart(ctx_donut, {
                                            type: 'doughnut',
                                            data: data,
                                            options: options
                                          });
    $('#donutLegend').html(myDonutChart.generateLegend());
});

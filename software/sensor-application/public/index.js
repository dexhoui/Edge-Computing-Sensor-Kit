const host = window.location.host
var ws = new WebSocket(`ws://192.168.0.103:8885`);
let data = {
    data: DATA,
    freqs: Y
}
let data2 = {
    data: DATA2,
    freqs: Y2
}
let setCount = 0;
let rCount = 0
let flag = 0
let dm = 0
let ps = []

ws.onopen = function () {
    console.log('open')
}

ws.onmessage = function (ev) {
    // let _data = JSON.parse(ev.data);
    ps.forEach(e => {
        window.clearTimeout(e)
    })
    ps = []
    // let result = ev.data.split(',')
    let result = JSON.parse(ev.data)
    console.log(result)
    // data = data.split(',')
    // var result = [];
    // let _r = []
    // for (var i = 0, len = data.length; i < len; i += 71) {
    //     result.push(data.slice(i, i + 71));
    // }
    // for (var i = 0, len = result.length; i < len; i += 1) {
    //     _r.push(result.slice(i, i + 3));
    // }
    let container = []
    // for (let i = 0; i < result.length; i++) {
    //     container.push(group(result[i]))
    // }
    // console.log('con:', container)
    // if (_r.length > 3) {
    //     console.log('result', _r)
    //     // addData(_r)
    // }
    yb(result)
    // ori_addData(chart,result)

}

function yb(result) {
    rCount = result.length
    for (var i = 0; i < rCount; i++) {
        //闭包， 保持i值的正确性
        let p = window.setTimeout(function () {
            var group = result[i];
            var index = i;
            return function () {
                //分批渲染
                addData(chart, group, index);
                // addData(chart2,group, index);
            }
        }(), 0);
        ps.push(p)
    }
}
var chart = Highcharts.chart('container', {
    chart: {
        type: 'heatmap',
        margin: [60, 110, 80, 42],
        plotBorderWidth: 0,
        seriesBoostThreshold: 0,
        // inverted: true,
    },
    boost: {
        useGPUTranslations: true,
        usePreallocated: true
    },
    title: {
        text: 'Spectral Waterfall'
    },
    credits: {
        enabled: false
    },
    tooltip: {
        enabled: false
    },
    legend: {
        align: 'right',
        layout: 'vertical',
        margin: 0,
        verticalAlign: 'top',
        y: 25,
        symbolHeight: 280
    },
    xAxis: {
        max: 40,
        labels: {
            enabled: false,
        },
    },
    yAxis: {
        // reversed: true,
        title: '',
        lineWidth: 0,
        minorGridLineWidth: 0,
        gridLineWidth: 0,
        lineColor: 'transparent',
        minorTickLength: 0,
        tickLength: 0,
        tickWidth: 0,
        minPadding: 0,
        maxPadding: 0,
        startOnTick: true,
        endOnTick: false,
        max: 128,
        tickInterval: 1,
        labels: {
            step: 5,
            enabled: false
        }
    },
    colorAxis: {
        stops: [
            [0, '#212121'],
            [0.25, '#6A1B9A'],
            [0.6, '#4A148C'],
            [1, '#7B1FA2']
        ],
        min: -0.984,
        max: 8.1,
        startOnTick: false,
        endOnTick: false,
        labels: {
            format: '{value}'
        }
    },
    plotOptions: {
        heatmap: {
            colsize: 4,
            rowsize: 1
        }
    },
    series: [{
        name: 'Signal power',
        borderWidth: 0,
        boostThreshold: 1,
        turboThreshold: 34200,
        enableMouseTracking: false,
        data: []
    }]
});


var chart2 = Highcharts.chart('container2', {
    chart: {
        type: 'heatmap',
        margin: [60, 110, 80, 42],
        plotBorderWidth: 0,
        seriesBoostThreshold: 0,
        // inverted: true,
    },
    boost: {
        useGPUTranslations: true,
        usePreallocated: true
    },
    title: {
        text: 'Spectral Waterfall'
    },
    credits: {
        enabled: false
    },
    tooltip: {
        enabled: false
    },
    legend: {
        align: 'right',
        layout: 'vertical',
        margin: 0,
        verticalAlign: 'top',
        y: 25,
        symbolHeight: 280
    },
    xAxis: {
        max: 40,
        labels: {
            enabled: false,
        },
    },
    yAxis: {
        reversed: true,
        title: '',
        lineWidth: 0,
        minorGridLineWidth: 0,
        gridLineWidth: 0,
        lineColor: 'transparent',
        minorTickLength: 0,
        tickLength: 0,
        tickWidth: 0,
        minPadding: 0,
        maxPadding: 0,
        startOnTick: true,
        endOnTick: false,
        max: 70,
        tickInterval: 1,
        labels: {
            step: 5,
            enabled: false
        }
    },
    colorAxis: {
        stops: [
            [0, '#212121'],
            [0.25, '#6A1B9A'],
            [0.6, '#4A148C'],
            [1, '#7B1FA2']
        ],
        min: -0.984,
        max: 8.1,
        startOnTick: false,
        endOnTick: false,
        labels: {
            format: '{value}'
        }
    },
    plotOptions: {
        heatmap: {
            colsize: 4,
            rowsize: 1
        }
    },
    series: [{
        name: 'Signal power',
        borderWidth: 0,
        boostThreshold: 1,
        turboThreshold: 34200,
        enableMouseTracking: false,
        data: []
    }]
});

function createRandomValue(min, max) {
    return Math.floor(Math.random() * (max - min + 1.0)) + min;
}

function createRandomData() {
    console.log('data', data)
    processData(chart, data);
    // processData(chart2,data);
}

function group(data) {
    let result = []
    let groupItem;
    for (let i = 0; i < data.length; i++) {
        if (i % 2 == 0) {
            groupItem != null && result.push(groupItem);
            groupItem = [];
        }
        groupItem.push(data[i]);
    }
    result.push(groupItem);
    return result;
}
var currIndex = 0;
let batch = 0;

Date.prototype.format = function (fmt) {
    var o = {
        "M+": this.getMonth() + 1, //月份 
        "d+": this.getDate(), //日 
        "h+": this.getHours(), //小时 
        "m+": this.getMinutes(), //分 
        "s+": this.getSeconds(), //秒 
        "q+": Math.floor((this.getMonth() + 3) / 3), //季度 
        "S": this.getMilliseconds() //毫秒 
    };
    if (/(y+)/.test(fmt)) {
        fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
    }
    for (var k in o) {
        if (new RegExp("(" + k + ")").test(fmt)) {
            fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
        }
    }
    return fmt;
}

function ori_addData(chart, data) {
    let ff = false
    for (var i = 0; i < data.length; i++) {

        for (let j = 0; j < data[0].length; j++) {
            // console.log("data.data[i][j]]", data.data[i][j])
            if (i == data.length - 1) {
                ff = true
            }
            if (ff) {
                chart.series[0].addPoint([i, j, data[i][j]], false, true);
            } else {
                chart.series[0].addPoint([i, j, data[i][j]], false, false);

            }
        }


    }
    chart.redraw();

}

function addData(chart, data, index) {
    console.log('curr', currIndex)
    if (currIndex == rCount - 1) {
        flag = 1
        dm = data.length - 1
        batch++
    }
    if (currIndex == rCount - 1) {
        currIndex = 0
        let parent = document.querySelector('#p')
        var p = document.createElement("p");
        parent.append(new Date().format("hh:mm:ss.S"), p);

    }
    while (index - currIndex == 1) {
        currIndex = index;
        if (flag) {
            chart.update({
                xAxis: {
                    max: chart.xAxis[0].max + 1,
                    // min: chart.xAxis[0].min + 1,
                },
                //     yAxis: {
                //         //  max: chart.yAxis[0].max + 1,
                //         // min: chart.yAxis[0].min + 1,
                //     }
            }, true);
            for (let i = 0; i < data.length; i++) {
                chart.series[0].addPoint([74 * batch + i, index, data[i]], false, true);
            }
        } else {
            for (let i = 0; i < data.length; i++) {
                chart.series[0].addPoint([i, index, data[i]], false, false);
            }
        }
        chart.redraw();
    }
}

function t_removeP() {
    chart.series[0].removePoint(rCount--, true);
    for (let i = 0; i < 1; i++) {
        chart.series[0].addPoint([i, 129, DATA[0][0]], false, false);
    }
    chart.update({
        yAxis: {
            max: chart.yAxis[0].max - 1,
        }
    }, true);
}

function processData(chart, data) {
    var newData = [];
    for (var i = 0; i < data.data.length; i++) {
        for (let j = 0; j < data.data[0].length; j++) {
            // console.log("data.data[i][j]]", data.data[i][j])
            chart.series[0].addPoint([i, j, data.data[i][j]], false, false);
        }
        chart.redraw();


    }
    // console.log('iii', chart.series[0])
    // if (i) {
    //     chart.update({
    //         yAxis: {
    //             max: chart.yAxis[0].max - 1
    //         }
    //     }, false);
    // }
    // chart.redraw();
}
// createRandomData();
$('#button2').click(() => {
    setInterval(() => {

    }, 10);
    t_removeP()

})
$('#button').click(function () {
    createRandomData();
    // console.log('data', Math.min(...([].concat.apply([], DATA))), Math.max(...([].concat.apply([], DATA))))
    // console.log('Y', Math.min(...Y), Math.max(...Y))
});
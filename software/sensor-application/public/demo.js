const host = window.location.host
var ws = new WebSocket(`ws://192.168.0.103:8885`);
let setCount = 0;
let rCount = 0
let flag = 0
let dm = 0
let ps = []
var y = 64
let nmax = 10
let nmin = 0
let accMax = 30
let accMin = 5
ws.onopen = function () {
    console.log('open')
}

let mpuBatchs = 0
let audioBatchs = 0
ws.onmessage = function (ev) {
    // let _data = JSON.parse(ev.data);
    ps.forEach(e => {
        window.clearTimeout(e)
    })
    ps = []
    // let result = ev.data.split(',')

    let data = JSON.parse(ev.data)
    // console.log('audio', data.audioResult)
    // console.log('mpu', data.mpuResult)
    document.querySelector('#btn').innerHTML = data.active
    y = data.audioResult[0].length
    // y2 = data.mpuResult[0].length
    y2 = data.xResult[0].length
    // console.log('y,', y)
    // yb(data.audioResult, data.mpuResult)
    yb(data.audioResult, data.xResult,data.yResult,data.zResult,data.laserResult)
    // ya(data)

}
var app = {};
var chartDom = document.getElementById('main');
var accDom_x = document.getElementById('acc_x');
var accDom_y = document.getElementById('acc_y');
var accDom_z = document.getElementById('acc_z');
var laserDom = document.getElementById('laser');
var accChart = echarts.init(accDom_x);
var accChartY = echarts.init(accDom_y);
var accChartZ = echarts.init(accDom_z);
var myChart = echarts.init(chartDom);
var laserChart = echarts.init(laserDom);
// var accChart = null;
let charts = [myChart, accChart]

var xData = [];
var yData = [];
var audioCurrentIndex = 0;
var mpuCurrentIndex = 0;
audioTag = myChart.id
mpuTag = accChart.id
// var data = generateData(2, -5, 5);
const cgrid = {
    x: 2,
    y: 2,
    x2: 2,
    y2: 2,
};
const option = {
    title:{
        text: "Microphone",
        right:0,
        top:0,
        textStyle:{
        color:'#fff',
        }
    },
    xAxis: {
        splitLine: {
            show: false
        },
        type: 'category',
        show: false,
        data: []
    },
    yAxis: {
        splitLine: {
            show: false
        },
        show: false,
        type: 'category',
        data: []
    },
    grid: cgrid,
    visualMap: {
        show: false,
        type: 'continuous',
        min: nmin,
        max: nmax,
        calculable: true,
        realtime: false,
        opacity: 1,
        inRange: {
            color: ['#212121', '#6A1B9A', 'rgba(50,28,146,1)']
        }
    },
    series: [{
        name: 'Gaussian',
        type: 'heatmap',
        showSymbol:false,
        data: [],
        progressive: 11000,
        progressiveThreshold: 11088,
        animation: false
    }]
};

function doRemove() {
    chart.series.data.shift()
}


const accOption = {
    title:{
        text: "Acceleration-X",
        right:0,
        top:0,
        textStyle:{
        color:'#fff',
        }
    },
    xAxis: {
        splitLine: {
            show: false
        },
        type: 'category',
        show: false,
        data: xData
    },
    grid: cgrid,
    yAxis: {
        splitLine: {
            show: false
        },
        show: false,
        type: 'category',
        data: yData
    },
    visualMap: {
        show: false,
        type: 'continuous',
        min: accMax,
        max: accMin,
        calculable: true,
        realtime: false,
        opacity: 0.5,
        inRange: {
            color: ['#212121', '#EF6C00', '#E65100']
        }
    },
    series: [{
        name: 'Gaussian',
        type: 'heatmap',
        showSymbol:false,
        data: [],
        progressive: 11000,
        progressiveThreshold: 11088,
        animation: false
    }]
};
const accOptionY = {
    title:{
        text: "Acceleration-Y",
        right:0,
        top:0,
        textStyle:{
        color:'#fff',
        }
    },
    xAxis: {
        splitLine: {
            show: false
        },
        type: 'category',
        show: false,
        data: xData
    },
    grid: cgrid,
    yAxis: {
        splitLine: {
            show: false
        },
        show: false,
        type: 'category',
        data: yData
    },
    visualMap: {
        show: false,
        type: 'continuous',
        min: accMax,
        max: accMin,
        calculable: true,
        realtime: false,
        opacity: 0.5,
        inRange: {
            color: ['#212121', '#76FF03', '#64DD17']
        }
    },
    series: [{
        name: 'Gaussian',
        type: 'heatmap',
        data: [],
        showSymbol:false,
        progressive: 11000,
        progressiveThreshold: 11088,
        animation: false
    }]
};
const accOptionZ = {
    title:{
        text: "Acceleration-Z",
        right:0,
        top:0,
        textStyle:{
        color:'#fff',
        }
    },
    xAxis: {
        splitLine: {
            show: false
        },
        type: 'category',
        show: false,
        data: xData
    },
    grid: cgrid,
    yAxis: {
        splitLine: {
            show: false
        },
        show: false,
        type: 'category',
        data: yData
    },
    visualMap: {
        show: false,
        type: 'continuous',
        min: accMax,
        max: accMin,
        calculable: true,
        realtime: false,
        opacity: 0.1,
        inRange: {
            color: ['#212121', '#C6FF00', '#AEEA00']
        }
    },
    series: [{
        name: 'Gaussian',
        type: 'heatmap',
        showSymbol:false,
        data: [],
        progressive: 11000,
        progressiveThreshold: 11088,
        animation: false
    }]
};

const laserOption = {
    title:{
        text: "Laser",
        right:0,
        top:0,
        textStyle:{
        color:'#fff',
        }
    },
    xAxis: {
        splitLine: {
            show: false
        },
        type: 'category',
        show: false,
        data: xData
    },
    grid: cgrid,
    yAxis: {
        splitLine: {
            show: false
        },
        show: false,
        type: 'category',
        data: yData
    },
    visualMap: {
        show: false,
        type: 'continuous',
        min: 0,
        max: 2,
        calculable: true,
        realtime: false,
        opacity: 0.1,
        inRange: {
            color: ['#212121', '#C6FF00', '#AEEA00']
        }
    },
    series: [{
        name: 'Gaussian',
        type: 'heatmap',
        showSymbol:false,
        data: [],
        progressive: 11000,
        progressiveThreshold: 11088,
        animation: false
    }]
};

option && myChart.setOption(option);
accOption && accChart.setOption(accOption);
accOptionY && accChartY.setOption(accOptionY);
accOptionZ && accChartZ.setOption(accOptionZ);
laserOption && laserChart.setOption(laserOption);

function yb(audioResult, xResult,yResult,zResult,laserResult) {
    rCount = audioResult.length
    for (var i = 0; i < rCount; i++) {
        //闭包， 保持i值的正确性
        let p = window.setTimeout(function () {
            var audioGroup = audioResult[i];
            // var mpuGroup = mpuResult[i];
            let xGroup = xResult[i]
            let yGroup = yResult[i]
            let zGroup = zResult[i]
            let laserGroup = laserResult[i]
            var index = i;
            return function () {
                //分批渲染
                addData(audioBatchs, myChart, option, audioGroup, xGroup,yGroup,zGroup,laserGroup, index)
                // addData2(mpuBatchs, accChart, accOption, mpuGroup, index)
                // addData(chart, group, index);
                // addData(chart2,group, index);
            }
        }(), 0);
        ps.push(p)
    }
}


function range(min, max) {
    let arr = [];
    for (let i = min; i <= max; i++) {
        arr.push(i);
    }
    return arr;
}
var cc = 0
let ccount = 128;
function addData(batch, charts, options, audioGroup,xGroup,yGroup,zGroup,laserGroup, index) {
    // console.log('charts.id', charts.id)'
    if (charts.id == audioTag) {
        if (audioCurrentIndex == rCount - 1) {
            audioCurrentIndex = 0
            // let parent = document.querySelector('#p')
            // var p = document.createElement("p");
            // parent.append(new Date().format("hh:mm:ss.S"), p);
            // batch++
            audioBatchs++

        }
        while (index - audioCurrentIndex == 1) {
            audioCurrentIndex = index;
            // console.log(batch,audioCurrentIndex,index)
            // var data1 = option.series[0].data;
            console.log(batch * (rCount - 1) + index)
            for (var j = 0; j < y; j++) {
                // var x = (max - min) * i / 200 + min;
                // var y = (max - min) * j / 100 + min;
                if (batch * (rCount - 1) + index > 12*(rCount)) {

                    option.series[0].data.shift()
                    accOption.series[0].data.shift()
                    accOptionY.series[0].data.shift()
                    accOptionZ.series[0].data.shift()
                    laserOption.series[0].data.shift()

                    option.xAxis.data = []
                    accOption.xAxis.data = []
                    accOptionY.xAxis.data = []
                    accOptionZ.xAxis.data = []
                    laserOption.xAxis.data = []
                }
                    
                option.series[0].data.push([batch * (rCount - 1) + index, j, audioGroup[j]]);
                accOption.series[0].data.push([batch * (rCount - 1) + index, j, xGroup[j]]);
                accOptionY.series[0].data.push([batch * (rCount - 1) + index, j, yGroup[j]]);
                accOptionZ.series[0].data.push([batch * (rCount - 1) + index, j, zGroup[j]]);
                laserOption.series[0].data.push([batch * (rCount - 1) + index, j, laserGroup[j]]);
                // console.log('2', accOption.series[0].data)
                // debugger;

                // data.push([ccount, j, noise.perlin2(ccount / 40, j / 20) + 0.5]);
                // data.push([i, j, normalDist(theta, x) * normalDist(theta, y)]);
            }

            if (batch == 12) {
                console.log('1', option.series[0].data)

                // console.log(accOption.series[0].data)
                // debugger
            }


            myChart.setOption(option);
            accChart.setOption(accOption)
            accChartY.setOption(accOptionY)
            accChartZ.setOption(accOptionZ)
            laserChart.setOption(laserOption)
            // data0.push(Math.round(Math.random() * 1000));
            // option.series[0].data = data0

        }
    }
}


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
const express = require('express');
const expressWs = require('express-ws');
const bodyParser = require('body-parser')
const exphbs = require('express-handlebars');
const WebSocket = require('ws');
const http = require('http');
const path = require('path');
const app = express();
const {CONFIGER} = require('./conf')
const {
    DATA,
    DATA2,
    Y,
    Y2
} = require('./data');
app.use(express.static('public'));
app.use(express.json({
    limit: '50mb'
}));

app.engine('html', exphbs({
    layoutsDir: 'views',
    defaultLayout: 'layout',
    extname: '.html'
}));
app.set('view engine', 'html');
// create application/json parser
var jsonParser = bodyParser.json()
// create application/x-www-form-urlencoded parser
var urlencodedParser = bodyParser.urlencoded({
    extended: false
})
// expressWs(app);

const WebSocketServer = require("ws").Server;
const wss = new WebSocketServer({
    port: 8885
});
// wsList=[]
let curWS = null
wss.on("connection", (ws) => {
    curWS = ws
    console.info("websocket connection open");
    ws.on('message', (message) => {
        console.log('websocket received: %s', message);
    });
    ws.on('close', () => {
        // deleteWebsocket(ws)
        console.log('websocket close.')
    })
    ws.on('error', (err) => {
        // deleteWebsocket(ws)
        console.log('websocket error.', err)
    })
    if (ws.readyState === ws.OPEN) {}
});
let currentData = {}
app.get('/heat', function (req, res) {
    res.render('heatmap', {
        layout: false,
        title: "首页",
        DATA,
        DATA2,
        Y,
        Y2
    });
});
app.get('/', function (req, res) {
    res.render('demo', {
        layout: false,
        title: "测试",
    });
});
// app.ws('/ws', function (ws, req) {
//     ws.send(currentData)

//     ws.on('message', function (msg) {
//         // 业务代码
//         ws.send(currentData)
//         console.log('msg', msg)
//     })
// })

app.post('/', jsonParser, (req, res) => {
    // console.log('res', req.body.data)
    try {
        console.log('req', req.body)

        let audioData = req.body.audio
        let mpuData = req.body.mpu
        let active = req.body.active
        let xData = req.body.x
        let yData = req.body.y
        let zData = req.body.z
        let laserData = req.body.l
        let packs = CONFIGER.package
        // currentData = data
        let audioResult = []
        let mpuResult = []
        let xResult = []
        let yResult = []
        let zResult = []
        let laserResult = []
        let body = {}

        if (curWS != null) {
            active = active.toString()
            audioData = audioData.toString().split(',')
            // mpuData = mpuData.toString().split(',')

            xData = xData.toString().split(',')
            yData = yData.toString().split(',')
            zData = zData.toString().split(',')
            laserData = laserData.toString().split(',')

            for (var i = 0, len = audioData.length; i < len; i += packs) {
                audioResult.push(audioData.slice(i, i + packs));
                xResult.push(xData.slice(i, i + packs));
                yResult.push(yData.slice(i, i + packs));
                zResult.push(zData.slice(i, i + packs));
                laserResult.push(laserData.slice(i, i + packs));
                // mpuResult.push(mpuData.slice(i, i + packs));
            }

            // result = result.filter((e,index)=>{
            //      return index%2==0?true:false
            // })
            body.audioResult = audioResult
            // body.mpuResult = mpuResult
            body.xResult = xResult
            body.yResult = yResult
            body.zResult = zResult
            body.laserResult = laserResult
            body.active = active.toString()
            console.log(body)
            curWS.send(JSON.stringify(body))

        }
        res.send('Hello from App Engine!');
    } catch (error) {
        console.log('error:', error)
    }

});
// 匹配/about路由
app.get('/about', function (req, res) {
    res.type('text/plain');
    res.send('访问了about页面');
});


// 定制 404 页面 (返回404状态码)
app.use(function (req, res) {
    let currentTime = new Date();
    res.type('text/plain');
    res.status(404);
    res.send('404 - 你访问的页面可能去了火星\n' + currentTime);
});


//定制 500 页面 (返回500状态码)
app.use(function (err, req, res, next) {
    let currentTime = new Date();
    let errInfo = err.stack;
    res.type('text/plain');
    res.status(500);
    res.send('500 - 服务器发生错误\n' + 'errInfo:' + errInfo + '\n' + 'currentTime:' + currentTime);
});

// Listen to the App Engine-specified port, or 8080 otherwise
const PORT = process.env.PORT || 8889;
app.listen(PORT, () => {
    console.log(`Server listening on port ${PORT}...`);
});
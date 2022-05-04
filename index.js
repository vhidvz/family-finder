let { FamilyFinder } = require('./wrapper')
const express = require('express')
const redis = require('redis');
const sha1 = require('sha1');
const fs = require('fs')
const app = express()

let client = redis.createClient();
const port = process.env.PORT || 3000

app.use(express.json())
app.use(express.static('assets'))
app.use(express.urlencoded({ extended: true }))

function queryParser(query) {
    if (!query.match(/((\w+:[&|]?(\w+[@+.]?)+)[\s]?)+/g))
        return [null, null]
    var site = query.match(/\w*(site)[:]\w+[.]?\w+/g)
    if (site != null) {
        _site = site[0]
        if (/\w*(site)[:]\w+[.]\w+/g.test(_site)) {
            site = _site.split(':')[1]
        } else {
            site = null
        }
        query = query.replace(/\w*(site)[:]\w+[.]?\w+\s*/g, '')
    }
    return [site, query]
}

app.all('/information', (req, res) => {
    _json = fs.readFileSync('./websites/Info.json', 'utf8')
    res.send(JSON.parse(_json))
})

app.get('/:query?', (req, res) => {
    if (!req.params.query) {
        html = fs.readFileSync('./home.html', 'utf8')
        res.send(html)
    } else {
        [site, query] = queryParser(req.params.query)
        if (query != null) {
            _sha1 = sha1(req.params.query)
            client.exists('key', function (err, reply) {
                if (reply === 1) {
                    client.get(_sha1, function (err, data) {
                        if (err) throw err;
                        res.send(JSON.parse(data))
                    });
                } else {
                    FamilyFinder(site, query, function (err, data) {
                        if (err) throw err;
                        client.set(_sha1, JSON.stringify(data))
                        client.expire(_sha1, 21600)
                        res.send(data)
                    })
                }
            });
        }
        else {
            html = fs.readFileSync('./home.html', 'utf8')
            res.send(html)
        }
    }
})

app.post('/', (req, res) => {
    [site, query] = queryParser(req.body.query)
    if (query != null) {
        _sha1 = sha1(req.body.query)
        client.exists(_sha1, function (err, reply) {
            if (err) throw err;
            if (reply === 1) {
                client.get(_sha1, function (err, data) {
                    if (err) throw err;
                    res.send(JSON.parse(data))
                });
            } else {
                FamilyFinder(site, query, function (err, data) {
                    if (err) throw err;
                    client.set(_sha1, JSON.stringify(data))
                    client.expire(_sha1, 21600)
                    res.send(data)
                })
            }
        });
    }
    else {
        res.send({ "status": 400, "message": "Bad Request error." })
    }
})

app.listen(port, () => console.log(`Example app listening on port ${port}!`))
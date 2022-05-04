const fs = require('fs');
let { PythonShell } = require('python-shell')

let Info = JSON.parse(fs.readFileSync('./websites/Info.json', 'utf8'));

function argify(site, args) {
  args = args.trim()
  args = args.replace(/\s*(?::)\s*/g, ':')
  args = args.replace(/\s+(?!:)\s+/g, ' ')

  if (args == '') {
    throw 400, 'Bad Request error.'
  }

  var params = []
  if (site != null && Info['_sites'].includes(site)) {
    params.push('--site', site)
  }

  str = '-string='
  args.split(' ').forEach(element => {
    el = element.split(':')
    if (Info['_support'].includes(el[0])) {
      params.push('-' + el[0], el[1])
    } else {
      str += el[0] + ':' + el[1] + '&'
    }
  })
  str = str.substr(0, str.length - 1)
  if (str != '-string') {
    params.push(str)
  }

  for (i = 0; i < params.length; i++) {
    if (params[i].includes('+')) {
      params[i] = params[i].replace(/[+]/g, ' ')
    }
  }

  return params
}

module.exports.FamilyFinder = function (site, args, callback) {
  PythonShell.run('pkglunch.py', { args: argify(site, args) }, function (err, results) {
    callback(err, JSON.parse(results))
  })
}

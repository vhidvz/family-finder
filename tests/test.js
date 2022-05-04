let { FamilyFinder } = require('../wrapper')

FamilyFinder('locatefamily.com', "phone:44000000000 name:Clark location:UK", function (err, results) {
    if (err) throw err;
    // results is an array consisting of messages collected during execution
    console.log('results: %j', results);
})
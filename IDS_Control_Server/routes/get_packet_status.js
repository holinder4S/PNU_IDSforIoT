var express = require('express');
var router = express.Router();

router.get('/weekly_packet_mapreduce', function(request, response) {

    var MongoClient = require('mongodb').MongoClient, assert = require('assert');
    var url = 'mongodb://localhost:26543/packet_data';

    MongoClient.connect(url, function(err, db) {
        assert.equal(null, err);
        console.log("connected successfully to server");

        var map = function() {
            emit(this.week, {packet_amount: this.packet_amount, vul_amount: this.vul_amount});  
        };

        var reduce = function(keyWeek, values) {
                var packet_amount = 0;
                var vul_amount = 0;
            values.forEach(function(value) {
                    packet_amount += value.packet_amount;
                    vul_amount += value.vul_amount;
            })

            return {packet_amount : packet_amount, vul_amount : vul_amount};
        };

        db.collection('daily_packet').mapReduce(
            map,
            reduce,
            { out : 'daily_temp' },
            function(err, coll) {
                    coll.find().toArray(function(err, arr) {
                        console.log(arr);
                        response.send(arr);
                    });
            }
        );
    });
});

router.get('/get_daily_packet', function(req, res, next) {
    var MongoClient = require('mongodb').MongoClient, assert = require('assert');
    var url = 'mongodb://localhost:26543/packet_data';
    MongoClient.connect(url, function(err, db) {
        assert.equal(null, err);
        console.log("connected successfully to server");
        db.listCollections({name: 'daily_packet'}).next(function(err, collinfo) {
            if (collinfo) {
                db.collection('daily_packet').find({}).toArray(function(err, results) {
                    console.log(results);
                    res.send(results);
                })
            } else {
                console.log('not exist, reload');
            }
        })
    })
});

/* GET home page. */
router.get('/get_packetsource_location', function(request, response, next) {

    var MongoClient = require('mongodb').MongoClient, assert = require('assert');
    var url = 'mongodb://localhost:26543/packet_data';

    MongoClient.connect(url, function(err, db) {
        assert.equal(null, err);
        console.log("connected successfully to server");
        var dt = new Date();
        function dateToYYYYMMDD(date){
            function pad(num) {
                num = num + '';
                return num.length < 2 ? '0' + num : num;
            }
            return pad(date.getMonth()+1) + pad(date.getDate());
        }

        var search_created_at = dateToYYYYMMDD(dt);
        var coll_name = search_created_at + 'geo_data';
        console.log(coll_name);

        var map = function() {
            emit({lat: this.lat, lon: this.lon},  this);   
        };

        var reduce = function(keyHour, values) {
            var count = 0;

            values.forEach(function(value) {
                    count += 1;
            })

            return {count: count};
        };

        db.collection(coll_name).mapReduce(
            map,
            reduce,
            { out : 'location_temp_data'},
            function(err, coll) {
                coll.find().toArray(function(err, arr) {
                    console.log(arr);
                    response.send(arr);
                });
            }
        );
    });
});


router.get('/get_manufacture_list', function(request, response) {

    var MongoClient = require('mongodb').MongoClient, assert = require('assert');
    var url = 'mongodb://localhost:26543/packet_data';

    MongoClient.connect(url, function(err, db) {
        assert.equal(null, err);
        console.log("connected successfully to server");
        var dt = new Date();
        function dateToYYYYMMDD(date){
            function pad(num) {
                num = num + '';
                return num.length < 2 ? '0' + num : num;
            }
            return pad(date.getMonth()+1) + pad(date.getDate());
        }

        var search_created_at = dateToYYYYMMDD(dt);
        var coll_name = search_created_at + 'manufacture';
        console.log(coll_name);

        var map = function() {
	        emit(this.manufacture, {count: 1});	
        };

        var reduce = function(keyHour, values) {
	        var count = 0;

	        values.forEach(function(value) {
	        		count += 1;
	        })

            return {count: count};
        };

        db.collection(coll_name).mapReduce(
            map,
            reduce,
            { out : 'manufacture_temp_data',
            sort : {'count':1}},
            function(err, coll) {
            		coll.find().toArray(function(err, arr) {
            			console.log(arr);
            			response.send(arr);
            		});
            }
        );
    });
});

module.exports = router;

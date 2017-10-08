var express = require('express');
var router = express.Router();

/* GET home page. */
router.get('/get_server_load', function(req, res, next) {
	var MongoClient = require('mongodb').MongoClient, assert = require('assert');
	var url = 'mongodb://localhost:26543/server_data';
	MongoClient.connect(url, function(err, db) {
		assert.equal(null, err);
		console.log("connected successfully to server");
		db.listCollections({name: 'now_stat'}).next(function(err, collinfo) {
			if (collinfo) {
				db.collection('now_stat').find({}).toArray(function(err, results) {
					console.log(results);
					res.send(results);
				})
			} else {
				console.log('not exist, reload');
			}
		})
	})
});


router.get('/usage_mapreduce', function(request, response) {

    var MongoClient = require('mongodb').MongoClient, assert = require('assert');
    var url = 'mongodb://localhost:26543/server_data';

    MongoClient.connect(url, function(err, db) {
        assert.equal(null, err);
        console.log("connected successfully to server");
        var dt = new Date();
        dt.setDate(dt.getDate() - 1);
        function dateToYYYYMMDD(date){
            function pad(num) {
                num = num + '';
                return num.length < 2 ? '0' + num : num;
            }
            return pad(date.getMonth()+1) + pad(date.getDate());
        }

        var search_created_at = dateToYYYYMMDD(dt);
        console.log(search_created_at);

        var map = function() {
	        emit(this.hour, this);	
        };

        var reduce = function(keyHour, values) {
	        var cpu = 0;
	        var ram = 0;
	        var network = 0;
	        var count = 0;

	        values.forEach(function(value) {
	        		cpu += value.cpu;
	        		ram += value.ram;
	        		network += value.network;
	        		count += 1;
	        })

	        cpu /= count;
	        ram /= count;
	        network /= count;

            return {cpu : cpu, ram : ram, network : network};
        };

        db.collection(search_created_at).mapReduce(
            map,
            reduce,
            { out : 'temp_data' },
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

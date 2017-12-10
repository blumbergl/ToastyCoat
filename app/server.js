// adapted from https://zellwk.com/blog/crud-express-mongodb/
const express = require('express');
const app = express();
const bodyParser = require('body-parser');
var request = require('request');
var config = require('config');
var ThingSpeakClient = require('thingspeakclient');


var client = new ThingSpeakClient();
var channelId = 377665;
var tsPrefsReadKey = config.get('ThingspeakPrefs.read_key');
var tsPrefsWriteKey = config.get('ThingspeakPrefs.write_key');
var weatherReadKey = config.get('weather.api_key');
client.attachChannel(channelId, { writeKey: tsPrefsWriteKey, readKey: tsPrefsReadKey}, function() { console.log("thingspeak callback");});

app.listen(process.env.PORT || 3000, () => {
  console.log('listening on 3000')
})


app.set('view engine', 'ejs');
app.use(bodyParser.urlencoded({extended: true}));
app.use(bodyParser.json());
app.use(express.static('public'));


app.get('/', (req, res) => {

  // adapted from http://shiffman.net/a2z/server-node/
  var url = "https://api.wunderground.com/api/" + weatherReadKey + "/geolookup/conditions/q/MA/Cambridge.json";

  // Execute the HTTP Request
  request(url, loaded);

  // Callback for when the request is complete
  function loaded(error, response, body) {
    // Check for errors
    if (!error && response.statusCode == 200) {
      var parsed_body = JSON.parse(body);
      var location = parsed_body['location']['city'];
      var temp_f = parsed_body['current_observation']['temp_f'];
      var weather = parsed_body['current_observation']['weather']
    } else {
      console.log("error");
    }
    client.getLastEntryInChannelFeed(channelId, {}, function(err, resp) {
      res.render('index.ejs', {'temp': resp['field1'], 'gestures': resp['field2'], 'location': location, 'temp_f': temp_f, 'weather': weather});
    });
  }

})

app.get('/:temp_pref',  function (req, res) {
  console.log("temp_pref route called");
  client.getLastEntryInChannelFeed(channelId, {}, function(err, resp) {
   res.json({
      'temp': resp['field1'],
      'gestures': resp['field2']
    });
  });
});


app.put('/prefs', (req, res) => {
 client.updateChannel(channelId, {field1: req.body.temp, field2: req.body.gestures}, function(err, resp) {
    if (!err && resp > 0) {
        console.log('update ' + req.body.name + ' successfully to ' + req.body.temp + '. Entry number was: ' + resp);
    } else {
      console.log(err);
    }
});

})



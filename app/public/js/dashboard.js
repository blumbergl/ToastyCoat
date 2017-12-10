/*function getVals(){
  // Get slider values
  var parent = this.parentNode;
  var slides = parent.getElementsByTagName("input");
    var slide1 = parseFloat( slides[0].value );
    var slide2 = parseFloat( slides[1].value );
  // Neither slider will clip the other, so make sure we determine which is larger
  if( slide1 > slide2 ){ var tmp = slide2; slide2 = slide1; slide1 = tmp; }
  
  var displayElement = parent.getElementsByClassName("rangeValues")[0];
      displayElement.innerHTML = slide1 + " - " + slide2;
}*/

function displayTempPref() {
  var tempPref = $("#custom-handle").text();
  console.log(JSON.stringify(tempPref));
}

function getGesturePref() {
  return $('#gest_switch').is(':checked');
}

function writeGestPrefData(gest) {
  //firebase.database().ref('gestures/').set({
  //  "val": gest
 // });
}

function writeTempPrefData() {
  var temp = $("#custom-handle").text();
  // TODO call mongo db?

 // firebase.database().ref('temp_pref/').set({
 //   "val": temp
 // });
}

function getTempScale() {
  var temp_scale = $('#temp_scale').is(':checked');
  console.log("temp_scale = " + temp_scale);
  console.log($('.slider_temp').text());
  if (temp_scale == false) {
    return "F";
  } else if (temp_scale == true) {
    return "C";
  }
}

function getWeather() {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "http://api.wunderground.com/api/f79586c591419f41/conditions/q/CA/San_Francisco.json", true);
    xhr.responseType = 'text';
    //xhttp.setRequestHeader("Content-type", "application/json");
    xhr.send();
    //var response = JSON.parse(xhttp.responseText);
    //return response;
    console.log(xhr.status);
    console.log(xhr.responseText);
   //console.log(response);
}

window.onload = function(){
  // Initialize Sliders
  var sliderSections = document.getElementsByClassName("range-slider");
      for( var x = 0; x < sliderSections.length; x++ ){
        var sliders = sliderSections[x].getElementsByTagName("input");
        for( var y = 0; y < sliders.length; y++ ){
          if( sliders[y].type ==="range" ){
            sliders[y].oninput = getVals;
            // Manually trigger event first time to display values
            sliders[y].oninput();
          }
        }
      }
}


/* globals fetch */
var update_temp = document.getElementById('temp-input');
var update_gestures = document.getElementById('gest_switch');
var del = document.getElementById('delete');
var lastTemp = $('#temp-input').val(); 

// adapted from https://stackoverflow.com/questions/34354975/refresh-section-of-a-page-using-ejs-and-express
function refreshTempPref() {
  console.log("refreshTempPref called");
  var curr_ui_temp = $('#temp-input').val();
  if (curr_ui_temp != lastTemp) {
    updateTempPreferences();
  } else { // see if it was updated on the jacket
    console.log("see if updated on jacket");
    $.ajax({
      type: 'GET',
      url: '/' + "temp_pref",
      success: function(data) {
        console.log("new temp = " + data.temp);
        $('#temp-input').val(data.temp); 
        if (data.temp > lastTemp) {
          $('#temp-input').stop().css("background-color", "#ffb39b")
            .animate({ backgroundColor: "#FFFFFF"}, 1500);
        } else if (data.temp < lastTemp) {
          $('#temp-input').stop().css("background-color", "#9bd0ff")
            .animate({ backgroundColor: "#FFFFFF"}, 1500);
        }
      }
    });
  } 
}


update_gestures.addEventListener('click', function () {
  console.log("update_gestures listener called");
  var gest_val = $('#gest_switch').is(':checked');
  var temp_val = $( "#temp-input" ).val();
  fetch('prefs', {
    method: 'put',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      'name': 'gestures',
      'gestures': gest_val,
      'temp': temp_val
    })
  })
  .then(response => {
    if (response.ok) return response.json()
  })
  .then(data => {
    console.log(data)
  })
})

function updateTempPreferences() {
  //setTimeout(function(){ console.log("waiting"); }, 20000);
  var gest_val = $('#gest_switch').is(':checked');
  var temp_val = $( "#temp-input" ).val();
  console.log("will put " + temp_val);
  lastTemp = temp_val;
  fetch('prefs', {
    method: 'put',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      'name': 'temp',
      'gestures': gest_val,
      'temp': temp_val
    })
  })
  .then(response => {
    if (response.ok) return response.json()
  })
  .then(data => {
    console.log(data);

  })
}

update_temp.addEventListener('click', function(event) {
  console.log("update_temp listener called");
  clearInterval(intervalID);
  $(this).clearQueue();
  //someAsynchronousFunction();
  //setTimeout(function(){ console.log("waiting"); }, 20000);
 /* var gest_val = $('#gest_switch').is(':checked');
  var temp_val = $( "#temp-input" ).val();
  fetch('prefs', {
    method: 'put',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      'name': 'temp',
      'gestures': gest_val,
      'temp': temp_val
    })
  })
  .then(response => {
    if (response.ok) return response.json()
  })
  .then(data => {
    console.log(data);

  })*/
  intervalID = window.setInterval(refreshTempPref, interval_period);
}) 

var interval_period = 5000;
var intervalID = window.setInterval(refreshTempPref, interval_period);




== General functionalties needed ==

* Microcontroller gets user preferences from web app (GET call to /prefs_temp and /prefs_gestures) -- ()
* Microcontroller posts user preferences (from gestures) to website (PUT call to /prefs_temp) (for temperature preferences). Website updates sliders accordingly.
* Microcontroller sends data from sensors to Thingspeak --> data displayed on website (DONE!)



*  Microcontroller gets user preferences from Thingspeak on each loop (to see if changed in web app) (using HTTP)
* Microcontroller posts user preferences (from gestures) to Thingspeak (for temperature preferences). Website updates sliders accordingly (calling Thingspeak or using graphs?) (using MQTT)
* Microcontroller sends data from sensors to Thingspeak --> data displayed on website (DONE!)

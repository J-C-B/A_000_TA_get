# A_000_TA_get
Get web API data into Splunk

This Splunk app was used in my Darksky Photographie Splunk app and demonstrated in my .conf 2017 talk:

Take a talk into the art of dark sky photography with a splunk ninja

https://conf.splunk.com/files/2017/slides/take-a-talk-into-the-art-of-dark-sky-photography-with-a-splunk-ninja.pdf

1. Install:
Install as usual in the Splunk web or copy into $SPLUNK_HOME/etc/apps

2. Configure:
Moon API - nothing to do here, move along.
Weather API - get your API key from http://api.openweathermap.org and use the Splunk web to configure the input.
Google directions - get your API key from https://developers.google.com/maps/documentation/directions/get-api-key and use the Splunk web to configure the input.

3. Usage:
Use the custom search command `get` to eihter get moon data (| get me=moon ), weater ( | get me=weather ... ) or Google directions ( | get me=dircetions ... )


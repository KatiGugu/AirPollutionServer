# AirPollutionServer
Air pollution information server is a small program developed using of technology asynchronous
programming  that, through HTTP requests, allows you to get air pollution data by point coordinates or city name/zip code . 
The data is provided through the openweathermap.com service. The API contains only three types of Get requests:

http:// HostName:Port /pollution?city={city name}&country={country code}&forecust={True/False}, 

where

city name – name of city

country – country code  ISO 3166 international standard (Alpha-2 code)

forecast – if True, you will get a forecast for 5 days, if False, then only the current data.

http://HostName:Port /pollution?zip={zip/post code}&country={country code},

where

zip - zip/post code

country – country code  ISO 3166 international standard (Alpha-2 code)

http://HostName:Port/pollution?lon={longitude}&lat={latitude}

where

lon, lat - geographical coordinates (latitude, longitude)


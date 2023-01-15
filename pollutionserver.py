import config
import json
import asyncio
from aiohttp import ClientSession, web


app_session = None
#The key may be blocked by openweathermap.com. You should get your own key. It's free.
API_key = '2a4ff86f9aaa70041ec8e82db64abf56'


async def get_datapollution(lat, lon, forecast = True ):
    '''Returns current air pollution data or forecast for 5 days for point with coord (lat, lon)''' 

    if forecast:
        url = 'http://api.openweathermap.org/data/2.5/air_pollution/forecast'
    else:
        url = 'http://api.openweathermap.org/data/2.5/air_pollution'

    params = {'lat': lat, 'lon': lon, 'APPID': config.API_key}

    async with app_session.get(url=url, params=params) as response:
        data_pol = await response.json()
        try:
            return data_pol
        except KeyError:
            return 'Нет данных'


async def Reverse_geocoding(lon, lat, limit = '1'):
    #http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit={limit}&appid={API key}
    url = 'http://api.openweathermap.org/geo/1.0/zip'
    params = {'lon': lon, 'lat': lat, 'limit': limit, 'APPID': config.API_key}
    async with app_session.get(url=url, params=params) as response:
        json_data = await response.json()
        try:
        
            return json_data[0]['name'], json_data[0]['lon'], json_data[0]['lat'] 
        except KeyError:
            return '', '', ''


async def geocoding(cityname = '', zipcode = '', statecode = '', countrycode = '', limit = '1'):
    '''Determines the coordinates of the city by postal code or cityname'''

    #http://api.openweathermap.org/geo/1.0/direct?q={city name},{state code},{country code}&limit={limit}&appid={API key}
    #http://api.openweathermap.org/geo/1.0/zip?zip={zip code},{country code}&appid={API key}

    zip = False
    if zipcode != '' and countrycode != '':
        url = 'http://api.openweathermap.org/geo/1.0/zip'
        zip_param = zipcode + ',' + countrycode
        params = {'zip': zip_param, 'APPID': config.API_key}
        zip = True

    elif zipcode != '' and countrycode == '':
        return 'Country code is messing in the request!'

    elif zipcode == '' and countrycode != '':
        return '', '', ''
    elif cityname != '':
        url = 'http://api.openweathermap.org/geo/1.0/direct'
        q_param = cityname + ',' + statecode + ',' + countrycode
        params = {'q': q_param, 'limit': limit, 'APPID': config.API_key}

    elif cityname != '' and zipcode == '':
        return '', '', ''
    else:
        return '', '', ''
    async with app_session.get(url=url, params=params) as response:
        json_data = await response.json()
        try:
            if zip:
                return json_data['name'], json_data['lon'], json_data['lat']
            else:
                return json_data[0]['name'], json_data[0]['lon'], json_data[0]['lat'] 
        except KeyError:
            return '', '', ''


async def get_translation(text, source, target):
    '''Online translater. Not used'''

    url = 'https://libretranslate.de/translate'
    data = {'q': text, 'source': source, 'target': target, 'format': 'text'}
    async with app_session.post(url, json=data) as response:
        translate_json = await response.json()
        try:
            return translate_json['translatedText']
        except KeyError:
            return text


async def handle(request):

    #localhost:8080/pollution?city={city name}&country={country code}&forecust={True/False}
    #localhost:8080/pollution?zip={zip/post code}&country={country code}
    #localhost:8080/pollution?lon={longitude}&lat={latitude}

    cityname = ''
    zipcode = ''
    statecode = ''
    countrycode = ''
    forecast = True

    if 'forecast' in request.rel_url.query:  
        if request.rel_url.query['forecast'] == 'False':
            forecast = False
        else:
            forecast = True

    if 'zip' in request.rel_url.query:
        if 'country' in request.rel_url.query:
            countrycode = request.rel_url.query['country']
        else:
            countrycode = ''
        zipcode = request.rel_url.query['zip']
    elif 'city' in request.rel_url.query:
        if 'country' in request.rel_url.query:
            countrycode = request.rel_url.query['country']
        else:
            countrycode = ''
        cityname = request.rel_url.query['city']
    elif 'lon' in request.rel_url.query and 'lat' in request.rel_url.query:
        lon = request.rel_url.query['lon']
        lat = request.rel_url.query['lat']
        data_pollution = await get_datapollution(lon, lat, forecast)
        result = {'air_pollution': data_pollution}
        return web.Response(text=json.dumps(result, ensure_ascii=False))

    else:  
        return web.Response(text='Bad request!!!')    

    cityname, lon, lat = await geocoding(cityname , zipcode, statecode, countrycode)
    data_pollution = await get_datapollution(lon, lat, forecast)
    data_pollution['name'] = cityname
    result = {'air_pollution': data_pollution}
    return web.Response(text=json.dumps(result, ensure_ascii=False))


async def main():

    global app_session

    app_session = ClientSession()

    async with app_session:
        app = web.Application()

        app.add_routes([web.get(config.URL, handle)])
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, config.HOSTNAME, config.PORT)
        await site.start()

        while True:
            await asyncio.sleep(3600)


if __name__ == '__main__':
    asyncio.run(main())
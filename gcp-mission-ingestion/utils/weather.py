import os

import logging

from typing import Dict, Any



import httpx


# Configurazione base del logger per il modulo.

# In produzione è consigliato configurare il logging a livello globale nell'app.

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)





API_URL = "https://api.openweathermap.org/data/2.5/weather"





async def get_weather(latitude: float, longitude: float) -> Dict[str, Any]:

    """
Recupera le condizioni meteo da OpenWeatherMap per le coordinate fornite.

Parameters

----------

latitude: float

Latitudine del punto per cui recuperare i dati meteo.

longitude: float

Longitudine del punto di interesse.

Returns

-------

Dict[str, Any]

Un dizionario contenente:

- "temperature": temperatura in gradi Celsius

- "wind_speed": velocità del vento in m / s

- "condition": breve descrizione testuale delle condizioni meteo

Notes

-----

- Richiede la variabile ambiente OPENWEATHER_API_KEY.
- In caso di errore di reteo risposta non valida, viene effettuato logging dell 'errore e viene ritornato un dizionario con valori di fallback.

"""



api_key = os.getenv("OPENWEATHER_API_KEY")

if not api_key:

    logger.error("OPENWEATHER_API_KEY environment variable not set.")

    # Ritorno valori fallback: l'endpoint /mission non deve collassare.

    return {

        "temperature": None,

        "wind_speed": None,

        "condition": "unknown",

    }



# Parametri della richiesta GET come specifica OpenWeatherMap.

params = {

    "lat": latitude,

    "lon": longitude,

    "appid": api_key,

    "units": "metric",  # usiamo Celsius per coerenza con il progetto

}



# Timeout di 5 secondi come richiesto.

timeout = httpx.Timeout(5.0, connect=5.0)



# Client asincrono per la richiesta HTTP.

async with httpx.AsyncClient(timeout=timeout) as client:

    try:

        response = await client.get(API_URL, params=params)



        # Se lo status HTTP non è 200, generiamo eccezione.

        response.raise_for_status()



        data = response.json()



        # Estrazione dei campi principali da OpenWeatherMap.

        temperature = data.get("main", {}).get("temp")

        wind_speed = data.get("wind", {}).get("speed")

        condition = (

            data.get("weather", [{}])[0].get("description", "unknown")

        )



        return {

            "temperature": temperature,

            "wind_speed": wind_speed,

            "condition": condition,

        }



    except httpx.HTTPError as exc:

        # Errore HTTP → log + fallback.

        logger.error(f"HTTP error during weather fetch: {exc}")

        return {

            "temperature": None,

            "wind_speed": None,

            "condition": "unknown",

        }



    except Exception as exc:

        # Errori generici imprevisti → log + fallback.

        logger.error(f"Unexpected error in get_weather(): {exc}")

        return {

            "temperature": None,

            "wind_speed": None,

            "condition": "unknown",

        }


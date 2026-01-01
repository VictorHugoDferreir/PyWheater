from fastapi import APIRouter, HTTPException
import httpx

router = APIRouter()

CODIGOS_CLIMATICOS = {
    0: "Céu Limpo",
    1: "Principalmente Limpo",
    2: "Parcialmente Nublado",
    3: "Nublado",
    45: "Nevoeiro",
    61: "Chuva Leve",
    63: "Chuva Moderada",
    80: "Pancadas de Chuva",
    95: "Trovoada"
}

@router.get("/climaAtual/{latitude}/{longitude}")
async def clima_atual(latitude: float, longitude: float):

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,apparent_temperature,is_day,rain,precipitation_probability,weather_code",
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            current = data.get("current", {})
            daily = data.get("daily", {})
            
            #tradução dos códigos climáticos no dicionário
            codigo = current.get("weather_code")
            descricao = CODIGOS_CLIMATICOS.get(int(codigo) if codigo is not None else -1, "Desconhecido")
            

            return {
                "temperatura": current.get("temperature_2m"),
                "sensacao_termica": current.get("apparent_temperature"),
                "precipitacao": current.get("rain"),
                "probabilidade_precipitacao": current.get("precipitation_probability"),
                "e_dia": bool(current.get("is_day")),
                "temperatura_minima": daily.get("temperature_2m_min", [None])[0],
                "temperatura_maxima": daily.get("temperature_2m_max", [None])[0],
                "descricao_climatica": descricao
            }

        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Erro na API externa: {e.response.text}")
        except Exception as e:
        
            raise HTTPException(status_code=500, detail=f"Falha no processamento: {type(e).__name__} - {str(e)}")
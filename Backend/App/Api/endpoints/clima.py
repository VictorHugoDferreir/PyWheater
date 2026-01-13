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

@router.get("/climaAtual/{cidade}")
async def clima_atual_por_cidade(cidade: str):
    async with httpx.AsyncClient() as client:
        try:
            geocode_url = "https://nominatim.openstreetmap.org/search"
            geocode_params = {"q": cidade, "format": "json", "limit": 1}
            geocode_response = await client.get(geocode_url, params=geocode_params, timeout=10.0)
            geocode_response.raise_for_status()
            geocode_data = geocode_response.json()
            
            if not geocode_data:
                raise HTTPException(status_code=404, detail="Cidade não encontrada")
            
            latitude = geocode_data[0]["lat"]
            longitude = geocode_data[0]["lon"]
            
            return await obter_dados_climaticos(latitude, longitude)
        
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Erro na API externa: {e.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Falha no processamento: {type(e).__name__} - {str(e)}")

    async def obter_dados_climaticos(latitude: float, longitude: float):
        async with httpx.AsyncClient() as client:
            clima_url = "https://api.open-meteo.com/v1/forecast"
            clima_params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,apparent_temperature,is_day,rain,precipitation_probability,weather_code",
                "daily": "temperature_2m_max,temperature_2m_min",
                "timezone": "auto"
            }
            clima_response = await client.get(clima_url, params=clima_params, timeout=10.0)
            clima_response.raise_for_status()
            clima_data = clima_response.json()

            if "current" not in clima_data or "daily" not in clima_data:
                raise HTTPException(status_code=500, detail="Dados climáticos incompletos recebidos")

            current = clima_data["current"]
            daily = clima_data["daily"]

            codigo_climatico = current.get("weather_code", -1)
            descricao_climatico = CODIGOS_CLIMATICOS.get(codigo_climatico, "Desconhecido")

            resultado = {
                "temperatura_atual": current.get("temperature_2m"),
                "sensacao_termica": current.get("apparent_temperature"),
                "eh_dia": bool(current.get("is_day")),
                "chuva_mm": current.get("rain"),
                "probabilidade_precipitacao_percentual": current.get("precipitation_probability"),
                "descricao_climatico": descricao_climatico,
                "temperatura_maxima_diaria": daily.get("temperature_2m_max", [None])[0],
                "temperatura_minima_diaria": daily.get("temperature_2m_min", [None])[0]
            }

            return resultado    
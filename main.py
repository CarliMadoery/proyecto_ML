# Librerias a utilizar
from fastapi import FastAPI
import uvicorn
import pandas as pd

# Instanciamos FastAPI
app = FastAPI()
# Cargamos los archivos a consumir
df_userdata_1 = pd.read_parquet('Data\\df_userdata_1.parquet')
df_userdata_2 = pd.read_parquet('Data\\df_userdata_2.parquet')
df_countreviews = pd.read_parquet('Data\\df_countreviews.parquet')
df_genres = pd.read_parquet('Data\\df_genres.parquet')
df_top5 = pd.read_parquet('Data\\df_top5.parquet')
df_developer = pd.read_parquet('Data\\df_developer.parquet')
df_sentiment = pd.read_parquet('Data\\df_sentiment.parquet')

@app.get("/")  # decorator to define a route http://127.0.0.1:8000
def index():
    return {"message": "Hello World"}


# Function 1
@app.get("/userdata/{user_id}")
async def userdata(User_id: str) -> dict:
    '''Dado un id de usuario igresado, la función retorna:
    - La cantidad de juegos que adquirió el usuario
    - El dinero gastado por el usuario
    - El % de juegos que recomienda de todos los que adquirió
    '''
    if type(User_id) is not str:
        raise TypeError("El parametro debe ser string")
    '''if User_id not in df_items_games.user_id:
                 print('Usuario no encontrado') # Para debuggear'''
                 

    # Filtra el DataFrame para obtener solo las filas correspondientes al User_id proporcionado
    data1 = df_userdata_1[df_userdata_1['user_id'] == User_id]
    data2 = df_userdata_2[df_userdata_2['user_id'] == User_id]
    
    # Obtiene la Cantidad de items comprados por el usuario extrayendo el valor del campo 'items_count'
    num_items = data1['items_count'].values[0].item()
    
    # Calcula la cantidad de dinero gastado por el usuario (suma de la columna 'price')
    Dinero_gastado = data1['price'].sum()
    
    # Calcula el porcentaje de recomendación del usuario
    recommend_percentage = data2.recommend.sum()/len(data2)*100
    

    
    # Crea un diccionario con los resultados
    user_info = {
        'User_id': User_id,
        'Cantidad_de_items': num_items,
        'Dinero_gastado': Dinero_gastado,
        'Porcentaje_recomendacion': recommend_percentage
    }
    
    return user_info

# Function 2
@app.get("/countreviews/{start_date}/{end_date}")
async def countreviews(start_date: str, end_date: str):
    """
    La presente función calcula la cantidad de usuarios que realizaron reviews entre las fechas ingresadas y, 
    el porcentaje de recomendación de los mismos en base a sus reviews.

    Args:
        start_time (str): fecha de inicio en formato 'YYYY-MM-DD'
        end_time (str): fecha de fin en formato 'YYYY-MM-DD'

    """
    # Convierte las fechas de inicio y fin en objetos datetime
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filtra las reseñas que están dentro del rango de fechas dado
    filtered_reviews = df_countreviews[(df_countreviews['formatted_date'] >= start_date) & (df_countreviews['formatted_date'] <= end_date)]

    # Obtiene la cantidad de usuarios únicos que realizaron reseñas en ese rango
    unique_users = filtered_reviews['user_id'].nunique()

    # Calcula el porcentaje de recomendación
    recommendation_percentage = round((filtered_reviews['recommend'].sum() / filtered_reviews.shape[0]) * 100, 2) 

    result = {
        'Cantidad de usuarios que realizaron reviews': unique_users,
        'Porcentaje de recomendaciones': recommendation_percentage
    }

    return result

#Function 3
@app.get('/genre/{genero}')
async def genre( genero : str ): 
    '''
    La función recibe el nombre de un género y retorna el puesto que ocupa el mismo en el ranking de los 
    género más jugados por los usuarios

    Args:
        genero (str): Género a buscar dentro de la base de datos.

    '''
    # validacion de argumento ingresado
    if type(genero) is not str:
        raise TypeError("El argumento debe ser de tipo string")
    # Convierte el género especificado a un formato consistente (primera letra en mayúscula, resto en minúsculas).
    genero = genero.lower().capitalize()
    # Filtra el DataFrame en función del género especificado.
    df_filtrado = df_genres[df_genres['genres'] == genero]
    
    # Verifica si el género especificado se encuentra en el DataFrame.
    if df_filtrado.empty:
        return print("El género especificado no se encuentra en la base de datos.") # El género no se encuentra en el DataFrame.
    
    # Obtiene el índice de la fila correspondiente al género especificado.
    puesto = df_filtrado.index[0].item() + 1  # Sumar 1 para obtener un ranking basado en 1 en lugar de 0.
    
    result = {
        'Género': genero,
        'Ranking N°': puesto
    }

    return result

#Function 4
@app.get('/userforgenre/{genero}')
async def userforgenre(genero:str):
    '''
    La presente función recibe como argumento el nombre de un género (str) y devuelve el 
    Top 5 de usuarios con más horas de juego en dado género, con su URL y user_id.
    '''
    #validacion de argumento
    if not isinstance(genero, str):
        raise TypeError("El argumento 'género' debe ser una cadena (str)")
    
    # Filtramos el DataFrame para incluir solo las filas relacionadas con el género especificado.
    df_filtrado = df_top5[df_top5['genres'].str.contains(genero, case=False, na=False)]

    if df_filtrado.empty:
        return print("No se encontraron registros para el género", genero)
    
    # Se agrupan los datos por usuario y url sumando las horas jugadas.
    df_agrupado = df_filtrado.groupby(['user_id','user_url'])['playtime_forever'].sum().reset_index()

    # Ordena los usuarios en función de las horas jugadas en orden descendente.
    df_ordenado = df_agrupado.sort_values(by='playtime_forever', ascending=False).reset_index(drop=True)

    # Selecciona los primeros 5 usuarios del ranking.
    top_5_usuarios = df_ordenado.head(5).reset_index(drop=True)

    # convertimos el resultado en un diccionario
    resultado = top_5_usuarios.to_dict(orient='list')

    return resultado

# Function 5
@app.get("/developer/{developer}")
async def developer(developer:str):
    '''
    'developer' calcula la cantidad de items y porcentaje de contenido Free por año según empresa desarrolladora.
    
    Args:
        developer (str): nombre de la empresa desarrolladora
    Return:
        diccionario con la cantidad total de items y el % de items gratis en cada año para esa empresa
    '''
    # Validacion de argumento
    if not isinstance(developer, str):
        raise TypeError("El argumento debe ser una cadena (str)")
    # Convierte el texto ingresado a un formato consistente (primera letra en mayúscula, resto en minúsculas).
    developer = developer.lower().capitalize()
    # Filtra el DataFrame para obtener solo los juegos del desarrollador especificado
    df_filter = df_developer[df_developer['developer'] == developer]

    # Validacion de dato
    if df_filter.empty:
        return {"mensaje": f"No se encontraron registros para la empresa {developer}"}

    # Agrupa por año y calcula la cantidad de juegos (item_id) y el porcentaje de contenido gratuito
    grouped = df_filter.groupby('release_year').agg(
        games_total=('item_id', 'count'),
        games_Free=('price', lambda x: (x == 'free').mean() * 100)
    ).reset_index()

    resultado = grouped.to_dict(orient='list')
    return resultado

# Function 6
@app.get("/sentiments_analysis/{year}")
async def sentiments_analysis(year:int) -> dict:
    '''
    Esta función recibe un año como argumento y cuenta la cantidad de reseñas de usuarios negativas (0),
    neutrales (1) y positivas (2) que hubo en ese año.

    Args:
        year (int): El año en formato numérico YYYY.

    Returns:
        dict: Un diccionario con la cantidad de cada tipo de sentimiento.
    '''
    # Validación de argumento 
    list_anios = df_sentiment.formatted_date.dt.year.to_list()
    if year not in list_anios:
        return {'message': 'No hay registros para el año ingresado'}
    # Filtrar el DataFrame por el año especificado
    df_filtered = df_sentiment[df_sentiment['formatted_date'].dt.year == year]

    # Contar la cantidad de cada tipo de sentimiento
    sentiment_counts = df_filtered['sentiment'].value_counts().to_dict()

    # Crear un diccionario con las cantidades
    result_dict = {
        'Negative (0)': sentiment_counts.get(0, 0),
        'Neutral (1)': sentiment_counts.get(1, 0),
        'Positive (2)': sentiment_counts.get(2, 0)
    }

    return result_dict

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

# Cargar los datos de valores de mercado desde el archivo JSON
ruta_archivo_valores = "datos_completos.json"
datos_jugadores = pd.read_json(ruta_archivo_valores)

# Reemplazar valores vacíos con NaN
datos_jugadores = datos_jugadores.replace('', np.nan)

# Eliminar filas con valores nulos en cualquier columna
datos_jugadores = datos_jugadores.dropna()

# Convertir la columna 'fecha' en formato datetime
datos_jugadores['fecha'] = pd.to_datetime(datos_jugadores['fecha'])

# Extraer las columnas 'anio', 'mes' y 'dia' de la columna 'fecha'
datos_jugadores['anio'] = datos_jugadores['fecha'].dt.year
datos_jugadores['mes'] = datos_jugadores['fecha'].dt.month
datos_jugadores['dia'] = datos_jugadores['fecha'].dt.day

# Dividir la columna 'temporada' en dos columnas 'año_inicio' y 'año_fin'
datos_jugadores[['año_inicio', 'año_fin']] = datos_jugadores['temporada'].str.split('/', expand=True).astype(int)

# Seleccionar las columnas relevantes para el modelo
X = pd.get_dummies(datos_jugadores[['anio', 'mes', 'dia', 'jugador_id', 'pais', 'edad_jugador', 'posicion_jugador', 'club_id', 'año_inicio', 'año_fin', 'goles', 'asistencias', 'minutos_jugados', 'tarjetas_amarillas', 'tarjetas_rojas']], columns=['pais', 'posicion_jugador'])

# Eliminar filas con valores nulos en el conjunto de características
X = X.dropna()

# Seleccionar la columna 'valor_de_mercado' como la variable objetivo
y = datos_jugadores['valor_de_mercado']

# Eliminar filas en y que hayan sido eliminadas en X
y = y[y.index.isin(X.index)]

# Dividir los datos en conjuntos de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)

# Creamos el modelo y lo entrenamos
modelo = RandomForestRegressor(n_estimators=3000, random_state=50)
modelo.fit(X_train, y_train)

# Realizar predicciones en el conjunto de prueba
predicciones = modelo.predict(X_test)

# Calcular el error cuadrático medio (MSE)
mse = mean_squared_error(y_test, predicciones)

# Calcular el coeficiente de determinación (R²)
r2 = r2_score(y_test, predicciones)

print("Error cuadrático medio (MSE):", mse)
print("Coeficiente de determinación (R²):", r2)

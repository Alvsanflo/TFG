import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Cargar los datos desde el archivo JSON
ruta_archivo = "valoresdemercado_nombres.json"
datos_jugadores = pd.read_json(ruta_archivo)

# Reemplazar "Desconocido" con NaN
datos_jugadores = datos_jugadores.replace('Desconocido', np.nan)

# Eliminar filas con valores nulos o vacíos en cualquier columna
datos_jugadores = datos_jugadores.dropna()

# Convertir la columna 'fields' en múltiples columnas
datos_jugadores = pd.concat([datos_jugadores.drop(['fields'], axis=1), datos_jugadores['fields'].apply(pd.Series)], axis=1)

# Convertir la columna 'fecha' en múltiples columnas de datos numéricos
datos_jugadores['fecha'] = pd.to_datetime(datos_jugadores['fecha'])
datos_jugadores['anio'] = datos_jugadores['fecha'].dt.year
datos_jugadores['mes'] = datos_jugadores['fecha'].dt.month
datos_jugadores['dia'] = datos_jugadores['fecha'].dt.day

#Seleccionamos las columnas que vamos a utilizar para entrenar el modelo y la variable objetivo y convertir las variables categóricas en variables dummy usando one-hot encoding
X = pd.get_dummies(datos_jugadores[['anio', 'mes', 'dia', 'jugador_id', 'pais', 'edad_jugador', 'posicion_jugador', 'club_id']], columns=['pais', 'posicion_jugador'])
y = datos_jugadores['valor_de_mercado']

# Dividir los datos en conjuntos de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)

# Normalizar los datos
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Construir el modelo de red neuronal
model = tf.keras.Sequential([
    tf.keras.layers.Dense(128, activation='relu', input_shape=(X_train_scaled.shape[1],)),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dense(1)
])

# Compilar el modelo
model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mean_squared_error'])

# Entrenar el modelo
history = model.fit(X_train_scaled, y_train, epochs=50, batch_size=32, validation_data=(X_test_scaled, y_test))

# Evaluar el modelo en el conjunto de prueba
mse = model.evaluate(X_test_scaled, y_test)[1]
print("Error cuadrático medio (MSE):", mse)

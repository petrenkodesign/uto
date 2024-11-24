import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
import numpy as np
import pandas as pd
# Генерація симуляційних даних
def generate_data(samples=10000):
    data = []
    for _ in range(samples):
        wind_speed = np.random.uniform(0, 20)  # м/с
        wind_dir = np.random.uniform(0, 360)  # градуси
        current_lat = np.random.uniform(-90, 90)
        current_lon = np.random.uniform(-180, 180)
        target_lat = current_lat + np.random.uniform(-0.1, 0.1)  # Цільова точка поруч
        target_lon = current_lon + np.random.uniform(-0.1, 0.1)

        # Ручне правило для симуляції "правильної" команди
        motor_left = 1 if target_lon > current_lon else 0
        motor_right = 1 if target_lat > current_lat else 0

        data.append([wind_speed, wind_dir, current_lat, current_lon, target_lat, target_lon, motor_left, motor_right])
    return np.array(data)

# Завантаження або створення набору даних
data = generate_data(5000)
df = pd.DataFrame(data, columns=["wind_speed", "wind_dir", "current_lat", "current_lon", 
                                 "target_lat", "target_lon", "motor_left", "motor_right"])
# Вхідні дані: фактори впливу
X = df[["wind_speed", "wind_dir", "current_lat", "current_lon", "target_lat", "target_lon"]].values
# Вихідні дані: команди двигунів
y = df[["motor_left", "motor_right"]].values

# Розділення на тренувальні та тестові дані
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
# Нейронна мережа
model = Sequential([
    Dense(64, input_dim=6, activation='relu'),
    Dropout(0.2),
    Dense(128, activation='relu'),
    Dropout(0.2),
    Dense(2, activation='sigmoid')  # Два виходи: лівий і правий двигуни
])

# Компіляція моделі
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
# Навчання
history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test))
# Оцінка точності
loss, accuracy = model.evaluate(X_test, y_test)
print(f"Test Accuracy: {accuracy * 100:.2f}%")
# Збереження моделі
model.save("balloon_control_model.h5")

## Завантаження моделі
#model = tf.keras.models.load_model("balloon_control_model.h5")

## Приклад передбачення
#test_input = np.array([[10, 45, 50.1, 30.2, 50.15, 30.25]])  # Поточні дані
#prediction = model.predict(test_input)
#motor_left, motor_right = (prediction > 0.5).astype(int)[0]
#print(f"Motor Left: {motor_left}, Motor Right: {motor_right}")


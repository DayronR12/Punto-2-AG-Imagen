import numpy as np
from PIL import Image
import random
import matplotlib.pyplot as plt
from tkinter import Tk, Label, Button, filedialog, Toplevel
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Variables para control de la pausa y estado del algoritmo
pausado = False
evolucionando = False  # Para verificar si el algoritmo ya está en ejecución
imagen_referencia = None  # Guardar la imagen cargada globalmente
poblacion_actual = None  # Guardar la población actual
generacion_actual = 0  # Guardar el número de generación actual

# Función para generar imagen aleatoria
def generar_imagen_aleatoria(ancho, alto):
    return np.random.randint(0, 256, (alto, ancho, 3), dtype=np.uint8)

# Función para calcular fitness
def calcular_fitness(individuo, imagen_referencia):
    return np.sum(np.abs(individuo - imagen_referencia))

# Función para seleccionar los mejores padres
def seleccionar_padres(poblacion, fitness_poblacion, num_padres):
    seleccionados = np.argsort(fitness_poblacion)[:num_padres]
    return [poblacion[i] for i in seleccionados]

# Función de cruce entre dos padres
def cruce(padre1, padre2):
    hijo = np.copy(padre1)
    mask = np.random.rand(*padre1.shape) > 0.5
    hijo[mask] = padre2[mask]
    return hijo

# Función de mutación
def mutacion(hijo, tasa_mutacion):
    if np.random.rand() < tasa_mutacion:
        x, y = np.random.randint(0, hijo.shape[1]), np.random.randint(0, hijo.shape[0])
        hijo[y, x] = np.random.randint(0, 256, 3)
    return hijo

# Función de evolución
def evolucion(poblacion, imagen_referencia, generaciones, tasa_mutacion, num_padres, ax, label_generaciones):
    global pausado, poblacion_actual, generacion_actual

    for generacion in range(generaciones):
        if pausado:  # Si está pausado, detener la evolución
            poblacion_actual = poblacion  # Guardar el estado de la población actual
            break

        fitness_poblacion = [calcular_fitness(individuo, imagen_referencia) for individuo in poblacion]
        padres = seleccionar_padres(poblacion, fitness_poblacion, num_padres)

        nuevos_hijos = []
        for _ in range(len(poblacion) - num_padres):
            padre1, padre2 = random.sample(padres, 2)
            hijo = cruce(padre1, padre2)
            hijo = mutacion(hijo, tasa_mutacion)
            nuevos_hijos.append(hijo)

        poblacion = padres + nuevos_hijos
        mejor_fitness = min(fitness_poblacion)
        
        # Actualizar la generación actual
        generacion_actual += 1
        label_generaciones.config(text=f"Generación: {generacion_actual}")

        if generacion % 100 == 0:
            mejor_individuo = padres[0]
            ax.clear()
            ax.imshow(mejor_individuo)
            canvas.draw()
            root.update()

    return padres[0]

# Función para cargar imagen y mostrarla en otra ventana
def cargar_imagen():
    global imagen_referencia, evolucionando, poblacion_actual, generacion_actual

    archivo = filedialog.askopenfilename(filetypes=[("Archivos de imagen", "*.jpg *.png *.jpeg")])
    if archivo:
        imagen_referencia = np.array(Image.open(archivo).resize((ancho, alto)))

        # Abrir una nueva ventana para mostrar la imagen de referencia
        ventana_imagen = Toplevel(root)
        ventana_imagen.title("Imagen de Referencia")
        fig_imagen, ax_imagen = plt.subplots()
        canvas_imagen = FigureCanvasTkAgg(fig_imagen, master=ventana_imagen)
        ax_imagen.imshow(imagen_referencia)
        canvas_imagen.get_tk_widget().pack()

        # Preparar para la evolución
        poblacion_actual = [generar_imagen_aleatoria(ancho, alto) for _ in range(tamaño_poblacion)]  # Nueva población
        evolucionando = True
        generacion_actual = 0  # Reiniciar el conteo de generaciones cuando se carga una nueva imagen
        ejecutar_algoritmo(imagen_referencia)

# Función para ejecutar el algoritmo
def ejecutar_algoritmo(imagen_referencia):
    global poblacion_actual
    mejor_individuo = evolucion(poblacion_actual, imagen_referencia, generaciones, tasa_mutacion, num_padres, ax, label_generaciones)
    ax.clear()
    ax.imshow(mejor_individuo)
    canvas.draw()

# Función para pausar la generación
def pausar_generacion():
    global pausado
    pausado = True

# Función para reanudar la generación
def reanudar_generacion():
    global pausado, evolucionando, imagen_referencia
    if evolucionando and pausado:  # Solo reanudar si se estaba evolucionando y se pausó
        pausado = False
        ejecutar_algoritmo(imagen_referencia)  # Continuar desde donde se pausó

# Parámetros
ancho, alto = 32, 32
tamaño_poblacion = 350
generaciones = 20000
tasa_mutacion = 0.001
num_padres = 300

# Crear interfaz
root = Tk()
root.title("Algoritmo Genético de Imágenes")

# Pestaña de evolución
label_generaciones = Label(root, text="Generación: 0")
label_generaciones.pack()

boton_cargar = Button(root, text="Cargar Imagen", command=cargar_imagen)
boton_cargar.pack()

boton_pausar = Button(root, text="Pausar", command=pausar_generacion)
boton_pausar.pack()

boton_reanudar = Button(root, text="Reanudar", command=reanudar_generacion)
boton_reanudar.pack()

fig, ax = plt.subplots()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

# Iniciar interfaz
root.mainloop()

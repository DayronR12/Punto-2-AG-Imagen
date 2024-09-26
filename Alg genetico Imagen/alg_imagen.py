from PIL import Image, ImageTk
import numpy as np
import tkinter as tk
import random

# Cargar la imagen de referencia
reference_image = Image.open("images.jpeg")
reference_image = reference_image.resize((40, 40))  # Redimensionar a 40x40
reference_data = np.array(reference_image)

# Nuevo tamaño para mostrar las imágenes
display_size = (200, 200)  # Tamaño de visualización

def generate_initial_population(size, width, height):
    return [np.random.randint(0, 256, (height, width, 3), dtype=np.uint8) for _ in range(size)]

def calculate_fitness(generated_image, reference_data):
    return np.sum(np.abs(generated_image - reference_data))

def select_parents(population, fitness_scores, num_parents):
    num_parents = min(num_parents, len(population))  # Asegurarse de no seleccionar más padres de los que hay
    parents_indices = np.argsort(fitness_scores)[:num_parents]
    return [population[i] for i in parents_indices]

def crossover(parent1, parent2):
    mask = np.random.randint(0, 2, parent1.shape, dtype=np.uint8)
    return parent1 * mask + parent2 * (1 - mask)

def mutate(image, mutation_rate=0.05):
    if np.random.rand() < mutation_rate:
        mutation = np.random.randint(-10, 11, image.shape, dtype=np.int16)
        return np.clip(image + mutation, 0, 255).astype(np.uint8)
    return image

def update_image(canvas, img):
    img = Image.fromarray(img)
    img = img.resize(display_size, Image.NEAREST)  # Redimensionar a 200x200
    img_tk = ImageTk.PhotoImage(img)
    canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
    canvas.img_tk = img_tk  # Mantener referencia para evitar recolección de basura

def create_window(title):
    window = tk.Toplevel()  # Crear una nueva ventana
    window.title(title)
    canvas = tk.Canvas(window, width=display_size[0], height=display_size[1])  # Ajustar tamaño del canvas
    canvas.pack()
    return canvas

def genetic_algorithm(reference_data, generations=1000, population_size=350):  # Tamaño de población ajustado a 300
    height, width, _ = reference_data.shape
    population = generate_initial_population(population_size, width, height)

    # Crear ventana para la imagen de referencia
    reference_window = create_window("Imagen de Referencia")
    reference_image_tk = ImageTk.PhotoImage(reference_image)
    update_image(reference_window, reference_data)  # Mostrar la imagen de referencia

    # Crear ventana para la imagen generada
    generated_window = create_window("Imagen Generada")

    for generation in range(generations):
        fitness_scores = [calculate_fitness(image, reference_data) for image in population]
        print(f"Generación {generation}: Mejor fitness = {min(fitness_scores)}")
        
        parents = select_parents(population, fitness_scores, population_size // 2)

        new_population = []
        
        # Mantener los mejores individuos (elitismo)
        best_indices = np.argsort(fitness_scores)[:2]  # Mantener los 2 mejores
        new_population.extend([population[i] for i in best_indices])

        # Generar nueva población
        while len(new_population) < population_size:
            parent1 = random.choice(parents)
            parent2 = random.choice(parents)
            child = crossover(parent1, parent2)
            child = mutate(child)
            new_population.append(child)

        population = new_population

        best_image = population[np.argmin(fitness_scores)]
        update_image(generated_window, best_image)

        reference_window.update_idletasks()
        reference_window.update()
        generated_window.update_idletasks()
        generated_window.update()

    # Mantener las ventanas abiertas después de la evolución
    reference_window.mainloop()
    generated_window.mainloop()

# Ejecutar el algoritmo
if __name__ == "__main__":
    root = tk.Tk()  # Crear una instancia de Tk solo para evitar que aparezca la ventana "Tk"
    root.withdraw()  # Ocultar la ventana principal
    genetic_algorithm(reference_data)
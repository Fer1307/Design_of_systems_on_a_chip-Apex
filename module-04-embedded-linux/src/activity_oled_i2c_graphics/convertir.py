# Path se usa para encontrar la imagen dentro de la misma carpeta del script.
from pathlib import Path

# Pillow permite abrir y convertir imágenes.
from PIL import Image

# matplotlib se usa solo para visualizar la matriz como imagen.
# No es necesario para controlar la OLED, pero sirve para comprobar el resultado.
import matplotlib.pyplot as plt


# Imagen que se va a convertir.
# En este caso usamos el logo del equipo.
IMAGE_NAME = "cabra.png"


def image_to_binary_matrix(image_name):
    """
    Convierte una imagen en una matriz de 0 y 1.

    La idea es representar la imagen como lo haría una OLED:
    - 1 = pixel encendido
    - 0 = pixel apagado
    """

    # Construimos la ruta completa hacia la imagen.
    image_path = Path(__file__).parent / image_name

    # Validamos que exista para evitar errores difíciles de interpretar.
    if not image_path.exists():
        raise FileNotFoundError(f"No se encontró la imagen: {image_name}")

    # Abrimos la imagen con Pillow.
    img = Image.open(image_path)

    # Convertimos la imagen a modo "1", es decir, blanco y negro puro.
    img = img.convert("1")

    width, height = img.size

    # Aquí se guardará la matriz final.
    matrix = []

    # Recorremos la imagen pixel por pixel.
    for y in range(height):
        row = []

        for x in range(width):
            pixel = img.getpixel((x, y))

            # En Pillow, para modo "1":
            # - 0 normalmente representa negro.
            # - 255 representa blanco.
            #
            # Para la lógica de la OLED usamos:
            # - 1 cuando el pixel debe estar encendido.
            # - 0 cuando debe estar apagado.
            if pixel == 0:
                row.append(1)
            else:
                row.append(0)

        matrix.append(row)

    return matrix


def print_matrix(matrix):
    """
    Imprime la matriz en la terminal.

    Esto sirve para comprobar que la imagen realmente se convirtió
    a una estructura de datos binaria.
    """
    for row in matrix:
        print(row)


def show_matrix(matrix):
    """
    Muestra la matriz como una imagen usando matplotlib.

    Esto fue útil en la etapa de pruebas, antes de mandar la imagen a la OLED real.
    """
    plt.imshow(matrix, cmap="gray")
    plt.title("Visualización de matriz binaria")
    plt.axis("off")
    plt.show()


if __name__ == "__main__":
    # Convertimos la imagen definida en IMAGE_NAME.
    binary_matrix = image_to_binary_matrix(IMAGE_NAME)

    # Imprimimos la matriz para revisar los datos.
    print_matrix(binary_matrix)

    # Mostramos la matriz como imagen para validar visualmente el resultado.
    show_matrix(binary_matrix)
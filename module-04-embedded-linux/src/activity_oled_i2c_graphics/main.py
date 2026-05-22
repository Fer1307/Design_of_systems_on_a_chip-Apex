# Importamos sys porque PyQt5 necesita acceder a los argumentos del sistema
# para iniciar correctamente la aplicación gráfica.
import sys

# Path permite manejar rutas de archivos de forma más segura.
# Lo uso para abrir imágenes sin depender de la carpeta exacta desde donde se ejecute el programa.
from pathlib import Path

# sqrt se usa para calcular una distancia entre colores.
# Esto ayuda a detectar qué pixeles pertenecen al dibujo y cuáles son fondo.
from math import sqrt

# Pillow se usa para crear, editar y convertir imágenes.
# En esta práctica es importante porque la OLED trabaja como una pantalla monocromática de 128x64.
from PIL import Image, ImageDraw, ImageFont

# PyQt5 se usa para crear la interfaz gráfica:
# - QtWidgets: botones, ventana, etiquetas, cajas de texto.
# - QtGui: conversión de imágenes a formato que PyQt puede mostrar.
# - QtCore: geometría, posiciones y propiedades internas de Qt.
from PyQt5 import QtWidgets, QtGui, QtCore

# Estas librerías permiten usar los pines I2C de la Raspberry Pi.
# board proporciona nombres estándar para pines como SDA y SCL.
import board

# busio permite crear el bus I2C usando los pines físicos de la Raspberry.
import busio

# Librería específica para controlar pantallas OLED SSD1306.
# Esta es la que realmente manda la imagen a la pantalla física.
import adafruit_ssd1306

# Importamos la clase generada en interfaz.py.
# Ese archivo contiene el diseño visual de la ventana.
from interfaz import Ui_MainWindow


# Tamaño real de la pantalla OLED usada en la práctica.
# La pantalla SSD1306 de esta actividad es de 128 pixeles de ancho por 64 de alto.
OLED_WIDTH = 128
OLED_HEIGHT = 64

# Dirección I2C detectada con el comando i2cdetect -y 1.
# En nuestro caso, la OLED apareció en la dirección 0x3C.
OLED_I2C_ADDRESS = 0x3C

# Escala visual para mostrar la OLED simulada más grande en la ventana.
# La OLED real es muy pequeña, así que en la GUI se multiplica por 3 para verla mejor.
SCALE = 3


class MiVentana(QtWidgets.QMainWindow):
    def __init__(self):
        """
        Constructor principal de la ventana.
        Aquí se inicializa la interfaz, la simulación OLED y la OLED física.
        """
        super().__init__()

        # Creamos el objeto de la interfaz gráfica definida en interfaz.py.
        self.ui = Ui_MainWindow()

        # setupUi construye todos los botones, cuadros de texto y elementos visuales.
        self.ui.setupUi(self)

        # Guardamos la ruta base del archivo actual.
        # Esto es útil para abrir imágenes como cabra.png o tec.png desde la misma carpeta.
        self.base_path = Path(__file__).parent

        # Variable donde se guardará la pantalla OLED física.
        # Inicia en None para que el programa pueda seguir funcionando aunque la OLED no esté conectada.
        self.oled_hardware = None

        # Configuramos primero la OLED simulada dentro de la interfaz.
        self.setup_oled_preview()

        # Después intentamos inicializar la OLED física por I2C.
        self.setup_oled_hardware()

        # Conectamos los botones de la interfaz con sus funciones.
        self.connect_buttons()

        # Limpiamos ambas pantallas al iniciar.
        self.clear_oled()

    def setup_oled_preview(self):
        """
        Crea la pantalla OLED simulada dentro de la ventana de PyQt5.

        Esta simulación fue útil para probar primero en laptop antes de pasar a Raspberry.
        También sirve como vista de depuración cuando el programa corre en Raspberry.
        """

        # Se oculta el textBrowser porque ese cuadro venía del diseño original,
        # pero en la versión final no lo usamos para mostrar la salida principal.
        self.ui.textBrowser.hide()

        # QLabel se usa como contenedor de imagen.
        # Aquí se mostrará la versión ampliada de lo que también se manda a la OLED real.
        self.oled_label = QtWidgets.QLabel(self.ui.centralwidget)

        # Posición y tamaño de la OLED simulada.
        # El tamaño real 128x64 se multiplica por SCALE para verla más grande.
        self.oled_label.setGeometry(
            QtCore.QRect(
                260,
                280,
                OLED_WIDTH * SCALE,
                OLED_HEIGHT * SCALE,
            )
        )

        # Estilo visual del recuadro que representa la OLED.
        # Se usa fondo negro porque la OLED real también trabaja con pixeles apagados en negro.
        self.oled_label.setStyleSheet("""
            QLabel {
                background-color: black;
                border: 2px solid #00b7ff;
                border-radius: 6px;
            }
        """)

        # Centramos el contenido dentro del QLabel.
        self.oled_label.setAlignment(QtCore.Qt.AlignCenter)

    def setup_oled_hardware(self):
        """
        Inicializa la pantalla OLED física SSD1306 usando comunicación I2C.

        Conexión usada:
        - VCC -> 3.3V
        - GND -> GND
        - SDA -> GPIO 2 / Pin 3
        - SCL -> GPIO 3 / Pin 5

        Se usa try/except para que el programa no se cierre si la OLED no está conectada.
        Esto permite probar la interfaz aunque el hardware falle o no esté disponible.
        """
        try:
            # Creamos el bus I2C usando los pines estándar de la Raspberry.
            i2c = busio.I2C(board.SCL, board.SDA)

            # Creamos el objeto de la pantalla OLED física.
            # Se especifica tamaño 128x64 y dirección 0x3C.
            self.oled_hardware = adafruit_ssd1306.SSD1306_I2C(
                OLED_WIDTH,
                OLED_HEIGHT,
                i2c,
                addr=OLED_I2C_ADDRESS,
            )

            # Limpiamos la OLED física al iniciar.
            self.oled_hardware.fill(0)
            self.oled_hardware.show()

            print(f"OLED física detectada en dirección I2C {hex(OLED_I2C_ADDRESS)}")

        except Exception as error:
            # Si ocurre un error, no se detiene el programa.
            # Solo se informa en terminal y se continúa usando la simulación.
            self.oled_hardware = None
            print(f"OLED física no disponible. Se usará solo simulación. Error: {error}")

    def connect_buttons(self):
        """
        Conecta cada botón de la interfaz con la función que debe ejecutar.

        Los nombres pushButton, pushButton_2, etc. vienen de interfaz.py.
        Aunque no son nombres muy descriptivos, se mantienen porque fueron generados
        desde el diseño de la interfaz.
        """
        self.ui.pushButton.clicked.connect(self.show_team_logo)       # Botón Logo
        self.ui.pushButton_2.clicked.connect(self.show_tec_logo)      # Botón Tec
        self.ui.pushButton_3.clicked.connect(self.show_three_tec)     # Botón 3 Tec
        self.ui.pushButton_4.clicked.connect(self.show_all_names)     # Botón Nombres
        self.ui.pushButton_5.clicked.connect(self.send_message)       # Botón Enviar Mensaje

    def clear_oled(self):
        """
        Limpia la OLED simulada y la OLED física.

        Se crea una imagen completamente negra de 128x64.
        En una OLED monocromática:
        - 0 significa pixel apagado.
        - 1 significa pixel encendido.
        """
        image = Image.new("1", (OLED_WIDTH, OLED_HEIGHT), 0)
        self.display_oled_image(image)

    def display_oled_image(self, image):
        """
        Muestra una misma imagen en dos salidas:
        1. OLED simulada dentro de PyQt5.
        2. OLED física SSD1306 por I2C.

        Esta función es importante porque centraliza la salida.
        Así, cualquier botón solo necesita generar una imagen y esta función se encarga
        de mostrarla en ambos lugares.
        """

        # Convertimos la imagen a modo "1", que es blanco y negro puro.
        # Esto es necesario porque la OLED SSD1306 no maneja colores.
        image = image.convert("1")

        # -----------------------------------------------------------------
        # Parte 1: mostrar imagen en la OLED simulada de PyQt5
        # -----------------------------------------------------------------

        # PyQt necesita una imagen RGB para poder mostrarla en QLabel,
        # por eso convertimos temporalmente la imagen binaria a RGB.
        rgb_image = image.convert("RGB")

        # QImage es el formato interno que usa Qt para manejar imágenes.
        qimage = QtGui.QImage(
            rgb_image.tobytes(),
            OLED_WIDTH,
            OLED_HEIGHT,
            OLED_WIDTH * 3,
            QtGui.QImage.Format_RGB888,
        )

        # Convertimos QImage a QPixmap, que es lo que QLabel puede mostrar.
        pixmap = QtGui.QPixmap.fromImage(qimage)

        # Escalamos la imagen sin suavizado.
        # Esto conserva el efecto de pixeles grandes, parecido a una OLED real.
        pixmap = pixmap.scaled(
            OLED_WIDTH * SCALE,
            OLED_HEIGHT * SCALE,
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.FastTransformation,
        )

        # Actualizamos la OLED simulada en pantalla.
        self.oled_label.setPixmap(pixmap)

        # -----------------------------------------------------------------
        # Parte 2: mandar imagen a la OLED física
        # -----------------------------------------------------------------

        # Solo se intenta mandar imagen si la OLED física fue detectada.
        if self.oled_hardware is not None:
            try:
                # Carga la imagen binaria en el buffer interno de la pantalla.
                self.oled_hardware.image(image)

                # show() actualiza físicamente la pantalla OLED.
                self.oled_hardware.show()

            except Exception as error:
                # Si hay error durante la transmisión, se avisa sin cerrar el programa.
                print(f"Error enviando imagen a OLED física: {error}")

    def get_font(self):
        """
        Regresa una fuente básica tipo bitmap.

        Al principio se probaron fuentes TrueType, pero se deformaban mucho en 128x64.
        La fuente default de Pillow no es la más elegante, pero en OLED se lee mejor
        porque está pensada para pixeles pequeños.
        """
        return ImageFont.load_default()

    def image_file_to_oled(self, filename, target_size=(OLED_WIDTH, OLED_HEIGHT)):
        """
        Convierte una imagen normal a formato compatible con OLED.

        Esta función se usa para convertir cabra.png y tec.png a blanco y negro.

        Proceso:
        1. Abrir la imagen.
        2. Redimensionarla sin deformarla.
        3. Pegarla en un canvas de 128x64.
        4. Detectar qué pixeles son dibujo y cuáles son fondo.
        5. Regresar una imagen binaria lista para la OLED.
        """
        image_path = self.base_path / filename

        # Validamos que el archivo exista antes de intentar abrirlo.
        if not image_path.exists():
            self.show_error(f"No se encontró: {filename}")
            return None

        # Abrimos la imagen en modo RGBA para conservar transparencia si existe.
        image = Image.open(image_path).convert("RGBA")

        # thumbnail ajusta el tamaño conservando proporción.
        # Esto evita que el logo se vea estirado.
        image.thumbnail(target_size, Image.LANCZOS)

        # Creamos un fondo blanco temporal de 128x64.
        # Luego se detecta el dibujo comparando contra este fondo.
        canvas = Image.new("RGBA", target_size, (255, 255, 255, 255))

        # Calculamos posición para centrar la imagen.
        x = (target_size[0] - image.width) // 2
        y = (target_size[1] - image.height) // 2

        # Pegamos la imagen centrada.
        canvas.paste(image, (x, y), image)

        # Convertimos el resultado a blanco y negro según diferencia con el fondo.
        return self.convert_to_oled_by_background(canvas)

    def convert_to_oled_by_background(self, image):
        """
        Convierte una imagen RGBA a una imagen OLED binaria.

        La parte rara aquí es la detección por distancia de color:
        - Se toma el pixel superior izquierdo como referencia del fondo.
        - Si un pixel es muy diferente al fondo, se considera parte del dibujo.
        - Si es parecido al fondo, se apaga.

        Esto permite usar imágenes con distintos colores sin tener que editarlas manualmente.
        """
        image = image.convert("RGBA")
        oled = Image.new("1", image.size, 0)

        pixels = image.load()
        oled_pixels = oled.load()

        # Tomamos el color del primer pixel como color de fondo.
        bg_r, bg_g, bg_b, _ = pixels[0, 0]

        for y in range(image.height):
            for x in range(image.width):
                r, g, b, a = pixels[x, y]

                # Si el pixel es transparente, se apaga.
                if a == 0:
                    oled_pixels[x, y] = 0
                    continue

                # Calculamos la distancia entre el color actual y el fondo.
                # Es una forma simple de medir qué tan diferente es un pixel.
                distance = sqrt(
                    (r - bg_r) ** 2 +
                    (g - bg_g) ** 2 +
                    (b - bg_b) ** 2
                )

                # Umbral elegido para separar fondo y dibujo.
                # Si la distancia es mayor a 45, se enciende el pixel.
                if distance > 45:
                    oled_pixels[x, y] = 1
                else:
                    oled_pixels[x, y] = 0

        return oled

    def show_team_logo(self):
        """
        Función del botón Logo.
        Convierte y muestra el logo del equipo.
        """
        image = self.image_file_to_oled("cabra.png")

        if image:
            self.display_oled_image(image)

    def show_tec_logo(self):
        """
        Función del botón Tec.
        Convierte y muestra el logo del Tecnológico de Monterrey.
        """
        image = self.image_file_to_oled("tec.png")

        if image:
            self.display_oled_image(image)

    def show_three_tec(self):
        """
        Función del botón 3 Tec.

        En vez de usar una imagen ya hecha con tres logos, se toma tec.png,
        se reduce de tamaño y se pega tres veces en una imagen nueva.
        Esto hace el código más flexible y demuestra procesamiento de imagen.
        """
        tec_path = self.base_path / "tec.png"

        if not tec_path.exists():
            self.show_error("No se encontró: tec.png")
            return

        # Creamos una imagen negra de 128x64.
        oled = Image.new("1", (OLED_WIDTH, OLED_HEIGHT), 0)

        # Abrimos el logo y lo hacemos más pequeño para que quepa tres veces.
        logo = Image.open(tec_path).convert("RGBA")
        logo.thumbnail((34, 34), Image.LANCZOS)

        # Creamos un canvas pequeño para cada logo.
        logo_canvas = Image.new("RGBA", (34, 34), (255, 255, 255, 255))

        # Centramos el logo dentro del canvas de 34x34.
        x = (34 - logo.width) // 2
        y = (34 - logo.height) // 2

        logo_canvas.paste(logo, (x, y), logo)

        # Convertimos el logo pequeño a formato OLED.
        logo_oled = self.convert_to_oled_by_background(logo_canvas)

        # Posiciones calculadas para distribuir los tres logos en línea.
        positions = [
            (5, 15),
            (47, 15),
            (89, 15),
        ]

        # Pegamos el mismo logo tres veces.
        for position in positions:
            oled.paste(logo_oled, position)

        self.display_oled_image(oled)

    def show_all_names(self):
        """
        Función del botón Nombres.

        La OLED tiene muy poco espacio, por eso se usaron abreviaciones.
        Se separa cada nombre y matrícula en dos líneas para que sea más legible.
        """
        oled = Image.new("1", (OLED_WIDTH, OLED_HEIGHT), 0)
        draw = ImageDraw.Draw(oled)

        font = self.get_font()

        lines = [
            "Luis F Salazar H",
            "A01738527",
            "Magdaleno P Olmos",
            "A01739632",
            "Fatima V Huerta C",
            "A01739997",
        ]

        y = 1

        for line in lines:
            draw.text((2, y), line, font=font, fill=1)
            y += 10

        self.display_oled_image(oled)

    def send_message(self):
        """
        Función del botón Enviar Mensaje.

        Lee lo que el usuario escribió en la caja de texto.
        Si está vacío, manda un mensaje por defecto.
        """
        message = self.ui.plainTextEdit.toPlainText().strip()

        if not message:
            message = "Mensaje vacio"

        self.show_text_on_oled(message)

    def show_text_on_oled(self, text):
        """
        Dibuja texto dentro de una imagen de 128x64.

        Primero se genera una imagen negra.
        Después se dibuja el texto en blanco.
        Finalmente se manda a la simulación y a la OLED física.
        """
        oled = Image.new("1", (OLED_WIDTH, OLED_HEIGHT), 0)
        draw = ImageDraw.Draw(oled)

        font = self.get_font()

        # Divide el mensaje en líneas para que no se salga de la pantalla.
        lines = self.wrap_text(text, max_chars=20)

        y = 4

        for line in lines[:6]:
            draw.text((4, y), line, font=font, fill=1)
            y += 10

        self.display_oled_image(oled)

    def wrap_text(self, text, max_chars=20):
        """
        Divide un texto largo en líneas más pequeñas.

        Esto es necesario porque la OLED no puede mostrar líneas largas.
        Se usa un límite aproximado de 20 caracteres por línea.
        """
        words = text.replace("\n", " \n ").split()
        lines = []
        current_line = ""

        for word in words:
            if word == "\n":
                if current_line:
                    lines.append(current_line)
                    current_line = ""
                continue

            # Si la palabra todavía cabe en la línea actual, se agrega.
            if len(current_line) + len(word) + 1 <= max_chars:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word

            # Si ya no cabe, se guarda la línea y se inicia otra.
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def show_error(self, message):
        """
        Muestra errores en terminal y también en la OLED.

        Esto ayuda a detectar problemas como archivos faltantes sin revisar solo la terminal.
        """
        print(f"ERROR: {message}")
        self.show_text_on_oled(f"ERROR:\n{message}")


if __name__ == "__main__":
    # Se crea la aplicación de PyQt5.
    app = QtWidgets.QApplication(sys.argv)

    # Se crea y muestra la ventana principal.
    ventana = MiVentana()
    ventana.show()

    # app.exec_() mantiene la ventana activa hasta que el usuario la cierre.
    sys.exit(app.exec_())
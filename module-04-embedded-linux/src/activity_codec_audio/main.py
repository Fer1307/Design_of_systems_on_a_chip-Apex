# ============================================================
# Materia: Diseño de Sistemas en Chip
# Actividad: Call Audio Codec Game
# Equipo: Luis Fernando Salazar Hernández - A01738527
#         Magdaleno Pérez Olmos - A01739632
#         Fatima Valeria Huerta Cabrera - A01739997
#
# Descripción general:
# Este programa implementa un juego en Raspberry Pi usando:
# - Una ventana de Pygame de 800x600 píxeles.
# - Un objeto móvil de 54x79 píxeles.
# - Botones físicos GPIO para mover la mira y disparar.
# - Una pantalla OLED SSD1306 por I2C para mostrar jugador, fecha y puntaje.
# - Un display de 7 segmentos para mostrar los disparos fallados.
# - Efectos de sonido para aciertos, fallos y música de fondo.
# ============================================================

import os
import sys

# Pygame se utiliza para crear la ventana del juego, dibujar imágenes,
# manejar sprites, detectar colisiones y reproducir sonidos.
import pygame

# Se usa la interfaz RPi.GPIO para controlar entradas y salidas digitales.
# En la Raspberry se puede instalar mediante rpi-lgpio, que funciona como
# reemplazo compatible de RPi.GPIO en versiones recientes de Raspberry Pi OS.
import RPi.GPIO as GPIO

from pygame.locals import *
from datetime import datetime

# Pillow permite crear la imagen que se enviará a la OLED.
# La pantalla SSD1306 trabaja con imágenes monocromáticas de 128x64 píxeles.
from PIL import Image, ImageDraw, ImageFont

# Estas librerías de Adafruit permiten usar el bus I2C de la Raspberry
# y comunicarse con la pantalla OLED SSD1306.
import board
import busio
import adafruit_ssd1306


# ============================================================
# CONFIGURACIÓN GPIO - NUMERACIÓN BCM
# ============================================================

# Se usa numeración BCM porque coincide con el número real de GPIO,
# no con el número físico del pin. Esto evita confusiones al programar.
GPIO.setmode(GPIO.BCM)

# Se desactivan advertencias para evitar mensajes repetidos cuando el programa
# se reinicia durante pruebas y los pines ya fueron configurados antes.
GPIO.setwarnings(False)

# Pines del display de 7 segmentos.
# La lista sigue el orden lógico de los segmentos: a, b, c, d, e, f, g.
#
# Tabla física usada:
# a -> pin 31 -> GPIO 6
# b -> pin 29 -> GPIO 5
# c -> pin 33 -> GPIO 13
# d -> pin 35 -> GPIO 19
# e -> pin 37 -> GPIO 26
# f -> pin 38 -> GPIO 20
# g -> pin 40 -> GPIO 21
SEGMENTS = [6, 5, 13, 19, 26, 20, 21]

# Pines de los botones físicos.
# Estos botones controlan la mira de la pistola y el disparo.
#
# Left  -> pin 16 -> GPIO 23
# Up    -> pin 15 -> GPIO 22
# Down  -> pin 13 -> GPIO 27
# Right -> pin 11 -> GPIO 17
# Shoot -> pin 7  -> GPIO 4
BTN_LEFT = 23
BTN_UP = 22
BTN_DOWN = 27
BTN_RIGHT = 17
BTN_SHOOT = 4

CONTROL_BUTTONS = [
    BTN_LEFT,
    BTN_UP,
    BTN_DOWN,
    BTN_RIGHT,
    BTN_SHOOT
]

# Los segmentos son salidas porque la Raspberry enciende o apaga cada LED
# del display de 7 segmentos.
for pin in SEGMENTS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# Los botones son entradas. Se usa resistencia pull-down interna para que,
# cuando el botón no está presionado, el valor leído sea LOW de forma estable.
# Al presionar el botón, el pin recibe HIGH.
for pin in CONTROL_BUTTONS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


# ============================================================
# CONFIGURACIÓN DEL DISPLAY DE 7 SEGMENTOS
# Cátodo común:
# 1 = segmento encendido
# 0 = segmento apagado
# Orden de segmentos: [a, b, c, d, e, f, g]
# ============================================================

# Cada arreglo representa qué segmentos deben encenderse para formar un dígito.
# Por ejemplo, el 0 enciende todos los segmentos excepto g.
DIGITS = [
    [1, 1, 1, 1, 1, 1, 0],  # 0
    [0, 1, 1, 0, 0, 0, 0],  # 1
    [1, 1, 0, 1, 1, 0, 1],  # 2
    [1, 1, 1, 1, 0, 0, 1],  # 3
    [0, 1, 1, 0, 0, 1, 1],  # 4
    [1, 0, 1, 1, 0, 1, 1],  # 5
    [1, 0, 1, 1, 1, 1, 1],  # 6
    [1, 1, 1, 0, 0, 0, 0],  # 7
    [1, 1, 1, 1, 1, 1, 1],  # 8
    [1, 1, 1, 1, 0, 1, 1],  # 9
]


def update_7segment(number):
    """
    Muestra en el display de 7 segmentos la cantidad de disparos fallados.

    Como el display usado solo tiene un dígito, se muestra únicamente de 0 a 9.
    Si el contador supera 9, se usa el último dígito. Por ejemplo:
    12 fallos se muestran como 2.
    """
    digit = number % 10

    for i in range(7):
        GPIO.output(SEGMENTS[i], DIGITS[digit][i])


# ============================================================
# CONFIGURACIÓN DE LA OLED SSD1306
# ============================================================

OLED_WIDTH = 128
OLED_HEIGHT = 64
OLED_I2C_ADDRESS = 0x3C

# La variable queda como None al inicio para permitir que el juego siga
# funcionando aunque la OLED no esté conectada o no sea detectada.
oled = None


def setup_oled():
    """
    Inicializa la pantalla OLED SSD1306 por I2C.

    Se usa try/except para que un error en la OLED no detenga todo el juego.
    Esto ayuda durante pruebas, porque permite seguir validando Pygame,
    botones y display de 7 segmentos aunque la OLED no esté disponible.
    """
    global oled

    try:
        i2c = busio.I2C(board.SCL, board.SDA)

        oled = adafruit_ssd1306.SSD1306_I2C(
            OLED_WIDTH,
            OLED_HEIGHT,
            i2c,
            addr=OLED_I2C_ADDRESS
        )

        oled.fill(0)
        oled.show()

        print("OLED detected successfully.")

    except Exception as error:
        oled = None
        print(f"OLED not available. Game will continue. Error: {error}")


def update_oled(score, player_name):
    """
    Actualiza la OLED con:
    - Nombre de la actividad
    - Nombre del jugador
    - Puntaje de aciertos
    - Fecha actual

    La OLED se actualiza principalmente cuando cambia el puntaje, no en cada
    frame del juego. Esto evita trabajo innecesario en el bus I2C.
    """
    if oled is None:
        return

    try:
        image = Image.new("1", (OLED_WIDTH, OLED_HEIGHT), 0)
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()

        date = datetime.now().strftime("%d/%m/%Y")

        draw.text((0, 0), "CALL AUDIO CODEC", font=font, fill=1)
        draw.text((0, 18), f"Player: {player_name}", font=font, fill=1)
        draw.text((0, 34), f"Score: {score}", font=font, fill=1)
        draw.text((0, 50), date, font=font, fill=1)

        oled.image(image)
        oled.show()

    except Exception as error:
        print(f"Error updating OLED: {error}")


def clear_oled():
    """
    Limpia la pantalla OLED al cerrar el juego.
    """
    if oled is not None:
        try:
            oled.fill(0)
            oled.show()
        except Exception:
            pass


# ============================================================
# CONFIGURACIÓN DE PYGAME
# ============================================================

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Tamaño solicitado para el objeto móvil de la actividad.
TARGET_WIDTH = 54
TARGET_HEIGHT = 79

# Velocidad de movimiento de la mira. Un valor pequeño da más control,
# mientras que uno muy alto hace difícil apuntar con precisión.
MOVE_SPEED = 6

PLAYER_NAME = "Fernando"

# Se usan rutas relativas a la ubicación del archivo.
# Esto permite mover la carpeta del proyecto a otra Raspberry o a otro repo
# sin depender de rutas absolutas como /home/pi/... o rutas de Windows.
main_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(main_dir, "assets")


def load_image(name, colorkey=None):
    """
    Carga una imagen desde la carpeta assets.

    Si colorkey es None, se usa convert_alpha() para conservar transparencias
    PNG y mejorar el rendimiento al dibujar la imagen en Pygame.

    Si se usa colorkey, se toma un color como transparente. Esto es útil para
    imágenes que no tienen canal alfa pero sí tienen un fondo de color fijo.
    """
    fullname = os.path.join(data_dir, name)

    try:
        image = pygame.image.load(fullname)

    except pygame.error:
        print(f"Cannot load image: {fullname}")
        raise SystemExit(str(pygame.get_error()))

    if colorkey is None:
        image = image.convert_alpha()
    else:
        image = image.convert()

        if colorkey == -1:
            colorkey = image.get_at((0, 0))

        image.set_colorkey(colorkey, RLEACCEL)

    return image, image.get_rect()


# ============================================================
# SPRITES DEL JUEGO
# ============================================================

class Fist(pygame.sprite.Sprite):
    """
    Representa la mira o pistola del jugador.

    Antes podía controlarse con el mouse, pero en esta versión se controla
    con botones físicos para cumplir con el uso de GPIO en la Raspberry Pi.
    """

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.image, self.rect = load_image("pistola.png", None)
        self.punching = 0

        # Posición inicial al centro para que el jugador empiece desde una
        # ubicación equilibrada dentro de la ventana.
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    def update(self):
        """
        Actualiza la posición de la mira leyendo los botones GPIO.
        """
        if GPIO.input(BTN_LEFT) == GPIO.HIGH:
            self.rect.x -= MOVE_SPEED

        if GPIO.input(BTN_RIGHT) == GPIO.HIGH:
            self.rect.x += MOVE_SPEED

        if GPIO.input(BTN_UP) == GPIO.HIGH:
            self.rect.y -= MOVE_SPEED

        if GPIO.input(BTN_DOWN) == GPIO.HIGH:
            self.rect.y += MOVE_SPEED

        # Evita que la mira salga de la ventana. Esto mantiene el control
        # dentro del área visible del juego.
        screen_rect = pygame.display.get_surface().get_rect()
        self.rect.clamp_ip(screen_rect)

        # Pequeño movimiento visual al disparar para dar retroalimentación
        # al jugador.
        if self.punching:
            self.rect.move_ip(5, 10)

    def punch(self, target):
        """
        Revisa si la mira está tocando al objetivo al momento del disparo.
        """
        if not self.punching:
            self.punching = 1

            # Se reduce ligeramente el área de colisión para que el acierto
            # dependa más de apuntar al centro de la mira y no solo de rozar
            # los bordes de la imagen.
            hitbox = self.rect.inflate(-5, -5)
            return hitbox.colliderect(target.rect)

        return False

    def unpunch(self):
        """
        Libera el estado de disparo cuando el botón deja de estar presionado.
        """
        self.punching = 0


class Chimp(pygame.sprite.Sprite):
    """
    Representa el objeto móvil que el jugador debe acertar.

    El nombre de la clase se mantiene por la base original del ejemplo
    'chimp', aunque en esta versión la imagen usada es duck.png.
    """

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.image, self.rect = load_image("duck.png", -1)

        # Se escala el objetivo al tamaño requerido por la actividad: 54x79 px.
        self.image = pygame.transform.scale(
            self.image,
            (TARGET_WIDTH, TARGET_HEIGHT)
        )

        self.rect = self.image.get_rect()

        # Se guarda una copia original para poder rotar la imagen sin acumular
        # deformaciones por rotaciones repetidas sobre una imagen ya rotada.
        self.original = self.image

        screen = pygame.display.get_surface()
        self.area = screen.get_rect()

        self.rect.topleft = 10, 10

        # Movimiento inicial del objetivo en x e y.
        self.move = [3, 2]

        # dizzy controla la animación de giro después de un acierto.
        self.dizzy = 0

    def update(self):
        if self.dizzy:
            self._spin()
        else:
            self._walk()

    def _walk(self):
        """
        Mueve el objetivo y lo hace rebotar cuando llega a los bordes.
        """
        newpos = self.rect.move(self.move)

        if self.rect.left < self.area.left or self.rect.right > self.area.right:
            self.move[0] = -self.move[0]
            newpos = self.rect.move(self.move)

            # Se voltea la imagen horizontalmente para que visualmente parezca
            # que cambia de dirección al rebotar.
            self.image = pygame.transform.flip(self.image, 1, 0)
            self.original = pygame.transform.flip(self.original, 1, 0)

        if self.rect.top < self.area.top or self.rect.bottom > self.area.bottom:
            self.move[1] = -self.move[1]
            newpos = self.rect.move(self.move)

        self.rect = newpos

    def _spin(self):
        """
        Rota el objetivo después de recibir un acierto.
        """
        center = self.rect.center
        self.dizzy += 12

        if self.dizzy >= 360:
            self.dizzy = 0
            self.image = self.original
        else:
            self.image = pygame.transform.rotate(self.original, self.dizzy)

        # Al rotar una imagen, cambia su rectángulo. Por eso se recalcula el
        # rect manteniendo el mismo centro, evitando saltos visuales.
        self.rect = self.image.get_rect(center=center)

    def punched(self):
        """
        Activa la animación de giro cuando el objetivo recibe un disparo.
        """
        if not self.dizzy:
            self.dizzy = 1


# ============================================================
# JUEGO PRINCIPAL
# ============================================================

def main():
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Call Audio Codec Game")

    # Se oculta el mouse porque el control principal del juego se hace con
    # botones físicos conectados a GPIO.
    pygame.mouse.set_visible(False)

    setup_oled()

    # Contadores principales del juego.
    # hits se muestra en la OLED y misses en el display de 7 segmentos.
    hits = 0
    misses = 0

    update_oled(hits, PLAYER_NAME)
    update_7segment(misses)

    # --------------------------------------------------------
    # Cargar fondo
    # --------------------------------------------------------
    try:
        background_path = os.path.join(data_dir, "fondo.png")
        background = pygame.image.load(background_path).convert()

        # Se escala el fondo al tamaño de la pantalla para asegurar que cubra
        # toda la ventana de 800x600.
        background = pygame.transform.scale(background, screen.get_size())

    except pygame.error:
        # Si no existe el fondo, el juego todavía puede ejecutarse con fondo
        # negro. Esto facilita pruebas cuando falta algún asset.
        print("Background image not found. Using black background.")
        background = pygame.Surface(screen.get_size())
        background.fill((0, 0, 0))

    # --------------------------------------------------------
    # Cargar sonidos
    # --------------------------------------------------------
    punch_sound = None
    whiff_sound = None
    back_sound = None

    try:
        punch_sound = pygame.mixer.Sound(os.path.join(data_dir, "hit.wav"))
        whiff_sound = pygame.mixer.Sound(os.path.join(data_dir, "failed_hit.wav"))
        back_sound = pygame.mixer.Sound(os.path.join(data_dir, "fondo.wav"))

        # El sonido de fondo se deja con volumen bajo para que no tape los
        # efectos de acierto y fallo.
        back_sound.set_volume(0.2)

        # -1 indica que el audio de fondo se reproduce en bucle.
        back_sound.play(-1)

    except pygame.error as error:
        print(f"Warning: Some sounds could not be loaded: {error}")

    # --------------------------------------------------------
    # Fuentes
    # --------------------------------------------------------
    font_title = pygame.font.Font(None, 36)
    font_score = pygame.font.Font(None, 30)

    title_text = font_title.render(
        "TE2003 - Embedded Systems Game",
        True,
        (255, 255, 255)
    )

    title_pos = title_text.get_rect(
        centerx=background.get_width() / 2,
        top=10
    )

    # El título se dibuja una sola vez sobre el fondo, porque no cambia durante
    # el juego. Esto evita renderizar el mismo texto en cada frame.
    background.blit(title_text, title_pos)

    # --------------------------------------------------------
    # Sprites
    # --------------------------------------------------------
    chimp = Chimp()
    fist = Fist()

    # RenderPlain agrupa los sprites para actualizarlos y dibujarlos juntos.
    allsprites = pygame.sprite.RenderPlain((fist, chimp))

    clock = pygame.time.Clock()
    going = True

    # Evita contar muchos disparos mientras el botón se mantiene presionado.
    # Sin esta bandera, el juego podría sumar varios disparos por segundo.
    shoot_pressed = False

    # ========================================================
    # CICLO PRINCIPAL DEL JUEGO
    # ========================================================

    try:
        while going:
            # Limita el juego a 60 FPS. Esto mantiene la animación fluida y
            # evita usar CPU de forma innecesaria.
            clock.tick(60)

            # -----------------------------------------------
            # Eventos de Pygame
            # -----------------------------------------------
            for event in pygame.event.get():
                if event.type == QUIT:
                    going = False

                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    going = False

            # -----------------------------------------------
            # Botón físico de disparo
            # -----------------------------------------------
            if GPIO.input(BTN_SHOOT) == GPIO.HIGH and not shoot_pressed:
                shoot_pressed = True

                if fist.punch(chimp):
                    if punch_sound:
                        punch_sound.play()

                    chimp.punched()
                    hits += 1

                    # La OLED muestra el puntaje de aciertos.
                    update_oled(hits, PLAYER_NAME)

                else:
                    if whiff_sound:
                        whiff_sound.play()

                    misses += 1

                    # El display de 7 segmentos muestra los fallos.
                    update_7segment(misses)

            if GPIO.input(BTN_SHOOT) == GPIO.LOW:
                shoot_pressed = False
                fist.unpunch()

            # -----------------------------------------------
            # Actualizar sprites
            # -----------------------------------------------
            allsprites.update()

            # -----------------------------------------------
            # Dibujar pantalla
            # -----------------------------------------------
            screen.blit(background, (0, 0))

            hit_text = font_score.render(
                f"Atinados: {hits}",
                True,
                (0, 255, 0)
            )

            miss_text = font_score.render(
                f"Fallados: {misses}",
                True,
                (255, 50, 50)
            )

            screen.blit(hit_text, (20, 20))
            screen.blit(miss_text, (20, 50))

            allsprites.draw(screen)
            pygame.display.flip()

    except KeyboardInterrupt:
        print("Game interrupted by user.")

    finally:
        # Limpieza final para dejar el hardware en un estado seguro.
        clear_oled()
        update_7segment(0)
        pygame.quit()
        GPIO.cleanup()
        sys.exit()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

import cv2
import numpy as np
import serial
import time

SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 9600

FRAME_WIDTH = 320
FRAME_HEIGHT = 240

ROI_TOP_RATIO = 0.65
ROI_BOTTOM_RATIO = 0.85
ROI_MARGIN_X = 20

GAUSSIAN_KERNEL = (5, 5)
THRESHOLD_VALUE = 150
THRESH_MODE = cv2.THRESH_BINARY_INV

DEAD_ZONE = 25

CMD_FORWARD = b"F"
CMD_LEFT = b"L"
CMD_RIGHT = b"R"
CMD_STOP = b"S"


def build_roi_vertices(width, height):
    y_top = int(height * ROI_TOP_RATIO)
    y_bottom = int(height * ROI_BOTTOM_RATIO)

    return np.array([[
        (ROI_MARGIN_X, y_bottom),
        (ROI_MARGIN_X, y_top),
        (width - ROI_MARGIN_X, y_top),
        (width - ROI_MARGIN_X, y_bottom),
    ]], dtype=np.int32)


try:
    arduino = serial.Serial(
        SERIAL_PORT,
        BAUD_RATE,
        timeout=0.1
    )
    time.sleep(2)
    print("Arduino conectado")

except Exception as e:
    print("Error serial:", e)
    exit()


cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

ret, frame = cap.read()

if not ret:
    print("No se pudo abrir la cámara")
    arduino.close()
    exit()

roi_vertices = build_roi_vertices(
    frame.shape[1],
    frame.shape[0]
)

print("Seguidor iniciado")

while True:
    ret, frame = cap.read()

    if not ret:
        break

    h, w = frame.shape[:2]
    center_x = w // 2

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(
        gray,
        GAUSSIAN_KERNEL,
        0
    )

    _, thresh = cv2.threshold(
        blur,
        THRESHOLD_VALUE,
        255,
        THRESH_MODE
    )

    mask = np.zeros_like(thresh)
    cv2.fillPoly(mask, roi_vertices, 255)

    masked = cv2.bitwise_and(thresh, mask)

    moments = cv2.moments(masked)

    debug = frame.copy()

    roi_center_y = int(
        h * (ROI_TOP_RATIO + ROI_BOTTOM_RATIO) / 2
    )

    cv2.polylines(
        debug,
        [roi_vertices],
        True,
        (0, 255, 255),
        2
    )

    cv2.circle(
        debug,
        (center_x, roi_center_y),
        8,
        (255, 0, 0),
        2
    )

    if moments["m00"] > 0:
        line_center_x = int(
            moments["m10"] / moments["m00"]
        )

        error = line_center_x - center_x
        giro = error

        cv2.circle(
            debug,
            (line_center_x, roi_center_y),
            8,
            (0, 0, 255),
            -1
        )

        if error < -DEAD_ZONE:
            command = CMD_LEFT

        elif error > DEAD_ZONE:
            command = CMD_RIGHT

        else:
            command = CMD_FORWARD

    else:
        giro = 0
        command = CMD_FORWARD

    arduino.write(command)

    print(
        f"\rGiro: {giro} | Comando: {command.decode()}",
        end=""
    )

    cv2.imshow("Seguidor", debug)
    cv2.imshow("ROI", masked)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        arduino.write(CMD_STOP)
        break


cap.release()
arduino.close()
cv2.destroyAllWindows()
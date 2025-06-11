import numpy as np
import cv2
from mss import mss
import pyautogui as pg
import keyboard
import time
import os

# Definirea zonelor de captură pentru Full HD (îți recomand să le ajustezi în funcție de monitorul tău)
monitor_without_man_left = {'top': 543, 'left': 630, 'width': 250, 'height': 100}  
monitor_with_man_left = {'top': 680, 'left': 630, 'width': 250, 'height': 200}
monitor_without_man_right = {'top': 543, 'left': 1040, 'width': 250, 'height': 100}
monitor_with_man_right = {'top': 680, 'left': 1040, 'width': 250, 'height': 200}

# Funcția pentru a salva capturi de ecran din zonele definite
def save_screenshot(region, file_name):
    with mss() as sct:
        img = sct.grab(region)
        img = np.array(img)
        cv2.imwrite(file_name, img)  # Salvează imaginea cu nuqmyele specificat
    print(f"Imagine salvată: {file_name}")

# Funcția pentru a vizualiza capturile de ecran
def show_screenshot(region):
    with mss() as sct:
        img = sct.grab(region)
        img = np.array(img)
        cv2.imshow('Captured Image', img)  # Afișează imaginea captuyraqtă
        cv2.waitKey(0)  # Așteaptă o tastă apăsată
        cv2.destroyAllWindows()

# Testează fiecare zonă de captură și salvează imaginile
save_screenshot(monitor_without_man_left, 'monitor_without_man_left.png')
save_screenshot(monitor_with_man_left, 'monitor_with_man_left.png')
save_screenshot(monitor_without_man_right, 'monitor_without_man_right.png')
save_screenshot(monitor_with_man_right, 'monitor_with_man_right.png')

# Funcția pentru a procesa imaginea (convertire în gri și detectarea marginilor)
def process_image(original_image):
    image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    
    grad_x = cv2.Sobel(image, cv2.CV_16S, 1, 0)
    grad_y = cv2.Sobel(image, cv2.CV_16S, 0, 1)
    abs_grad_x = cv2.convertScaleAbs(grad_x)
    abs_grad_y = cv2.convertScaleAbs(grad_y)
    edge_image = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)

    edge_image = cv2.Canny(edge_image, threshold1=50, threshold2=150)  # Detectare margini
    return edge_image

# Funcția principală pentru capturarea ecranului și detectarea acțiunii
def screen_record():
    with mss() as sct:
        while True:
            if keyboard.is_pressed('Y'):
                # Capturăm imaginea din regiunile definite
                img1 = sct.grab(monitor_without_man_left)
                img1 = np.array(img1)
                processed_image = process_image(img1)
                mean1 = np.mean(processed_image)

                img2 = sct.grab(monitor_with_man_left)
                img2 = np.array(img2)
                processed_image = process_image(img2)
                mean2 = np.mean(processed_image)

                print(f"mean1: {mean1}, mean2: {mean2}")  # Afișăm valorile pentru diagnosticare

                button = 'left'

                while True:
                    # Acum verificăm condițiile de detecție pentru schimbarea butonului
                    if mean1 > 30:  # Ajustează pragul pentru detectarea unei schimbări clare
                        if button == 'left':
                            pg.press('right')
                            button = 'right'
                        else:
                            pg.press('left')
                            button = 'left'
                    elif mean2 > 30 and mean2 < 40:  # Ajustează pentru o diferență mai clară
                        if button == 'left':
                            pg.press('right')
                            button = 'right'
                        else:
                            pg.press('left')
                            button = 'left'
                    else:
                        if button == 'left':
                            pg.press('left')
                        else:
                            pg.press('right')

                    # Așteaptă o perioadă scurtă între apăsările butoanelor
                    time.sleep(0.04)  # Ajustează timpul de pauză în secunde (de exemplu, 0.5 secunde)

                    # Actualizăm imaginea pentru monitorul stâng sau drept
                    if button == 'left':
                        img1 = sct.grab(monitor_without_man_left)
                        img1 = np.array(img1)
                        processed_image = process_image(img1)
                        mean1 = np.mean(processed_image)

                        img2 = sct.grab(monitor_with_man_left)
                        img2 = np.array(img2)
                        processed_image = process_image(img2)
                        mean2 = np.mean(processed_image)
                    elif button == 'right':
                        img1 = sct.grab(monitor_without_man_right)
                        img1 = np.array(img1)
                        processed_image = process_image(img1)
                        mean1 = np.mean(processed_image)

                        img2 = sct.grab(monitor_with_man_right)
                        img2 = np.array(img2)
                        processed_image = process_image(img2)
                        mean2 = np.mean(processed_image)

                    if keyboard.is_pressed('q'):
                        print("Botul este oprit prin apăsarea tastei 'q'")
                        return

# Mesajul de pornire al botului
def info():
    print('Hi, this is a bot for playing in Timberman.')
    print('If you want to run the bot, then:')
    print('1) Open your game;')
    print('2) Press the start button;')
    print('3) Then press "Y".')
    print('If you want to stop the bot then press "q".')
    print('The bot works in a green summer forest.')

# Rulăm funcția
if __name__ == '__main__':
    info()
    screen_record()

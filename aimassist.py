import vgamepad as vg
from pynput import mouse

# Creează un controller virtual DualShock 4
gamepad = vg.VDS4Gamepad()

def on_click(x, y, button, pressed):
    if button == mouse.Button.left:  # click stânga -> X (Cross)
        if pressed:
            gamepad.press_button(button=vg.DS4_BUTTONS.DS4_BUTTON_CROSS)
        else:
            gamepad.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_CROSS)

    elif button == mouse.Button.right:  # click dreapta -> □ (Square)
        if pressed:
            gamepad.press_button(button=vg.DS4_BUTTONS.DS4_BUTTON_SQUARE)
        else:
            gamepad.release_button(button=vg.DS4_BUTTONS.DS4_BUTTON_SQUARE)

    gamepad.update()

# Ascultă clickurile mouse-ului
with mouse.Listener(on_click=on_click) as listener:
    listener.join()

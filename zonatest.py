import pyautogui

# Poziția curentă a cursorului pe partea stângă
print("Plasează cursorul pe zona stângă și apasă Enter pentru a obține coordonatele.")
input("Apasă Enter pentru a începe...")
left_position = pyautogui.position()
print("Coordenatele pentru zona stângă sunt: ", left_position)

# Poziția curentă a cursorului pe partea dreaptă
print("Plasează cursorul pe zona dreaptă și apasă Enter pentru a obține coordonatele.")
input("Apasă Enter pentru a începe...")
right_position = pyautogui.position()
print("Coordenatele pentru zona dreaptă sunt: ", right_position)



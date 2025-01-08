from pyfirmata2 import Arduino, util
import time
from LCD import LCD


# Vervang 'COM5' door de poort die je Arduino gebruik
board = Arduino('COM4')
board.samplingOn(100)
lcd = LCD(board)

#wachtrij_vol toevoegen dan + aan het einde teoveogen

def line2_lcd():
    global wachttijd, bezoeker_in_wachtrij, wachtrij_max


    progressbar_blocks = 0
    geformatteerde_string = ""
    progressbar_percentage = 0

    #edgecases
    if not wachttijd or not aantal_personen or not max_aantal_personen:
        print("01, Ongeldige invoer")
        return("Error01")
    
    if len(str(wachttijd)) > 3:
        print("02, Wachttijd is te lang om op de display weer te geven")
        return("Error 02")
    
    #progressbar percentage & blocks berekenen
    progressbar_percentage = round(aantal_personen * 100 / max_aantal_personen) if (aantal_personen * 100 / max_aantal_personen) < 100 else 100
    progressbar_blocks = int((round(progressbar_percentage, -1)  / 10) /2)

    ### - PROGRESSBAR
    #stringlogic om progressbar te maken
    geformatteerde_progressbar = ""
    progressbar_blocks_empty = 5 - progressbar_blocks
    full_block = chr(255)

    geformatteerde_progressbar = full_block * progressbar_blocks + progressbar_blocks_empty * " "
    print(geformatteerde_progressbar)

    #Scheiding toevoegen
    geformatteerde_progressbar += "|"

    #Percentage toevoegen
    geformatteerde_progressbar += str(progressbar_percentage) + "%"

    ### - WACHTTIJD
    #Wachttijd aan het einde toevoegen en de overige ruimte in het midden opvullen met spaties

    if wachttijd >= 60:
        geformatteerde_wachttijd = wachttijd / 60
        if geformatteerde_wachttijd.is_integer():
            geformatteerde_wachttijd = str(int(geformatteerde_wachttijd)) + "h"
        else:
            geformatteerde_wachttijd = str(round(geformatteerde_wachttijd, 1)) + "h"

    else:
        geformatteerde_wachttijd = str(wachttijd) + "m"


    opvullende_spaties = 16 - len(geformatteerde_progressbar) - len(geformatteerde_wachttijd)
    geformatteerde_line2_lcd = geformatteerde_progressbar + (opvullende_spaties * " ") + geformatteerde_wachttijd
    print(geformatteerde_line2_lcd)
    print(f"lengte string = {len(geformatteerde_line2_lcd)}")
    return str(geformatteerde_line2_lcd)

def update_lcd():
    global elapsed_since_lcd_update, wachttijd, bezoeker_in_wachtrij, wachtrij_max
    if elapsed_since_lcd_update >= 2:
        lcd.clear()
        lcd.print("test")
        lcd.set_cursor(0,1)
        lcd.print(line2_lcd())
        print("LCD has been refreshed")

        elapsed_since_lcd_update = 0
        elapsed_since_lcd_update = time.time()

    else:
        time.sleep(0.1)







# line2_lcd_value = line2_lcd(int(input("Wachttijd in minuten : ")), int(input("Aantal Personen in wachtrij : ")), int(input("Maximaal aantal personen in wachtrij : ")))

wachttijd, bezoeker_in_wachtrij, wachtrij_max = 0, 0, 10
elapsed_since_lcd_update = time.time()

lcd.clear()
lcd.print("Ugly ass nigga")
lcd.set_cursor(0, 1)
lcd.print("UGly Ass Hitl")
while True:
    wachttijd += 1
    bezoeker_in_wachtrij += 0.5
    update_lcd()
    print(f"Elapsed Time = {elapsed_since_lcd_update}")
    time.sleep(0.5)



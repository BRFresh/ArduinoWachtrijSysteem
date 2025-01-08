from pyfirmata2 import Arduino
import time


### - Setupwerk
board = Arduino('COM4')
board.samplingOn(10)

pin2_input = board.get_pin('d:2:i')  # Digital pin 2 as input
pin3_output = board.get_pin('d:3:o')  # Digital pin 3 as output
pin4_input = board.get_pin('d:4:i')
pin5_output = board.get_pin('d:5:o')
pin6_input = board.get_pin('d:6:i')
pin7_output = board.get_pin('d:7:o')

# reporting
pin2_input.enable_reporting()
pin4_input.enable_reporting()
pin6_input.enable_reporting()

# power pins configreren voor sensoren (5v 40mA max)
pin3_output.write(1)
pin5_output.write(1)
pin7_output.write(1)

#Callback functies
def pin2_callback(data):
    global pin2_value
    pin2_value = data

def pin4_callback(data):
    global pin4_value
    pin4_value = data

def pin6_callback(data):
    global pin6_value
    pin6_value = data

pin2_input.register_callback(pin2_callback)
pin4_input.register_callback(pin4_callback)
pin6_input.register_callback(pin6_callback)

### |

### - Def functies


def bezoeker_in():
    # Wait for PIN2 to go from True to False
    if pin2_value:  # Check if PIN2 starts as True
        start_time = time.time()
        while pin2_value:  # Wait until PIN2 becomes False
            if time.time() - start_time > 1:  # Timeout after 1 second
                return 0

        # PIN2 is now False; start waiting for PIN6 to go True
        start_time = time.time()
        while not pin6_value:  # Wait until PIN6 becomes True
            if time.time() - start_time > 1:  # Timeout after 1 second
                return 0

        # PIN6 is now True; wait for it to become False
        start_time = time.time()
        while pin6_value:  # Wait until PIN6 becomes False
            if time.time() - start_time > 1:  # Timeout after 1 second
                return 0

        # Successful sequence
        return 1
    else:
        # PIN2 was not True at the start
        return 0

def bezoeker_uit():
    if pin4_value:

        while True:
            if pin4_value:
                continue

            else:
                return 1

    else:
        return 0

def bezoeker_uit_via_ingang():

    if pin6_value:  # Check if PIN6 starts as True
        start_time = time.time()
        while pin6_value:  # Wait until PIN6 becomes False
            if time.time() - start_time > 1:  # Timeout after 1 second
                return 0

        # PIN6 is now False; start waiting for PIN2 to go True
        start_time = time.time()
        while not pin2_value:  # Wait until PIN2 becomes True
            if time.time() - start_time > 1:  # Timeout after 1 second
                return 0

        # PIN2 is now True; wait for it to become False
        start_time = time.time()
        while pin2_value:  # Wait until PIN2 becomes False
            if time.time() - start_time > 1:  # Timeout after 1 second
                return 0

        # Successful sequence
        return 1
    else:
        # PIN6 was not True at the start
        return 0


def bepaal_update_status():
    global status
    #Percentage 100 maken als deze groter is dan 100 hier later een check() voor maken en in de main loop zetten
    percentage_gevuld = (bezoeker_in_wachtrij * 100 / wachtrij_max) if bezoeker_in_wachtrij * 100 / wachtrij_max <= 100 else 100


    if percentage_gevuld >= 91:
        status = "Vol"
    elif percentage_gevuld >= 71:
        status = "Bijna vol"
    elif percentage_gevuld >= 31:
        status = "Gevuld"
    elif percentage_gevuld >= 11:
        status = "Licht gevuld"
    else:
        status = "Leeg"


    #Overvol toevoegen als helemaal vol?

def check_overflow_of_negatief_aantal_bezoekers(wachtrij_uitgang_type):
    #bezoeker in
    if wachtrij_uitgang_type == 1:
        if bezoeker_in_wachtrij + 1 > wachtrij_max:
            print("Overflow: Wachtrij is vol er kan niemand meer bij")

            return True
        else:
            return False


    #bezoeker uit
    elif wachtrij_uitgang_type == 2:
        if bezoeker_in_wachtrij - 1 < 0:
            print("Underflow: Wachtrij is al leeg er kan niemand meer uit")
            return True

        else:
            return False
    #bezoeker uit via ingang
    elif wachtrij_uitgang_type == 3:
        if bezoeker_in_wachtrij - 1 < 0:
            print("Underflow: Wachtrij is al leeg er kan niemand meer uit")
            return True

        else:
            return False

def bereken_wachttijd():
    global wachttijd
    wachttijd = bezoeker_in_wachtrij / verwerkingstijd_per_minuut

def line2_lcd():
    global wachttijd, aantal_personen, max_aantal_personen


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
    global elapsed_since_lcd_update, wachttijd, aantal_personen, max_aantal_personen
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










### |


### - Main loop

# defineer variabelen
# previous_pin2_value, previous_pin4_value = False, False
bezoeker_in_wachtrij, wachtrij_max = 0, 10
pin2_value, pin4_value, pin6_value = False, False, False
verwerkingstijd_per_minuut, wachttijd = 0.5, 0
last_update = time.time()

previous_string = ""
status = ""

# EdgeCases
if not wachtrij_max or wachtrij_max < 1:
    print("06 Wachtrij max heeft een ongeldige waarde")
    exit()

if bezoeker_in_wachtrij < 0 or bezoeker_in_wachtrij > wachtrij_max:
    print("07 Bezoekers in de wachtrij heeft een ongeldige waarde")
    exit()


while True:
    # debug_info = f"pin 2 = {pin2_value}, pin 4 = {pin4_value}, er zitten nu {bezoeker_in_wachtrij} in de wachtrij, status = {status}"
    # if debug_info != previous_string:
    #     print(debug_info)
    #     previous_string = debug_info

    debug_info = f"pin 2 = {pin2_value}, pin 6 = {pin6_value}, er zitten nu {bezoeker_in_wachtrij} in de wachtrij, status = {status} en de inloop = {wachttijd} min"
    if debug_info != previous_string:
        print(debug_info)
        previous_string = debug_info



    if bezoeker_in():
        if check_overflow_of_negatief_aantal_bezoekers(1):
            continue

        else:
            bezoeker_in_wachtrij += 1
            bereken_wachttijd()
            bepaal_update_status()

        time.sleep(0.01)


    elif bezoeker_uit():
        if check_overflow_of_negatief_aantal_bezoekers(2):
            continue

        else:
            bezoeker_in_wachtrij -= 1
            bepaal_update_status()

        time.sleep(0.01)


    elif bezoeker_uit_via_ingang():
        if check_overflow_of_negatief_aantal_bezoekers(3):
            continue

        else:
            bezoeker_in_wachtrij -= 1
            bepaal_update_status()

        time.sleep(0.01)


    else:
        time.sleep(0.01)
        bereken_wachttijd()


    update_lcd()




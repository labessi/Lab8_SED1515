# setup.py - SED1515 Lab 8 : cinématique inverse et étalonnage
import math, time
from machine import Pin, PWM

LA, LB = 155, 155          # longueurs des bras (mm)
AX, AY = -50, 139.7        # position de l'épaule (mm)
STYLO_HAUT, STYLO_BAS = 0, 30

def creer_servo(pin):
    s = PWM(Pin(pin)); s.freq(50); return s

servo_epaule, servo_coude, servo_stylo = creer_servo(0), creer_servo(1), creer_servo(2)

def envoyer_angle(servo, angle):
    angle = max(0, min(180, angle))                       # protège le servo
    servo.duty_u16(int((500 + angle * 2000 / 180) * 65535 / 20000))

def stylo(baisse):
    envoyer_angle(servo_stylo, STYLO_BAS if baisse else STYLO_HAUT)
    time.sleep(0.3)

def cinematique_inverse(x, y):
    """Position du stylo (mm) -> angles des servos épaule et coude (degrés)."""
    ac = math.sqrt((AX - x)**2 + (AY - y)**2)
    abase_c = math.sqrt((AX - x)**2 + y**2)
    bac = math.acos((LA**2 + ac**2 - LB**2) / (2 * LA * ac))
    acb = math.asin(LA * math.sin(bac) / LB)
    yac = math.acos((AY**2 + ac**2 - abase_c**2) / (2 * AY * ac))
    return math.degrees(bac + yac) - 75, 150 - math.degrees(bac + acb)

def calibration_configuration(fichier):
    """Lignes 'servo désiré réel' -> {servo: [(désiré, désiré - réel), ...]}."""
    table = {"epaule": [], "coude": []}
    for ligne in open(fichier):
        if ligne.strip() and not ligne.startswith("#"):
            servo, desire, reel = ligne.split()
            table[servo].append((float(desire), float(desire) - float(reel)))
    for servo in table:
        table[servo].sort()
    return table

def correction(points, angle):
    """Interpolation linéaire entre deux mesures (prises aux 10 degrés)."""
    for (a0, c0), (a1, c1) in zip(points, points[1:]):
        if a0 <= angle <= a1:
            return c0 + (c1 - c0) * (angle - a0) / (a1 - a0)
    return 0

def envoyer_angles_compenses(epaule, coude, table):
    envoyer_angle(servo_epaule, epaule + correction(table["epaule"], epaule))
    envoyer_angle(servo_coude, coude + correction(table["coude"], coude))

if __name__ == "__main__":
    # Comparaison : le même carré sans puis avec étalonnage
    table = calibration_configuration("calibration_donnees_X.txt")
    coins = [(60, 90), (140, 90), (140, 170), (60, 170), (60, 90)]
    for t in ({"epaule": [], "coude": []}, table):     # table vide = sans étalonnage
        stylo(False)
        e, c = cinematique_inverse(*coins[0])
        envoyer_angles_compenses(e, c, t)
        time.sleep(1)
        stylo(True)
        for (xa, ya), (xb, yb) in zip(coins, coins[1:]):
            for k in range(1, 17):                     # petits pas = lignes droites
                x, y = xa + (xb - xa) * k / 16, ya + (yb - ya) * k / 16
                e, c = cinematique_inverse(x, y)
                envoyer_angles_compenses(e, c, t)
                time.sleep(0.05)
        stylo(False)

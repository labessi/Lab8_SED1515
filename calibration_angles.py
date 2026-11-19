# calibration_angles.py
# Envoie 0, 10, ..., 180° à un servo à la fois, marque un point sur le papier,
# puis demande l'angle réel mesuré au rapporteur.
# Chaque mesure est ajoutée tout de suite au fichier.

import time
from setup import servo_epaule, servo_coude, envoyer_angle, stylo

FICHIER = "calibration_donnees_X.txt"
ANGLE_FIXE = 90     # position de l'autre servo pendant la mesure

# En cas de blocage ou de bourdonnement : Ctrl+C (les servos sont coupés)

def calibrer(nom, servo, autre, debut=0):
    envoyer_angle(autre, ANGLE_FIXE)
    for desire in range(debut, 181, 10):
        envoyer_angle(servo, desire)
        time.sleep(1)
        stylo(True)          # marque le point
        stylo(False)
        rep = input("{} {} deg -> angle mesure (Entree = sauter, q = arreter) : ".format(nom, desire))
        if rep == "q":
            return
        if rep:
            with open(FICHIER, "a") as f:          # "a" = ajoute à la fin du fichier
                f.write("{} {} {}\n".format(nom, desire, float(rep)))

try:
    stylo(False)
    calibrer("epaule", servo_epaule, servo_coude, 50)
    calibrer("coude", servo_coude, servo_epaule)
finally:
    stylo(False)
    for s in (servo_epaule, servo_coude):
        s.duty_u16(0)          # coupe le signal : le servo arrête de forcer
    print("Termine. Voir", FICHIER)

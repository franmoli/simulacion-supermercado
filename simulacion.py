import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

t = 0
tpll = 0
tpsa = sys.maxsize
tpsb = sys.maxsize
ns = 0
itoa = 0
itob = 0
stoa = 0
stob = 0
sps = 0
nt = 0
sta = 0
sttb = 0

CANT_PERSONAS_ESPERANDO_MAX = 3
MINUTOS_POR_ITEM = 0.15
TIEMPO_FINAL_SIMULACION = 1051200 #2 años

def ejecutar_simulacion():
    global t
    global tpll
    global tpsa
    global tpsb
    global ns

    t = 0
    tpll = 0
    tpsa = sys.maxsize
    tpsb = sys.maxsize
    ns = 0

    while t < TIEMPO_FINAL_SIMULACION:
        # poner 2 cajas intermitentes, o n fijas
        if(tpll <= tpsa and tpll <= tpsb):
            llegada()
            continue

        if(tpsa <= tpsb):
            salida_por_a()
            continue
        else:
            salida_por_b()
            continue
        
    calcular_resultados()

def calcular_resultados():
    ptoa = stoa * 100 / t
    ptob = stob * 100 / t
    pps = sps / nt
    pec = (sps - sta) / nt
    ptb = sttb * 100 / t
    print(f"""Calculo de resultados: 
                ptob : {round(ptob,2)}% 
                ptoa: {round(ptoa, 2)}%
                gente total: {nt} 
                tiempo trabajado por b: {round(ptb,2)}%
                permanencia en sistema {round(pps,2)} min 
                espera en cola {round(pec,2)} min""")


def salida_por_a():
    # print("Salida por a")
    # La caja a es fija
    global tpsa
    global ns
    global t
    global itoa
    global sps

    sps += (tpsa - t) * ns
    t = tpsa
    ns -= 1

    if((ns == 1 and tpsb == sys.maxsize) or ns >= 2):
        # hay uno en el sistema y se acaba de ir el que tenia yo, lo atiendo
        atender_caja_a()
    else:
        # no hay nadie mas, o hay uno y lo atiende B
        itoa = t
        tpsa = sys.maxsize
        return



def atender_caja_a():
    # print("Lo atiendo en la caja a")
    global tpsa
    global t
    global sta

    # generar el ta
    ta = tiempo_de_atencion()
    tpsa = t + ta
    sta += ta

def salida_por_b():
    # print("Salida por b")
    global tpsb
    global ns
    global t
    global itob
    global sps
    global CANT_PERSONAS_ESPERANDO_MAX

    sps += (tpsb - t) * ns
    t = tpsb
    ns -= 1

    if(ns >=CANT_PERSONAS_ESPERANDO_MAX):
        atender_caja_b()
    else:
        itob = t
        tpsb = sys.maxsize




def atender_caja_b():
    global tpsb
    global t
    global sta
    global sttb
    
    # generar el ta
    ta = tiempo_de_atencion()
    tpsb = t + ta
    sta += ta
    sttb += ta

def llegada():
    # print("Llego alguien")
    global t
    global tpll
    global ns
    global stoa
    global stob
    global itoa
    global itob
    global sps
    global nt
    global CANT_PERSONAS_ESPERANDO_MAX

    sps += (tpll - t) * ns
    t = tpll
    ia = intervalo_entre_arribos()
    tpll = t + ia
    ns += 1
    nt += 1



    #si solo hay uno en la fila 
    if(ns == 1):
        stoa += t - itoa
        atender_caja_a()
        return
    
    # Si hay uno atendiendose en caja b, el siguiente en llegar atiendo por caja a
    if(ns == 2 and tpsb != sys.maxsize):
        stoa += t - itoa
        atender_caja_a()


    # Si se llego al limite de personas para abrir la otra caja atiendo por ahi
    if(ns == CANT_PERSONAS_ESPERANDO_MAX):
        stob += t - itob
        atender_caja_b()

    return

def generar_cant_productos():
    rho = 0.35578005915822714
    loc = 1
    scale =  0.32396170822425063
    return round(stats.halfgennorm.rvs(rho, loc, scale))

def tiempo_de_atencion():
    global MINUTOS_POR_ITEM
    return generar_cant_productos() * MINUTOS_POR_ITEM


def intervalo_entre_arribos():
    a = 4.294437555278593
    b = 4.2570194575870195
    loc = 0.04050820232979768
    scale =  0.2833975319715394
    return stats.norminvgauss.rvs(a, b, loc, scale)


def main():
    ejecutar_simulacion()
        


if __name__ == "__main__":
    main()


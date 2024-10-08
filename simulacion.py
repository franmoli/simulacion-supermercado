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
rotacionCaja = False
atendidosA = 0
atendidosB = 0
maxItems = 200
minItems = 100
minTLlegada = 100
maxTLlegada = 0
MAX_ITEMS_POR_TICKET = 200
MIN_INTERVALO_ARRIBO = 0.1


cant_personas_apertura_b = 1
MINUTOS_POR_ITEM = 0.15
# TIEMPO_FINAL_SIMULACION = 1051200 #2 años
# TIEMPO_FINAL_SIMULACION = 525600 #1 año
TIEMPO_FINAL_SIMULACION = 262800 #1/2 año
# TIEMPO_FINAL_SIMULACION = 1000



def ejecutar_simulacion():
    global t
    global tpll
    global tpsa
    global tpsb
    global ns
    global itoa
    global itob
    global stoa
    global stob
    global sps
    global nt
    global sta
    global sttb
    global atendidosA
    global atendidosB

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
    atendidosA = 0
    atendidosB = 0

    while t < TIEMPO_FINAL_SIMULACION:
        a=0
        if(tpsa != sys.maxsize):
            a+=1
        if(tpsb != sys.maxsize):
            a+=1
        test = ns - a + atendidosA + atendidosB

        if(nt != test):
            print(f"HAY ALGO RARO nt:{nt} sum: {test} ns: {ns} a:{atendidosA}  b:{atendidosB}") 
       
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
                espera en cola {round(pec,2)} min
                atendidos {atendidosA} + {atendidosB} = {atendidosA + atendidosB}
                ns: {ns}
                max items: {maxItems}
                min items: {minItems}
                max intervalo: {maxTLlegada}
                min intervalo: {minTLlegada}
                """)


def salida_por_a():
    # La caja a es fija
    global tpsa
    global ns
    global t
    global itoa
    global sps
    # print("Salida a")

    sps += (tpsa - t) * ns
    t = tpsa
    ns -= 1

    # sale de a-- ns = 1 --> o esta libre o lo atiende b 
    # si hay 2 o mas --> hay uno en cola y lo atiendo

    if((ns == 1 and tpsb == sys.maxsize) or ns >= 2):
        # hay uno en el sistema y no lo atiende b, o hay uno en cola
        atender_caja_a()
    else:
        # no hay nadie mas, o hay uno y lo atiende B
        itoa = t
        tpsa = sys.maxsize
        return



def atender_caja_a():
    # print(f"Atiendo a {ns}")
    global tpsa
    global t
    global sta
    global atendidosA

    # generar el ta
    ta = tiempo_de_atencion()
    tpsa = t + ta
    sta += ta
    atendidosA += 1

def salida_por_b():
    global tpsb
    global ns
    global t
    global itob
    global sps
    global cant_personas_apertura_b
    # print("Salida b")

    sps += (tpsb - t) * ns
    t = tpsb
    ns -= 1

    # sale de b --> si ns = 1  lo esta atiendiendo a pq a nunca cierra --> si hay mas de 1 si o si esta libre

    if(ns >=cant_personas_apertura_b and ns >= 2):
        atender_caja_b()
    else:
        itob = t
        tpsb = sys.maxsize




def atender_caja_b():
    global tpsb
    global t
    global sta
    global sttb
    global atendidosB
    # print(f"Atiendo b {ns}")
    
    # generar el ta
    ta = tiempo_de_atencion()
    tpsb = t + ta
    sta += ta
    sttb += ta
    atendidosB += 1

def llegada():
    global t
    global tpll
    global ns
    global stoa
    global stob
    global itoa
    global itob
    global sps
    global nt
    global cant_personas_apertura_b
    global rotacionCaja
    # print("Llegada")

    sps += (tpll - t) * ns
    t = tpll
    ia = intervalo_entre_arribos()
    tpll = t + ia
    ns += 1
    nt += 1

    # Caso con 2 cajas fijas
    if(cant_personas_apertura_b == 1): 
        # si los dos estan libres al mismo tiempo le mando uno y uno
        if(tpsa == sys.maxsize and tpsb == sys.maxsize):
            if(rotacionCaja):
                stob += t - itob
                atender_caja_b()
            else:
                stoa += t - itoa
                atender_caja_a()
            rotacionCaja = not rotacionCaja
            return
            
            
        # sino al primeor que se libere le mando
        if(tpsb == sys.maxsize):
            stob += t - itob
            atender_caja_b()
        else:
            if(tpsa == sys.maxsize):
                stoa += t - itoa
                atender_caja_a()
        return

    #si solo hay uno en la fila 
    if(ns == 1):
        stoa += t - itoa
        atender_caja_a()
        return
    
    # Si hay uno atendiendose en caja b, el siguiente en llegar atiendo por caja a
    if(ns == 2 and tpsb != sys.maxsize):
        stoa += t - itoa
        atender_caja_a()
        return

    # Si se llego al limite de personas para abrir la otra caja atiendo por ahi
    if(ns == cant_personas_apertura_b and tpsb == sys.maxsize):
        stob += t - itob
        # print("Atiendo por llegada")
        atender_caja_b()
        return

    return

def generar_cant_productos():
    global maxItems
    global minItems
    rho = 0.35578005915822714
    loc = 1
    scale =  0.32396170822425063
    items = round(stats.halfgennorm.rvs(rho, loc, scale))

    if(items > MAX_ITEMS_POR_TICKET):
        return generar_cant_productos()

    if(items > maxItems):
        maxItems = items
    if(items < minItems):
        minItems = items
    return items

def tiempo_de_atencion():
    global MINUTOS_POR_ITEM
    return generar_cant_productos() * MINUTOS_POR_ITEM


def intervalo_entre_arribos():
    global minTLlegada
    global maxTLlegada
    a = 4.294437555278593
    b = 4.2570194575870195
    loc = 0.04050820232979768
    scale =  0.2833975319715394
    intervalo = stats.norminvgauss.rvs(a, b, loc, scale)

    if(intervalo < MIN_INTERVALO_ARRIBO):
        return intervalo_entre_arribos()

    if(intervalo > maxTLlegada):
        maxTLlegada = intervalo
    if(intervalo < minTLlegada):
        minTLlegada = intervalo

    return intervalo


def main():
    global cant_personas_apertura_b

    print("Iniciando simulacion...")
    for i in range(10):
        cant_personas_apertura_b = i + 1 
        print(f"Simulando apertura a partir de {i + 1} personas")
        ejecutar_simulacion()
    
    # cant_personas_apertura_b = 100
    # ejecutar_simulacion()

    
        


if __name__ == "__main__":
    main()


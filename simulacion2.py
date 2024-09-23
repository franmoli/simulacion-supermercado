import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

t = 0
tpll = 0
tps = []
tpsa = sys.maxsize
tpsb = sys.maxsize
ns = 0
ito = []
itoa = 0
itob = 0
sto = []
stoa = 0
stob = 0
sps = 0
nt = 0
sta = 0
sttb = 0
rotacionCaja = False
atendidos = []
atendidosA = 0
atendidosB = 0
maxItems = 200
minItems = 100
minTLlegada = 100
maxTLlegada = 0
MAX_ITEMS_POR_TICKET = 200
MIN_INTERVALO_ARRIBO = 0.1
ultimo_puesto = 0
cant_personas_apertura_b = 1
cant_de_cajas = 3
MINUTOS_POR_ITEM = 0.15
# TIEMPO_FINAL_SIMULACION = 1051200 #2 años
# TIEMPO_FINAL_SIMULACION = 525600 #1 año
TIEMPO_FINAL_SIMULACION = 262800 #1/2 año
# TIEMPO_FINAL_SIMULACION = 1000



def ejecutar_simulacion():
    condiciones_iniciales()

    while t < TIEMPO_FINAL_SIMULACION:
    
        caja = buscar_menos_tps()
       
        if(tpll <= tps[caja]):
            llegada()
            continue
        else:
            salida(caja)
        
    calcular_resultados()

def calcular_resultados():
    print("Calculo de resultados")
    for i in range(cant_de_cajas):
        pto = sto[i] * 100 / t
        print(f"                Pto{i}: {round(pto,2)}%")
    pps = sps / nt
    pec = (sps - sta) / nt
    # ptb = sttb * 100 / t
    print(f"""  gente total: {nt} 
                permanencia en sistema {round(pps,2)} min 
                espera en cola {round(pec,2)} min
                atendidos {sum(atendidos)}
                ns: {ns}
                max items: {maxItems}
                min items: {minItems}
                max intervalo: {maxTLlegada}
                min intervalo: {minTLlegada}
                """)

# Devuelve la caja con menor tps
def buscar_menos_tps():
    caja = 0
    for i in range(cant_de_cajas):
        if(tps[i] < tps[caja]):
            caja = i
    return caja

def condiciones_iniciales():
    global t
    global tpll
    global tps
    global ito
    global sto
    global ns
    global sps
    global nt
    global sta
    global sttb
    global atendidos
    global maxItems
    global minItems
    global maxTLlegada
    global minTLlegada
    global ultimo_puesto

    t = 0
    tpll = 0
    tps = []
    ns = 0
    ito = []
    sto = []
    sps = 0
    nt = 0
    sta = 0
    sttb = 0
    atendidos = []
    maxItems = 200
    minItems = 100
    minTLlegada = 100
    maxTLlegada = 0
    ultimo_puesto = 0

    for i in range(cant_de_cajas):
        tps.append(sys.maxsize)
        ito.append(0)
        sto.append(0)
        atendidos.append(0)


def salida(caja):
     # La caja a es fija
    global tps
    global ns
    global t
    global ito
    global sps
    # print("Salida a")

    sps += (tps[caja] - t) * ns
    t = tps[caja]
    ns -= 1

    # sale de a-- ns = 1 --> o esta libre o lo atiende b 
    # si hay 2 o mas --> hay uno en cola y lo atiendo

    if(ns >= cant_de_cajas):
        # hay uno en el sistema y no lo atiende b, o hay uno en cola
        atender(caja)
    else:
        # no hay nadie mas, o hay uno y lo atiende B
        ito[caja] = t
        tps[caja] = sys.maxsize
        return
    

def atender(caja):
     # print(f"Atiendo a {ns}")
    global tps
    global t
    global sta
    global atendidos

    # generar el ta
    ta = tiempo_de_atencion()
    tps[caja] = t + ta
    sta += ta
    atendidos[caja] += 1


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
    print(f"Atiendo b {ns}")
    
    # generar el ta
    ta = tiempo_de_atencion()
    tpsb = t + ta
    sta += ta
    sttb += ta
    atendidosB += 1

def buscar_puesto():
    global ultimo_puesto

    ultimo_puesto +=1
    if(ultimo_puesto >= cant_de_cajas):
        ultimo_puesto = 0
    if(tps[ultimo_puesto] != sys.maxsize):
        return buscar_puesto()
    return ultimo_puesto

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

    # considerando a todas las cajas como fijas
    if(ns <= cant_de_cajas):
        caja = buscar_puesto()
        sto[caja] += t - ito[caja]
        atender(caja)

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
    global cant_de_cajas

    print("Iniciando simulacion...")
    for i in range(3):
        cant_de_cajas = i + 1 
        print(f"Simulando con {i + 1} cajas")
        ejecutar_simulacion()
    
    # cant_personas_apertura_b = 100
    # ejecutar_simulacion()

    
        


if __name__ == "__main__":
    main()


import pandas as pd
from kwhmeter import append_prices
from .common import config_pvpc


def LuT(LuTable,fecha,periodo=None):
    #Funcion para interpolar datos de una tabla basandose en 
    #la fecha. Para coger los precios vigentes en cada momento
    res = min([i for i in LuTable.keys() if i < fecha.date()], key=lambda x: abs(x - fecha.date()))
    if periodo is None:
        result=LuTable[res]
    else:
        result=LuTable[res][periodo]
    return result

def calculos_pvpc(datos,consumos):
    consumos_con_precios=append_prices(consumos)
    consumos_con_precios['EDCGASPCB']=consumos_con_precios['EDCGASPCB'].fillna(0)
    coeff=pd.DataFrame.from_dict(config_pvpc,orient='index')
    coeff_ene=coeff.energia.apply(pd.DataFrame.from_dict,orient='index').to_dict()
    precios=consumos_con_precios.reset_index().apply(lambda row: LuT(coeff_ene,row['fecha'],row['periodo']),axis=1)
    precios.index=consumos_con_precios.index
    consumos_con_precios['PEAJES_E_PRICE']=precios['peajes']    
    consumos_con_precios['CARGOS_E_PRICE']=precios['cargos']    
    consumos_con_precios['PEAJES_E']=consumos_con_precios['PEAJES_E_PRICE']*consumos_con_precios['consumo']/1000
    consumos_con_precios['CARGOS_E']=consumos_con_precios['CARGOS_E_PRICE']*consumos_con_precios['consumo']/1000
    consumos_con_precios['PEAJES_Y_CARGOS_E']=consumos_con_precios['PEAJES_E']+consumos_con_precios['CARGOS_E']
    consumos_con_precios['ENERGIA_SIN_PEAJES_NI_CARGOS']=consumos_con_precios['PCB']-consumos_con_precios['PEAJES_Y_CARGOS_E']
    consumos_con_precios['ENERGIA_SIN_PEAJES_NI_CARGOS_NI_GAS']=consumos_con_precios['ENERGIA_SIN_PEAJES_NI_CARGOS']-consumos_con_precios['EDCGASPCB']
    coeff_pot=coeff.potencia.apply(pd.DataFrame.from_dict,orient='index').to_dict()
    precios_p1=consumos_con_precios.reset_index().apply(lambda row: LuT(coeff_pot,row['fecha'],'P1'),axis=1)/(365*24)
    precios_p2=consumos_con_precios.reset_index().apply(lambda row: LuT(coeff_pot,row['fecha'],'P2'),axis=1)/(365*24)
    precios_p1.index=consumos_con_precios.index
    precios_p2.index=consumos_con_precios.index
    potencias_contratadas=datos['potencias']
    consumos_con_precios['PEAJES_P1_P']=precios_p1['peajes']*potencias_contratadas['P1']
    consumos_con_precios['CARGOS_P1_P']=precios_p1['cargos']*potencias_contratadas['P1']
    consumos_con_precios['PEAJES_P2_P']=precios_p2['peajes']*potencias_contratadas['P2']
    consumos_con_precios['CARGOS_P2_P']=precios_p2['cargos']*potencias_contratadas['P2']
    consumos_con_precios['PEAJES_P']=consumos_con_precios['PEAJES_P1_P']+consumos_con_precios['PEAJES_P2_P']
    consumos_con_precios['CARGOS_P']=consumos_con_precios['CARGOS_P1_P']+consumos_con_precios['CARGOS_P2_P']
    consumos_con_precios['PEAJES_Y_CARGOS_P']=consumos_con_precios['PEAJES_P']+consumos_con_precios['CARGOS_P']
    coeff_marge_comercializadora=coeff.margen_comercializacion.to_dict()
    precios_comercializacion=consumos_con_precios.reset_index().apply(lambda row: LuT(coeff_marge_comercializadora,row['fecha']),axis=1)
    precios_comercializacion.index=consumos_con_precios.index
    consumos_con_precios['COMERCIALIZADORA_P']=precios_comercializacion*potencias_contratadas['P2']/(365*24)
    consumos_con_precios['TERMINO_FIJO']=consumos_con_precios['PEAJES_Y_CARGOS_P']+consumos_con_precios['COMERCIALIZADORA_P']
    consumos_con_precios['TERMINO_VARIABLE']=consumos_con_precios['PEAJES_Y_CARGOS_E']+consumos_con_precios['ENERGIA_SIN_PEAJES_NI_CARGOS']
    consumos_con_precios['TOTAL_ELECTRICIDAD']=consumos_con_precios['TERMINO_VARIABLE']+consumos_con_precios['TERMINO_FIJO']
    coeff_impuesto_electrico=coeff.impuesto_electrico.to_dict()
    precios_impuesto_electrico=consumos_con_precios.reset_index().apply(lambda row: LuT(coeff_impuesto_electrico,row['fecha']),axis=1)
    precios_impuesto_electrico.index=consumos_con_precios.index
    consumos_con_precios['IMPUESTO_ELECTRICO']=consumos_con_precios['TOTAL_ELECTRICIDAD']*precios_impuesto_electrico/100
    coeff_contador=coeff.contador.to_dict()
    precios_contador=consumos_con_precios.reset_index().apply(lambda row: LuT(coeff_contador,row['fecha']),axis=1)
    precios_contador.index=consumos_con_precios.index
    consumos_con_precios['ALQUILER_CONTADOR']=precios_contador*12/(365*24)
    consumos_con_precios['IMPORTE_TOTAL']=consumos_con_precios['TOTAL_ELECTRICIDAD']+consumos_con_precios['IMPUESTO_ELECTRICO']+consumos_con_precios['ALQUILER_CONTADOR']
    coeff_iva=coeff.iva.to_dict()
    precios_iva=consumos_con_precios.reset_index().apply(lambda row: LuT(coeff_iva,row['fecha']),axis=1)
    precios_iva.index=consumos_con_precios.index
    consumos_con_precios['IVA']=consumos_con_precios['IMPORTE_TOTAL']*precios_iva/100
    consumos_con_precios['TOTAL_CON_IVA']=consumos_con_precios['IMPORTE_TOTAL']+consumos_con_precios['IVA']
    return consumos_con_precios


def formater(datos,consumos,anonimo=True):
    cc_por_periodo=consumos.groupby('periodo').sum(numeric_only=True)
    ndias=int(consumos.shape[0]/24)
    potencias_contratadas=datos['potencias']
    kWP1=potencias_contratadas['P1']
    kWP2=potencias_contratadas['P2']
    result={
    'Termino Fijos':{
        'Subtotal':f"{cc_por_periodo['consumo'].sum()/1000:.0f} kWh x {cc_por_periodo['TERMINO_FIJO'].sum()*1000/cc_por_periodo['consumo'].sum():.5f} €/kWh (ponderado)= {cc_por_periodo['TERMINO_FIJO'].sum():.2f} €",        
        'Peajes':{
            'P1': f"{ndias} dias x {cc_por_periodo['PEAJES_P1_P'].sum()/(ndias*kWP1):.6f} €/kW dia x {kWP1} kWP1 ={cc_por_periodo['PEAJES_P1_P'].sum():.2f} €",
            'P2': f"{ndias} dias x {cc_por_periodo['PEAJES_P2_P'].sum()/(ndias*kWP2):.6f} €/kW dia x {kWP2} kWP2 ={cc_por_periodo['PEAJES_P2_P'].sum():.2f} €",
        },
        'Cargos':{
            'P1': f"{ndias} dias x {cc_por_periodo['CARGOS_P1_P'].sum()/(ndias*kWP1):.6f} €/kW dia x {kWP1} kWP1 ={cc_por_periodo['CARGOS_P1_P'].sum():.2f} €",
            'P2': f"{ndias} dias x {cc_por_periodo['CARGOS_P2_P'].sum()/(ndias*kWP2):.6f} €/kW dia x {kWP2} kWP2 ={cc_por_periodo['CARGOS_P2_P'].sum():.2f} €",
        },
        f"Margen de comercialización {ndias} dias x {cc_por_periodo['COMERCIALIZADORA_P'].sum()/(ndias*kWP1):.6f} €/kW dia x {kWP1} kWP1":f"{cc_por_periodo['COMERCIALIZADORA_P'].sum():.2f} €"
    },
    'Termino Variables':{
        'Subtotal':f"{cc_por_periodo['consumo'].sum()/1000:.3f} kWh x {cc_por_periodo['TERMINO_VARIABLE'].sum()*1000/cc_por_periodo['consumo'].sum():.5f} €/kWh (ponderado)= {cc_por_periodo['TERMINO_VARIABLE'].sum():.2f} €",    
        'Peajes':{
            'Subtotal':f"{cc_por_periodo['consumo'].sum()/1000:.0f} kWh x {cc_por_periodo['PEAJES_E'].sum()*1000/cc_por_periodo['consumo'].sum():.5f} €/kWh (ponderado)= {cc_por_periodo['PEAJES_E'].sum():.2f} €",    
            'P1':f"{cc_por_periodo.loc['P1','consumo']/1000:.0f} kWh x {cc_por_periodo.loc['P1','PEAJES_E'].sum()*1000/cc_por_periodo.loc['P1','consumo'].sum():.6f} €/kWh = {cc_por_periodo.loc['P1','PEAJES_E']:.2f} €",
            'P2':f"{cc_por_periodo.loc['P2','consumo']/1000:.0f} kWh x {cc_por_periodo.loc['P2','PEAJES_E'].sum()*1000/cc_por_periodo.loc['P2','consumo'].sum():.6f} €/kWh = {cc_por_periodo.loc['P2','PEAJES_E']:.2f} €",
            'P3':f"{cc_por_periodo.loc['P3','consumo']/1000:.0f} kWh x {cc_por_periodo.loc['P3','PEAJES_E'].sum()*1000/cc_por_periodo.loc['P3','consumo'].sum():.6f} €/kWh = {cc_por_periodo.loc['P3','PEAJES_E']:.2f} €",
        },
        'Cargos':{
            'Subtotal':f"{cc_por_periodo['consumo'].sum()/1000:.0f} kWh x {cc_por_periodo['CARGOS_E'].sum()*1000/cc_por_periodo['consumo'].sum():.5f} €/kWh (ponderado) = {cc_por_periodo['CARGOS_E'].sum():.2f} €",
            'P1':f"{cc_por_periodo.loc['P1','consumo']/1000:.0f} kWh x {cc_por_periodo.loc['P1','CARGOS_E'].sum()*1000/cc_por_periodo.loc['P1','consumo'].sum():.6f} €/kWh = {cc_por_periodo.loc['P1','CARGOS_E']:.2f} €",
            'P2':f"{cc_por_periodo.loc['P2','consumo']/1000:.0f} kWh x {cc_por_periodo.loc['P2','CARGOS_E'].sum()*1000/cc_por_periodo.loc['P2','consumo'].sum():.6f} €/kWh = {cc_por_periodo.loc['P2','CARGOS_E']:.2f} €",
            'P3':f"{cc_por_periodo.loc['P3','consumo']/1000:.0f} kWh x {cc_por_periodo.loc['P3','CARGOS_E'].sum()*1000/cc_por_periodo.loc['P3','consumo'].sum():.6f} €/kWh = {cc_por_periodo.loc['P3','CARGOS_E']:.2f} €",
        },
        'Energia': {
            'Subtotal':f"{cc_por_periodo['consumo'].sum()/1000:.0f} kWh x {cc_por_periodo['ENERGIA_SIN_PEAJES_NI_CARGOS'].sum()*1000/cc_por_periodo['consumo'].sum():.5f} €/kWh (ponderado)= {cc_por_periodo['ENERGIA_SIN_PEAJES_NI_CARGOS'].sum():.2f} €",
            'Coste mercados':{
                'Subtotal':f"{cc_por_periodo['consumo'].sum()/1000:.0f} kWh x {cc_por_periodo['ENERGIA_SIN_PEAJES_NI_CARGOS_NI_GAS'].sum()*1000/cc_por_periodo['consumo'].sum():.5f} €/kWh (ponderado)= {cc_por_periodo['ENERGIA_SIN_PEAJES_NI_CARGOS_NI_GAS'].sum():.2f} €",
                'P1':f"{cc_por_periodo.loc['P1','consumo'].sum()/1000:.0f} kWh x {cc_por_periodo.loc['P1','ENERGIA_SIN_PEAJES_NI_CARGOS_NI_GAS'].sum()*1000/cc_por_periodo.loc['P1','consumo'].sum():.5f} €/kWh (ponderado)= {cc_por_periodo.loc['P1','ENERGIA_SIN_PEAJES_NI_CARGOS_NI_GAS'].sum():.2f} €",
                'P2':f"{cc_por_periodo.loc['P2','consumo'].sum()/1000:.0f} kWh x {cc_por_periodo.loc['P1','ENERGIA_SIN_PEAJES_NI_CARGOS_NI_GAS'].sum()*1000/cc_por_periodo.loc['P2','consumo'].sum():.5f} €/kWh (ponderado)= {cc_por_periodo.loc['P2','ENERGIA_SIN_PEAJES_NI_CARGOS_NI_GAS'].sum():.2f} €",
                'P3':f"{cc_por_periodo.loc['P3','consumo'].sum()/1000:.0f} kWh x {cc_por_periodo.loc['P1','ENERGIA_SIN_PEAJES_NI_CARGOS_NI_GAS'].sum()*1000/cc_por_periodo.loc['P3','consumo'].sum():.5f} €/kWh (ponderado)= {cc_por_periodo.loc['P3','ENERGIA_SIN_PEAJES_NI_CARGOS_NI_GAS'].sum():.2f} €",
                },
            'Compensación tope Gas': {
                'Subtotal':f"{cc_por_periodo['consumo'].sum()/1000:.0f} kWh x {cc_por_periodo['EDCGASPCB'].sum()*1000/cc_por_periodo['consumo'].sum():.5f} €/kWh (ponderado)= {cc_por_periodo['EDCGASPCB'].sum():.2f} €",
                'P1':f"{cc_por_periodo.loc['P1','consumo'].sum()/1000:.0f} kWh x {cc_por_periodo.loc['P1','EDCGASPCB'].sum()*1000/cc_por_periodo.loc['P1','consumo'].sum():.5f} €/kWh (ponderado)= {cc_por_periodo.loc['P1','EDCGASPCB'].sum():.2f} €",
                'P2':f"{cc_por_periodo.loc['P2','consumo'].sum()/1000:.0f} kWh x {cc_por_periodo.loc['P1','EDCGASPCB'].sum()*1000/cc_por_periodo.loc['P2','consumo'].sum():.5f} €/kWh (ponderado)= {cc_por_periodo.loc['P2','EDCGASPCB'].sum():.2f} €",
                'P3':f"{cc_por_periodo.loc['P3','consumo'].sum()/1000:.0f} kWh x {cc_por_periodo.loc['P1','EDCGASPCB'].sum()*1000/cc_por_periodo.loc['P3','consumo'].sum():.5f} €/kWh (ponderado)= {cc_por_periodo.loc['P3','EDCGASPCB'].sum():.2f} €",
                }
        }
    },
    'Impuesto Electrico':f"{cc_por_periodo['IMPUESTO_ELECTRICO'].sum()*100/cc_por_periodo['TOTAL_ELECTRICIDAD'].sum():.2f}% x {cc_por_periodo['TOTAL_ELECTRICIDAD'].sum():.2f} € = {cc_por_periodo['IMPUESTO_ELECTRICO'].sum():.2f} €",
    'Otros':{
            'Alquiler Contador':f"{ndias} dias x {cc_por_periodo['ALQUILER_CONTADOR'].sum()/ndias:.6f} €/dia = {cc_por_periodo['ALQUILER_CONTADOR'].sum():.2f} €"
            },
    'Base imponible':f"{cc_por_periodo['IMPORTE_TOTAL'].sum():.2f} €",
    'I.V.A.':f"{cc_por_periodo['IVA'].sum()*100/cc_por_periodo['IMPORTE_TOTAL'].sum():.1f}% x {cc_por_periodo['IMPORTE_TOTAL'].sum():.2f} € = {cc_por_periodo['IVA'].sum():.2f} €",
    'TOTAL IMPORTE FACTURA':f"{cc_por_periodo['TOTAL_CON_IVA'].sum():.2f} €",
    }
    if anonimo:
        suministro={'CUPS':'ES34XXXXXXXXXXXXXXXXX','TITULAR':'FULANO DE TAL','DIRECCION':'PASEILLO DE LA PALANQUETA, 3 ROZAS DEL BIERZO MURZIA'}
    else:
        suministro={'CUPS':datos['cups'],'TITULAR':datos['titular'],'DIRECCION':datos['direccion']}
    result={'suministro':suministro,
            'potencias_contratadas':datos['potencias'],
            'periodo':{'desde':consumos.index.min(),'hasta':consumos.index.max()},
            'factura':result} 
    return result     


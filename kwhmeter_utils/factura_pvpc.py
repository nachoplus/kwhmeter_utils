import pandas as pd
from kwhmeter import contador, timezone, append_prices, read_config
from datetime import datetime, timedelta
from .common import data_dir, config
import logging



class suministro:
    def __init__(self,suministro) -> None:
        credenciales=read_config()
        if not suministro in credenciales:
            print(f"Error: No exite el suministro:{suministro} en el archivo de configuración")
            exit(1)
        self.suministro=suministro
        params={ k:v for k,v in credenciales[suministro].items() if k in ['distribuidora','user','password']}
        self.connection = contador(**params)  

    def periodos_facturacion(self):
        return self.connection.lista_facturas

    def calculos_pvpc(self,consumos):
        consumos_con_precios=append_prices(consumos)
        precios_e=pd.DataFrame(config['precios']['energia']).reset_index()
        precios_e.rename({'index':'periodo','peajes':'PEAJES_E_PRICE','cargos':'CARGOS_E_PRICE'},axis=1,inplace=True)
        consumos_con_precios=consumos_con_precios.reset_index().merge(precios_e,left_on='periodo',right_on='periodo').set_index('fecha').sort_index()
        consumos_con_precios['PEAJES_E']=consumos_con_precios['PEAJES_E_PRICE']*consumos_con_precios['consumo']/1000
        consumos_con_precios['CARGOS_E']=consumos_con_precios['CARGOS_E_PRICE']*consumos_con_precios['consumo']/1000
        consumos_con_precios['PEAJES_Y_CARGOS_E']=consumos_con_precios['PEAJES_E']+consumos_con_precios['CARGOS_E']
        consumos_con_precios['ENERGIA_SIN_PEAJES_NI_CARGOS']=consumos_con_precios['PCB']-consumos_con_precios['PEAJES_Y_CARGOS_E']
        consumos_con_precios['ENERGIA_SIN_PEAJES_NI_CARGOS_NI_GAS']=consumos_con_precios['ENERGIA_SIN_PEAJES_NI_CARGOS']-consumos_con_precios['EDCGASPCB']
        precios_p=pd.DataFrame(config['precios']['potencia'])
        potencias_contratadas=self.connection.potencias
        precios_p.loc['P1']=precios_p.loc['P1']*potencias_contratadas['P1']
        precios_p.loc['P2']=precios_p.loc['P2']*potencias_contratadas['P2']
        consumos_con_precios['PEAJES_P1_P']=precios_p.loc['P1']['peajes']/24
        consumos_con_precios['CARGOS_P1_P']=precios_p.loc['P1']['cargos']/24
        consumos_con_precios['PEAJES_P2_P']=precios_p.loc['P2']['peajes']/24
        consumos_con_precios['CARGOS_P2_P']=precios_p.loc['P2']['cargos']/24
        consumos_con_precios['PEAJES_P']=precios_p.sum()['peajes']/24
        consumos_con_precios['CARGOS_P']=precios_p.sum()['cargos']/24
        consumos_con_precios['PEAJES_Y_CARGOS_P']=consumos_con_precios['PEAJES_P']+consumos_con_precios['CARGOS_P']
        consumos_con_precios['COMERCIALIZADORA_P']=config['precios']['margen_comercializacion']*potencias_contratadas['P2']/24
        consumos_con_precios['TERMINO_FIJO']=consumos_con_precios['PEAJES_Y_CARGOS_P']+consumos_con_precios['COMERCIALIZADORA_P']
        consumos_con_precios['TERMINO_VARIABLE']=consumos_con_precios['PEAJES_Y_CARGOS_E']+consumos_con_precios['ENERGIA_SIN_PEAJES_NI_CARGOS']
        consumos_con_precios['TOTAL_ELECTRICIDAD']=consumos_con_precios['TERMINO_VARIABLE']+consumos_con_precios['TERMINO_FIJO']
        consumos_con_precios['IMPUESTO_ELECTRICO']=consumos_con_precios['TOTAL_ELECTRICIDAD']*config['precios']['impuesto_electrico']/100
        consumos_con_precios['ALQUILER_CONTADOR']=config['precios']['contador']/24
        consumos_con_precios['IMPORTE_TOTAL']=consumos_con_precios['TOTAL_ELECTRICIDAD']+consumos_con_precios['IMPUESTO_ELECTRICO']+consumos_con_precios['ALQUILER_CONTADOR']
        consumos_con_precios['IVA']=consumos_con_precios['IMPORTE_TOTAL']*config['precios']['iva']/100
        consumos_con_precios['TOTAL_CON_IVA']=consumos_con_precios['IMPORTE_TOTAL']+consumos_con_precios['IVA']
        return consumos_con_precios


    def formater(self,datos,anonimo=True):
        cc_por_periodo=datos.groupby('periodo').sum()
        precios_e=pd.DataFrame(config['precios']['energia'])
        precios_p=pd.DataFrame(config['precios']['potencia'])
        margen_comercializacion=float(config['precios']['margen_comercializacion'])
        ndias=int(datos.shape[0]/24)
        potencias_contratadas=self.connection.potencias
        kWP1=potencias_contratadas['P1']
        kWP2=potencias_contratadas['P2']
        result={
        'Termino Fijos':{
            'Subtotal':f"{cc_por_periodo['consumo'].sum()/1000:.0f} kWh x {cc_por_periodo['TERMINO_FIJO'].sum()*1000/cc_por_periodo['consumo'].sum():.5f} €/kWh (ponderado)= {cc_por_periodo['TERMINO_FIJO'].sum():.2f} €",        
            'Peajes':{
                'P1': f"{ndias} dias x {precios_p.loc['P1','peajes']:.5f} €/kW dia x {kWP1} kWP1 ={ndias*precios_p.loc['P1','peajes']*kWP1:.2f} €",
                'P2': f"{ndias} dias x {precios_p.loc['P2','peajes']:.5f} €/kW dia x {kWP2} kWP2 ={ndias*precios_p.loc['P2','peajes']*kWP2:.2f} €",
            },
            'Cargos':{
                'P1': f"{ndias} dias x {precios_p.loc['P1','cargos']:.5f} €/kW dia x {kWP1} kWP1 ={ndias*precios_p.loc['P1','cargos']*kWP1:.2f} €",
                'P2': f"{ndias} dias x {precios_p.loc['P2','cargos']:.5f} €/kW dia x {kWP2} kWP2 ={ndias*precios_p.loc['P2','cargos']*kWP2:.2f} €",
            },
            f'Margen de comercialización {ndias} dias x {margen_comercializacion:.5f} €/kW dia x {kWP1} kWP1':ndias*margen_comercializacion*kWP1
        },
        'Termino Variables':{
            'Subtotal':f"{cc_por_periodo['consumo'].sum()/1000:.0f} kWh x {cc_por_periodo['TERMINO_VARIABLE'].sum()*1000/cc_por_periodo['consumo'].sum():.5f} €/kWh (ponderado)= {cc_por_periodo['TERMINO_VARIABLE'].sum():.2f} €",    
            'Peajes':{
                'Subtotal':f"{cc_por_periodo['consumo'].sum()/1000:.0f} kWh x {cc_por_periodo['PEAJES_E'].sum()*1000/cc_por_periodo['consumo'].sum():.5f} €/kWh (ponderado)= {cc_por_periodo['PEAJES_E'].sum():.2f} €",    
                'P1':f"{cc_por_periodo.loc['P1','consumo']/1000:.0f} kWh x {precios_e.loc['P1','peajes']} €/kWh = {cc_por_periodo.loc['P1','PEAJES_E']:.2f} €",
                'P2':f"{cc_por_periodo.loc['P2','consumo']/1000:.0f} kWh x {precios_e.loc['P2','peajes']} €/kWh = {cc_por_periodo.loc['P2','PEAJES_E']:.2f} €",
                'P3':f"{cc_por_periodo.loc['P3','consumo']/1000:.0f} kWh x {precios_e.loc['P3','peajes']} €/kWh = {cc_por_periodo.loc['P3','PEAJES_E']:.2f} €",
            },
            'Cargos':{
                'Subtotal':f"{cc_por_periodo['consumo'].sum()/1000:.0f} kWh x {cc_por_periodo['CARGOS_E'].sum()*1000/cc_por_periodo['consumo'].sum():.5f} €/kWh (ponderado) = {cc_por_periodo['CARGOS_E'].sum():.2f} €",
                'P1':f"{cc_por_periodo.loc['P1','consumo']/1000:.0f} kWh x {precios_e.loc['P1','cargos']} €/kWh = {cc_por_periodo.loc['P1','CARGOS_E']:.2f} €",
                'P2':f"{cc_por_periodo.loc['P2','consumo']/1000:.0f} kWh x {precios_e.loc['P2','cargos']} €/kWh = {cc_por_periodo.loc['P2','CARGOS_E']:.2f} €",
                'P3':f"{cc_por_periodo.loc['P3','consumo']/1000:.0f} kWh x {precios_e.loc['P3','cargos']} €/kWh = {cc_por_periodo.loc['P3','CARGOS_E']:.2f} €",
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
        'Impuesto Electrico':f"{config['precios']['impuesto_electrico']}% x {cc_por_periodo['TOTAL_ELECTRICIDAD'].sum():.2f} € = {cc_por_periodo['IMPUESTO_ELECTRICO'].sum():.2f} €",
        'Otros':{
                'Alquiler Contador':f"{ndias} dias x {config['precios']['contador']} €/dia = {cc_por_periodo['ALQUILER_CONTADOR'].sum():.2f} €"
                },
        'Base imponible':f"{cc_por_periodo['IMPORTE_TOTAL'].sum():.2f}",
        'I.V.A.':f"{cc_por_periodo['IVA'].sum():.2f}",
        'TOTAL IMPORTE FACTURA':f"{cc_por_periodo['TOTAL_CON_IVA'].sum():.2f}",
        }
        if anonimo:
            suministro={'CUPS':'ES34XXXXXXXXXXXXXXXXX','TITULAR':'FULANO DE TAL','DIRECCION':'PASEILLO DE LA PALANQUETA, 3 ROZAS DEL BIERZO MURZIA'}
        else:
            suministro={'CUPS':self.connection.cups,'TITULAR':self.connection.titular,'DIRECCION':self.connection.direccion}
        result={'suministro':suministro,
                'potencias_contratadas':self.connection.potencias,
                'periodo':{'desde':datos.index.min().date(),'hasta':datos.index.max().date()},
                'factura':result} 
        return result     

    def factura_pvpc(self,consumos):
        datos=self.calculos_pvpc(consumos)
        return datos

    def consumo(self,start,end):
        return self.connection.consumo(start,end)

    def consumo_facturado(self,lista_periodos):
        return self.connection.consumo_facturado(lista_periodos)        
import click
import json
import datetime
from pathlib import Path
import kwhmeter_utils as ku
from kwhmeter.common import flex_consumos
from pandas.api.types import is_datetime64_any_dtype as is_datetime

class DateTimeEncoder(json.JSONEncoder):
        #Override the default method
        def default(self, obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_nivel(res,level=0):
    #print(level,res)
    if isinstance(res,dict):
        if not 'Subtotal' in res:
            first=True
        else:
            first=False
        tabs=['\t' for i in range(level)]            
        for k,v in res.items():
            if level==0:
                color=bcolors.HEADER
                end='\n'
            elif level==1:
                color=bcolors.OKBLUE
            elif level==2:
                color=bcolors.OKGREEN
            elif level==3:
                color=bcolors.OKCYAN
            else:
                color=bcolors.WARNING
            if k!="Subtotal":
                if first:
                    first=False
                    print()
                print(f'{color}{"".join(tabs)}{k}:{bcolors.ENDC}',end=' ')                        
            print_nivel(v,level+1)            
    else:
        tabs=['  ' for i in range(level)]
        print(f'{res}')              
            
    return

#datos
@click.command()
@click.argument('suministro',type=str)
@click.option('--lista-facturas',is_flag=True, show_default=True, default=False, help="Muestra los periodos de facturación disponibles")
@click.option('--n','n',multiple=True,type=click.INT,help="Consumos para las facturas especificadas por indice. Se puede usar tantas veces como facturas se quieran recuperar",show_default=True,default=False)
@click.option('--m',multiple=False,type=click.INT,help="Consumos para las ultimas m facturas",show_default=True,default=False)
@click.option('--d',multiple=False,type=click.INT,help="Consumos para los ultimos d dias",show_default=True,default=False)
@click.option('--factura','factura',multiple=True,help="Consumos para las facturas especificadas. Se puede usar tantas veces como facturas se quieran recuperar",show_default=True,default=False)
@click.option('--fecha-ini', 'fecha_ini',type=click.DateTime(formats=["%Y-%m-%d"]),
              help="Fecha inicio consumos por fecha",show_default=True)
@click.option('--fecha-fin', 'fecha_fin',type=click.DateTime(formats=["%Y-%m-%d"]),
              help="Fecha fin consumos por fecha",show_default=True)
@click.option('--format',help="Formato de salida",
              type=click.Choice(['screen','json', 'pdf','html'], case_sensitive=False),default='screen',show_default=True)
def pvpc(suministro,lista_facturas,n,m,d,factura,fecha_ini,fecha_fin,format):
    datos,consumo=flex_consumos(suministro,n,m,d,factura,fecha_ini,fecha_fin)
    if not datos:
        return
    cc=ku.calculos_pvpc(datos,consumo)
    result=ku.formater(datos,cc)
    if format=='screen':
        print_nivel(result)
    if format=='json':
        print(json.dumps(result, default=str))
    elif format=='html':
        print("TODO: No implementado. ")
        pass

#datos
@click.command()
@click.argument('suministro',type=str)
@click.option('--lista-facturas',is_flag=True, show_default=True, default=False, help="Muestra los periodos de facturación disponibles")
@click.option('--n','n',multiple=True,type=click.INT,help="Consumos para las facturas especificadas por indice. Se puede usar tantas veces como facturas se quieran recuperar",show_default=True,default=False)
@click.option('--m',multiple=False,type=click.INT,help="Consumos para las ultimas m facturas",show_default=True,default=False)
@click.option('--d',multiple=False,type=click.INT,help="Consumos para los ultimos d dias",show_default=True,default=False)
@click.option('--factura','factura',multiple=True,help="Consumos para las facturas especificadas. Se puede usar tantas veces como facturas se quieran recuperar",show_default=True,default=False)
@click.option('--fecha-ini', 'fecha_ini',type=click.DateTime(formats=["%Y-%m-%d"]),
              help="Fecha inicio consumos por fecha",show_default=True)
@click.option('--fecha-fin', 'fecha_fin',type=click.DateTime(formats=["%Y-%m-%d"]),
              help="Fecha fin consumos por fecha",show_default=True)
@click.option('--format',help="Formato de salida",
              type=click.Choice(['screen','json', 'pdf','html'], case_sensitive=False),default='screen',show_default=True)
def influxDB(suministro,lista_facturas,n,m,d,factura,fecha_ini,fecha_fin,format):
    datos,consumo=flex_consumos(suministro,n,m,d,factura,fecha_ini,fecha_fin)
    if not datos:
        return
    ku.to_influxDB(datos,consumo)
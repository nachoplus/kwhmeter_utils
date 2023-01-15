import click
import json
import datetime
from pathlib import Path
import logging
import kwhmeter_utils as ku
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
        for k,v in res.items():
            tabs=['  ' for i in range(level)]
            end=' '
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
            print(f'{color}{"".join(tabs)}{k}:{bcolors.ENDC}',end=end)                        
            print_nivel(v,level+1)            
    else:
        tabs=['  ' for i in range(level)]
        print(f'{"".join(tabs)}{res}')              
            
    return

#datos
@click.command()
@click.argument('suministro',type=str)
@click.option('--lista-facturas',is_flag=True, show_default=True, default=False, help="Muestra los periodos de facturación disponibles")
@click.option('--n','n',help="Consumos para las facturas especificadas.",show_default=True,default=1)
@click.option('--factura','factura',multiple=True,help="Consumos para las facturas especificadas. Se puede usar tantas veces como facturas se quieran recuperar",show_default=True,default=False)
@click.option('--fecha-ini', 'fecha_ini',type=click.DateTime(formats=["%Y-%m-%d"]),
              default=str(datetime.date.today()-datetime.timedelta(days=30)),help="Fecha inicio consumos por fecha",show_default=True)
@click.option('--fecha-fin', 'fecha_fin',type=click.DateTime(formats=["%Y-%m-%d"]),
              default=str(datetime.date.today()),help="Fecha fin consumos por fecha",show_default=True)
@click.option('--format',help="Formato de salida",
              type=click.Choice(['screen','json', 'pdf','html'], case_sensitive=False),default='screen',show_default=True)
def pvpc(suministro,lista_facturas,n,factura,fecha_ini,fecha_fin,format):
    suministro=ku.suministro(suministro)   
    if lista_facturas:
        print("Peridos de facturacion disponibles:")
        df=suministro.periodos_facturacion()
        print(df)
        return
    elif n:
        f=suministro.periodos_facturacion()
        factura=f.index[n-1]
        print(f'FACTURA:{factura}')
        df=suministro.consumo_facturado([factura])
    elif factura:
        factura=list(factura)
        print(f"Consumos de la facturas:{factura}")
        df=suministro.consumo_facturado(factura)
    elif fecha_fin and fecha_ini:
        fecha_ini=ku.timezone.localize(fecha_ini)
        fecha_fin=ku.timezone.localize(fecha_fin)
        print(f"Consumos entre las fechas {fecha_ini} y {fecha_fin}")
        df=suministro.consumo(fecha_ini,fecha_fin)
    else:
        print("No se han especificado parametros")
        return
    cc=suministro.factura_pvpc(df)
    result=suministro.formater(cc)
    if format=='screen':
        print_nivel(result)
    if format=='json':
        print(json.dumps(result, default=str))
    elif format=='html':
        pass

    
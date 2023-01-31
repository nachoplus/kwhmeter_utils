# kwhmeter_utils

IMPORTANTE: Este software no etá vinculado con ninguna compañia electrica. Es un proyecto personal que se pone a disposición de todo el que quiera utilizarlo bajo su propia responsanbilidad.

Varias utilidades:

* Simula la factura PVPC partiendo de los datos de consumo descargados de las web de las correspondiente distribuidaoras usando el paquete kwhmeter

## Uso

ver el directorio jupyter con ejemplos de uso

Tambien se incluye un comando:

> kwhmeter_pvpc --help
> Usage: kwhmeter_pvpc [OPTIONS] SUMINISTRO> 

> Options:
>   --lista-facturas                Muestra los periodos de facturación
>                                   disponibles  [default: False]> 

>   --n INTEGER                     Consumos para las facturas especificadas por
>                                   indice. Se puede usar tantas veces como
>                                   facturas se quieran recuperar  [default:
>                                   False]> 

>   --m INTEGER                     Consumos para las ultimas m facturas
>                                   [default: False]> 

>   --factura TEXT                  Consumos para las facturas especificadas. Se
>                                   puede usar tantas veces como facturas se
>                                   quieran recuperar  [default: False]> 

>   --fecha-ini [%Y-%m-%d]          Fecha inicio consumos por fecha
>   --fecha-fin [%Y-%m-%d]          Fecha fin consumos por fecha
>   --format [screen|json|pdf|html]
>                                   Formato de salida  [default: screen]
>   --help                          Show this message and exit.

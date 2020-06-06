# tiendanube-bulk-importer
Tool for bulk importing / updating products in Nuvemshop / Tiendanube

Script que permite la actualización masiva de precios y stocks de productos en TiendaNube desde un archivo CSV.

## Motivación

El import CSV standard de TiendaNube tiene dos desventajas:
- Para actualizar un producto existente require obligatoriamente referenciar al 'ID de url' del mismo. 
- No se puede automatizar limpiamente ya que no hay un endpoint via API para realizar la carga. 

Este script soluciona estos problemas haciendo la carga via API, buscando los productos a actualizar por su SKU asociado. 

Tambien permite realizar un export de los productos de la tienda en JSON

## Uso
Es necesario crear una app de TiendaNube, y obtener un access token para el store sobre el que se van a actualizar los productos

https://tiendanube.docs.apiary.io/#reference/product/create-a-new-product
https://tiendanube.docs.apiary.io/#introduction/authentication/authorization-flow

Luego se utiliza via linea de comandos

```
$ python sku_importer.py -h

usage: sku_importer.py [-h] --storeid STOREID --token TOKEN [--file FILE]
                       [--delimiter DELIMITER] [--quotechar QUOTECHAR]
                       [--skipheader] [--sku SKU] [--price PRICE]
                       [--stock STOCK] [--name NAME]
                       [--decimalseparator DECIMALSEPARATOR]
                       [--thousandseparator THOUSANDSEPARATOR] [--create]
                       [--propercase] [--addsku] [--export]
                       [--exportfile EXPORTFILE] [--readexport]

optional arguments:
  -h, --help            show this help message and exit
  --storeid STOREID     The store_id to sync the product stocks to
  --token TOKEN         The authorization token
  --file FILE           Path to the CSV file to use for updating stocks and
                        prices. Defaults to 'products.csv'
  --delimiter DELIMITER
                        CSV field delimiter. Defaults to ,
  --quotechar QUOTECHAR
                        CSV field quote character. Defaults to "
  --skipheader          If the first row of the CSV is a header and should be
                        skipped
  --sku SKU             Column number that holds the SKU. 0 based. Defaults to
                        0
  --price PRICE         Column number that holds the price. 0 based. Defaults
                        to 1
  --stock STOCK         Column number that holds the stock. 0 based. Defaults
                        to 2
  --name NAME           Optional column number that holds the product name to
                        use to create a new name if the SKU is not found. 0
                        based. Defaults to 3
  --decimalseparator DECIMALSEPARATOR
                        Character used for decimal separator on the price
                        column. Defaults to '.'
  --thousandseparator THOUSANDSEPARATOR
                        Character for thousands separator on the price column.
                        Default none
  --create              Creates a new product if a SKU is not found. By
                        default it just warns about it
  --propercase          Changes casing on the name to Proper Case
  --addsku              Adds the SKU at the end of the product name
  --export              Exports all existing products to exportfile instead
  --exportfile EXPORTFILE
                        Path to the file to export to
  --readexport          Checks current prices and stocks against the
                        exportfile instead of calling the API
```

Ejemplo de llamada 

```
python sku_importer.py --storeid 123456 --token abcdefg --sku 1 --name 2 --price 3 --stock 4 --decimalseparator , --addsku --propercase --create
```

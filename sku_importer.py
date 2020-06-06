from collections import namedtuple
from decimal import Decimal

import argparse
import csv
import json
import urllib2


def api_request(path, verb='GET', data=None):
	url = "https://api.tiendanube.com/v1/" + args.storeid + path
	headers = {
		'Content-Type': 'application/json',
		'User-Agent': 'mass updater',
		'Authentication': 'bearer ' + args.token
	}
	req = urllib2.Request(url, data=json.dumps(data) if data else None, headers=headers)
	req.get_method = lambda: verb
	f = urllib2.urlopen(req)
	return json.load(f)

def load_all(path):
	page=1
	cont = True
	while cont:
		items = api_request(path + "?per_page=200&page=" + str(page))
		for item in items:
			yield item
		if len(items) < 200:
			cont = False
		page = page + 1	

def load_products():
	if (args.readexport):
		with open(args.exportfile) as exportfile:
			return json.load(exportfile)
	return load_all("/products")

def setup_name(name, sku):
	cased = name.title() if args.propercase else name
	return cased + " (" + sku + ")" if args.addsku else cased

parser = argparse.ArgumentParser()

# API parameters
parser.add_argument("--storeid", help="The store_id to sync the product stocks to", required=True)
parser.add_argument("--token", help="The authorization token", required=True)

# CSV parsing options
parser.add_argument("--file", help="Path to the CSV file to use for updating stocks and prices. Defaults to 'products.csv'", default='products.csv')
parser.add_argument("--delimiter", help="CSV field delimiter. Defaults to ,", default=",")
parser.add_argument("--quotechar", help="CSV field quote character. Defaults to \"", default="\"")
parser.add_argument("--skipheader", help="If the first row of the CSV is a header and should be skipped", action="store_true", default=True)
parser.add_argument("--sku", help="Column number that holds the SKU. 0 based. Defaults to 0", default=0, type=int)
parser.add_argument("--price", help="Column number that holds the price. 0 based. Defaults to 1", default=1, type=int)
parser.add_argument("--stock", help="Column number that holds the stock. 0 based. Defaults to 2", default=2, type=int)
parser.add_argument("--name", help="Optional column number that holds the product name to use to create a new name if the SKU is not found. 0 based. Defaults to 3", default=3, type=int)
parser.add_argument("--decimalseparator", help="Character used for decimal separator on the price column. Defaults to '.'", default=".")
parser.add_argument("--thousandseparator", help="Character for thousands separator on the price column. Default none", default="")

# New product creation options
parser.add_argument("--create", help="Creates a new product if a SKU is not found. By default it just warns about it", action="store_true")
parser.add_argument("--propercase", help="Changes casing on the name to Proper Case", action="store_true")
parser.add_argument("--addsku", help="Adds the SKU at the end of the product name", action="store_true")

# Exporting options
parser.add_argument("--export", help="Exports all existing products to exportfile instead", action="store_true")
parser.add_argument("--exportfile", help="Path to the file to export to", default="export.json")
parser.add_argument("--readexport", help="Checks current prices and stocks against the exportfile instead of calling the API", action="store_true")

args = parser.parse_args()

if (args.export):
	with open(args.exportfile, 'w') as outfile:
		json.dump([p for p in load_products()], outfile, indent=4)
	exit()

print "Parsing CSV..."

Product = namedtuple('Product', 'sku price stock name')

csv_products = []

with open(args.file) as csvfile:
	reader = csv.reader(csvfile, delimiter=args.delimiter, quotechar=args.quotechar)
	if args.skipheader:
		next(reader, None)

	csv_products = [
		Product(
			row[args.sku], 
			str(Decimal(row[args.price].replace(args.thousandseparator, '').replace(args.decimalseparator, '.'))), 
			int(row[args.stock]), 
			setup_name(row[args.name], row[args.sku]) if len(row) > args.name else None
		) for row in reader]


print "Loading store products..."

existing_products = load_products()

variant_by_sku = dict([(variant['sku'], variant)
	for product in existing_products
	for variant in product['variants']])

to_update = []
to_create = []

for product in csv_products:
	if product.sku in variant_by_sku:
		variant = variant_by_sku[product.sku]
		if variant['stock'] != product.stock or variant['price'] != product.price: 
			variant['price'] = product.price
			variant['stock'] = product.stock
			to_update.append(variant)
	else:
		to_create.append(product)


for variant in to_update:
	print "Updating " + variant['sku'] + " price: " + variant['price'] + " stock: " + str(variant['stock'])
	api_request("/products/" + str(variant['product_id']) + '/variants/' + str(variant['id']), verb="PUT", data=variant)

for product in to_create:
	print "New product " + product.sku + " - " + (product.name or "")
	if args.create:
		api_request("/products/", verb="POST", data={
			"name": product.name,
			"variants": [{
				"sku": product.sku,
				"stock": product.stock,
				"price": product.price
			}]
		})



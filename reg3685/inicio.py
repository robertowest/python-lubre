import argparse
import calendar
import fdb

from datetime import date
from afip.compras import Compra
from afip.ventas import Venta

parser = argparse.ArgumentParser()
parser.add_argument("-a", help="Año a procesar", type=int, default=date.today().year)
parser.add_argument("-m", help="Mes a procesar", type=int, default=date.today().month)
parser.add_argument("-ruta", help="Directorio de ecritura", type=str, default="~/")
parser.add_argument("--pantalla", help="Realiza la salida por pantalla", action="store_true")
args = parser.parse_args()

def dbconnect():
    global conn

    try:
        conn = fdb.connect(host="192.168.1.254",
                           database="P:\PROYECTO\datos\Gestion.fdb",
                           user="sysdba", password="masterkey", charset="ISO8859_1")
    except:
        conn = None

def iva_compras():
    global conn
    file1 = open(args.ruta + "/01-Compras.txt", "w")
    file2 = open(args.ruta + "/02-Compras-ALI.txt", "w")

    SQL = "SELECT idfacprovedor, fecha, comprob, terminal, numero, cuit, nombre, " \
          "neto, no_grab, iva21, iva10, iva27, p_ibb, p_iva, itc, total, c_ali " \
          "FROM citi_compras_v " \
          "WHERE anio = {} AND mes = {}".format(args.a, args.m)
          # "WHERE idfacprovedor = 145574"

    cursor = conn.cursor()
    for row in cursor.execute(SQL).itermap():
        compra = Compra(row["fecha"], row["comprob"], row["terminal"], row["numero"],
                        row["cuit"], row["nombre"],
                        row["neto"], row["no_grab"],
                        row["iva21"], row["iva10"], row["iva27"],
                        row["p_ibb"], row["p_iva"], row["itc"], row["total"],
                        row["c_ali"])

        try:
            # linea de factura
            if args.pantalla:
                print(compra)
            else:
                file1.write(str(compra).replace("|", "") + "\n")

            # información de alícuotas
            if compra.iva10():
                if args.pantalla:
                    print(compra.linea_iva10())
                else:
                    file2.write(compra.linea_iva10().replace("|", "") + "\n")

            if compra.iva21():
                if args.pantalla:
                    print(compra.linea_iva21())
                else:
                    file2.write(compra.linea_iva21.replace("|", "") + "\n")

            if compra.iva27():
                if args.pantalla:
                    print(compra.linea_iva27())
                else:
                    file2.write(compra.linea_iva27.replace("|", "") + "\n")

        except:
            print("Error al procesar la factura de compras Nº %s" % row["idfacprovedor"])

    file1.close()
    file2.close()

def iva_ventas():
    global conn
    desde = date(args.a, args.m, 1)
    hasta = date(args.a, args.m,
                 calendar.monthrange(args.a, args.m)[1])

    SQL = "SELECT idfactura, fecha, tipocomprob, letra, terminal, numero, c_iva, cuit, nombre, " \
          "gravado, no_grav, iva, otro_iva, ii, p_ibb, p_iva, total " \
          "FROM citi_ventas_v " \
          "WHERE fecha >= '{}' AND FECHA <= '{}'".format(desde, hasta)
    # "WHERE idfactura = 81981"

    file1 = open(args.ruta + "/03-Ventas.txt", "w")
    file2 = open(args.ruta + "/04-Ventas-ALI.txt", "w")
    cursor = conn.cursor()
    for row in cursor.execute(SQL).itermap():
        venta = Venta(row["fecha"], row["tipocomprob"] + row["letra"], row["terminal"], row["numero"],
                      row["c_iva"], row["cuit"], row["nombre"],
                      row["gravado"], row["no_grav"],
                      row["iva"], row["otro_iva"], row["ii"],
                      row["p_ibb"], row["p_iva"], row["total"])

        try:
            if venta.es_valido():
                # factura de venta
                if args.pantalla:
                    print(venta)
                else:
                    file1.write(str(venta).replace("|", "") + "\n")

                # información de alícuotas
                if args.pantalla:
                    print(venta.linea_iva())
                else:
                    file2.write(venta.linea_iva().replace("|", "") + "\n")

        except:
            print("Error al procesar la factura de ventas Nº %s" % row["idfactura"])
            
    file1.close()
    file2.close()


if __name__=="__main__":
    global conn

    dbconnect()

    if conn:
        # if args.pantalla: print("-- libro iva compras ----")
        # iva_compras()
        if args.pantalla: print("-- libro iva ventas -----")
        iva_ventas()

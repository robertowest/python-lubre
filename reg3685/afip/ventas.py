from datetime import date
from unidecode import unidecode


class Venta:
    linea_iva = []

    def __init__(self, fecha, comprob, terminal, numero,
                 cond_iva, cuit, nombre,
                 gravado, no_grav, iva, otro_iva, ii, p_ibb, p_iva, total):
        self.__fecha = fecha
        self.__comprob = comprob
        self.__terminal = terminal
        self.__numero = numero
        self.__cond_iva = cond_iva
        self.__cuit = cuit[0:13]
        self.__nombre = nombre[0:30]
        self.__gravado = abs(float(gravado))
        self.__no_grav = abs(float(no_grav))
        self.__iva = abs(float(iva))
        self.__otro_iva = abs(float(otro_iva))
        self.__ii = abs(float(ii))
        self.__p_ibb = abs(float(p_ibb))
        self.__p_iva = abs(float(p_iva))
        self.__total = abs(float(total))
        self.recalcular()

    def __str__(self):
        linea = [
            self.fecha(),
            self.comprobante(),
            self.terminal(),
            self.numero(),
            self.numero(),
            "80",
            self.cuit(),
            self.nombre(),
            self.formato_numero(self.__total, 15),
            self.formato_numero(self.__no_grav, 15),
            "0".rjust(15, "0"),
            "0".rjust(15, "0"),
            self.formato_numero(self.__p_iva, 15),
            self.formato_numero(self.__p_ibb, 15),
            "0".rjust(15, "0"),
            self.formato_numero(self.__ii, 15),
            "PES",
            "0001000000",
            "1",
            self.validar_operacion(self.__no_grav, self.__total),
            self.formato_numero(self.__otro_iva, 15),
            "00000000"
        ]
        return "|".join(linea)

    def recalcular(self):
        if self.__numero == 82:
            import pdb; pdb.set_trace()

        neto = self.__gravado
        no_grav = self.__no_grav
        iva = self.__iva
        otros = self.__otro_iva + self.__ii + self.__p_ibb + self.__p_iva
        total = self.__total
        dif = round(total - (neto + no_grav + iva + otros), 2)

        # si la diferencia es mayor que el redondeo, recalculamos
        if abs(dif) > 1:
            print("Recalculando comprobantes %s de la terminal %s" % (self.__numero, self.__terminal))
            neto = round(iva / .21, 2)
            no_grav = 0
            total = neto + iva + otros

        elif dif != 0:
            self.__neto = neto - dif
            self.__no_grav = 0

        self.__gravado = neto
        self.__no_grav = no_grav
        self.__total = total

    def fecha(self):
        if type(self.__fecha) is date:
            return str(self.__fecha.strftime('%Y%m%d'))
        else:
            return "".join([x for x in self.__fecha if x.isdigit()])

    def comprobante(self):
        switcher = {
            'FACA': '001',
            'FACB': '006',
            'FACC': '011',
            'LSGA': '090',
            'NCRA': '003',
            'NCRB': '008',
            'NCRC': '013',
            'NDEA': '002',
            'NDEB': '007',
            'NDEC': '012',
            'LPRA': '060',
        }
        return switcher.get(self.__comprob, "FACA")

    def terminal(self):
        if self.__terminal == 0:
            return "00001"
        else:
            return str(self.__terminal).rjust(5, '0')

    def numero(self):
        return str(self.__numero).rjust(20, '0')

    def cuit(self):
        return "".join([x for x in self.__cuit if x.isdigit()]).rjust(20, '0')

    def nombre(self):
        return unidecode(self.__nombre).ljust(30, ' ')

    def formato_numero(self, valor, largo):
        return format(valor, '.2f').replace(".", "").rjust(largo, '0')

    def validar_operacion(self, valor1, valor2):
        if valor1 == valor2:
            return 'N'
        else:
            return '0'

    def valor_iva(self, iva, porcentaje, largo):
        neto = round(iva / porcentaje, 2)
        return format(neto, '.2f').replace(".", "").rjust(largo, '0')

    def es_valido(self):
        if self.__iva == 0:
            return False
        return True

    def iva(self):
        return self.__iva != 0

    def __define_linea_iva(self):
        global linea_iva

        linea_iva = [
            self.comprobante(),
            self.terminal(),
            self.numero()
        ]

    def linea_iva(self):
        global linea_iva
        self.__define_linea_iva()

        if self.__iva != 0:
            linea2 = linea_iva
            # linea2.append(self.valor_iva(self.__iva, .21, 15))
            linea2.append(self.formato_numero(self.__gravado, 15))
            linea2.append("0005")
            linea2.append(self.formato_numero(self.__iva, 15))
            return "|".join(linea2)

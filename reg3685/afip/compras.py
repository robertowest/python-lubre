from datetime import date
from unidecode import unidecode

class Compra:
    linea_iva = []

    def __init__(self, fecha, comprob, terminal, numero,
                       cuit, nombre,
                       neto, no_grab, iva21, iva10, iva27, p_ibb, p_iva, itc, total, c_ali):
        self.__fecha = fecha
        self.__comprob = comprob
        self.__terminal = terminal
        self.__numero = numero
        self.__cuit = cuit[0:13]
        self.__nombre = nombre[0:30]
        self.__neto = abs(float(neto))
        self.__no_grab = abs(float(no_grab))
        self.__iva21 = abs(float(iva21))
        self.__iva10 = abs(float(iva10))
        self.__iva27 = abs(float(iva27))
        self.__p_ibb = abs(float(p_ibb))
        self.__p_iva = abs(float(p_iva))
        self.__itc = abs(float(itc))
        self.__total = abs(float(total))
        self.__c_ali = c_ali
        self.recalcular()

    def __str__(self):
        linea = [
            self.fecha(),
            self.comprobante(),
            self.terminal(),
            self.numero(),
            "".rjust(16, " "),
            "80",
            self.cuit(),
            self.nombre(),
            self.formato_numero(self.__total, 15),
            self.formato_numero(self.__no_grab, 15),
            "0".rjust(15, "0"),
            self.formato_numero(self.__p_iva, 15),
            "0".rjust(15, "0"),
            self.formato_numero(self.__p_ibb, 15),
            "0".rjust(15, "0"),
            self.formato_numero(self.__itc, 15),
            "PES",
            "0001000000",
            str(self.__c_ali),
            "0",
            "0".rjust(15, "0"),
            "0".rjust(15, "0"),
            "0".rjust(11, "0"),
            "".rjust(30, " "),
            "0".rjust(15, "0")
        ]
        return "|".join(linea)

    def recalcular(self):
        # if self.__numero == 16217:
        #     import pdb; pdb.set_trace()

        neto = self.__neto
        iva = self.__iva21 + self.__iva10 + self.__iva27
        otros = self.__p_ibb + self.__p_iva + self.__itc
        total = self.__total

        no_grab = total - (neto + iva + otros)
        if no_grab != 0:
            if (total > 0 and no_grab < 0) or (total < 0 and no_grab > 0):
                # si no_grab es diferente signo del total, recalcular en función de alicuotas
                neto = round(self.__iva21 / .21, 2) + \
                       round(self.__iva10 / .105, 2) + \
                       round(self.__iva27 / .27, 2)
                self.__no_grab = 0
                self.__neto = neto
                self.__total = neto + iva + otros

            elif abs(no_grab) > 1:
                self.__no_grab = no_grab

            else:
                self.__neto = neto - no_grab
                self.__no_grab = 0

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
        # if valor < 0:
        #     return '-' + format(abs(valor), '.2f').replace(".", "").rjust(largo - 1, '0')
        # else:
        #     return format(valor, '.2f').replace(".", "").rjust(largo, '0')
        return format(valor, '.2f').replace(".", "").rjust(largo, '0')

    def valor_iva(self, iva, porcentaje, largo):
        neto = round(iva / porcentaje, 2)
        return format(neto, '.2f').replace(".", "").rjust(largo, '0')

    def iva10(self):
        return self.__iva10 != 0

    def iva21(self):
        return self.__iva21 != 0

    def iva27(self):
        return self.__iva27 != 0

    def __define_linea_iva(self):
        global linea_iva

        linea_iva = [
            self.comprobante(),
            self.terminal(),
            self.numero(),
            "80",
            self.cuit()
        ]

    def linea_iva10(self):
        global linea_iva
        self.__define_linea_iva()

        if self.__iva10 != 0:
            linea2 = linea_iva
            linea2.append(self.valor_iva(self.__iva10, .105, 15))
            linea2.append("0004")
            linea2.append(self.formato_numero(self.__iva10, 15))
            return "|".join(linea2)

    def linea_iva21(self):
        global linea_iva
        self.__define_linea_iva()

        if self.__iva21 != 0:
            linea2 = linea_iva
            linea2.append(self.valor_iva(self.__iva21, .21, 15))
            linea2.append("0005")
            linea2.append(self.formato_numero(self.__iva21, 15))
            return "|".join(linea2)

    def linea_iva27(self):
        global linea_iva
        self.__define_linea_iva()

        if self.__iva27 != 0:
            linea2 = linea_iva
            linea2.append(self.valor_iva(self.__iva27, .27, 15))
            linea2.append("0006")
            linea2.append(self.formato_numero(self.__iva27, 15))
            return "|".join(linea2)

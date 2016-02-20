from PyQt5.QtCore import QPoint, QRect, QSize, Qt
from PyQt5.QtGui import (QBrush, QPainter,
                         QPainterPath, QPalette, QPen, QPixmap, QPolygon, QColor)
from PyQt5.QtWidgets import (QApplication, QMainWindow, QComboBox, QGridLayout,
                             QLabel, QSpinBox, QWidget, QPushButton, QLineEdit)
import random
import sys
import time


class RenderArea(QWidget):
    points = QPolygon([
        QPoint(10, 80),
        QPoint(90, 10),
        QPoint(80, 30),
        QPoint(90, 70)
    ])

    Line, Points, Polyline, Polygon, Rect, RoundedRect, Ellipse, Arc, Chord, \
    Pie, Path, Text, Pixmap = range(13)


    def __init__(self, dimension, tablero, cant_equipos, turnos, parent=None):
        super(RenderArea, self).__init__(parent)

        self.colores_todos = [QColor(200, 100, 0), QColor(50, 100, 100), QColor(120, 100, 100), QColor(100, 30, 60),
                              QColor(150, 2, 150), QColor(4, 200, 200)]
        self.dimension = dimension
        self.tablero = tablero
        self.pen = QPen()
        self.brush = QBrush()
        self.brush.setColor(Qt.green)
        self.pixmap = QPixmap()
        self.colores = self.crea_colores(cant_equipos)
        self.turnos = turnos
        self.posiciones = {}

        self.shape = RenderArea.Polygon
        self.antialiased = True
        self.pixmap.load('candela 2.ico')

        self.setBackgroundRole(QPalette.Base)
        self.setAutoFillBackground(True)

    def minimumSizeHint(self):
        return QSize(100, 100)

    def sizeHint(self):
        return QSize(400, 200)

    def setShape(self, shape):
        self.shape = shape
        self.update()

    def setPen(self, pen):
        self.pen = pen
        self.update()

    def setAntialiased(self, antialiased):
        self.antialiased = antialiased
        self.update()

    def paintEvent(self, event):
        rect = QRect(0, 0, self.width() / self.dimension, self.width() / self.dimension)
        self.dame_posiciones()

        path = QPainterPath()
        path.moveTo(20, 80)
        path.lineTo(20, 30)
        path.cubicTo(80, 0, 50, 50, 80, 80)

        painter = QPainter(self)
        painter.setPen(self.pen)
        painter.setBrush(self.brush)
        if self.antialiased:
            painter.setRenderHint(QPainter.Antialiasing)
        columna = 0
        for x in range(0, self.height(), self.height() // self.dimension):
            fila = 0
            for y in range(0, self.width(), self.width() // self.dimension):
                painter.save()
                painter.translate(y, x)
                painter.drawRect(rect)
                self.brush.setColor(Qt.green)
                if columna < self.dimension and fila < self.dimension and self.tablero[columna][fila] == 0:
                    painter.fillRect(rect, QColor(240, 150, 130))
                elif columna < self.dimension and fila < self.dimension:
                    painter.fillRect(rect, self.colores[self.tablero[columna][fila] - 1])
                    painter.drawText(rect, Qt.AlignCenter, '[ ' + str(self.tablero[columna][fila]) + ' ] ')
                painter.restore()
                #painter.drawPixmap(rect, self.pixmap)
                #painter.restore()
                fila += 1
            columna += 1

        painter.setPen(self.palette().dark().color())
        painter.setBrush(Qt.NoBrush)
        #painter.drawRect(QRect(0, 0, self.width() - 1, self.height() - 1))

    def crea_colores(self, cant_equipos):
        colores = []
        for x in range(cant_equipos):
            colores.append(self.colores_todos[x])
        return colores

    def dame_posiciones(self):
        count = 1
        for x in self.turnos:
            self.posiciones[count] = x
            count += 1


IdRole = Qt.UserRole


class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.t = -1
        self.cant_equipo = 2
        self.nombre = ''
        self.cant_agente = 5
        self.equipo_agente = {'alfa': 1, 'beta': 2}
        self.equipos = {1: [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],
                        2: [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]}
        self.validez = {1: [True, True, True, True, True],
                        2: [True, True, True, True, True]}
        self.tipo_equipo = {1: 'Random (F)',
                            2: 'Random (F)'}
        self.resize(650, 685)
        self.equipo_turno = ''
        self.turnos = []
        self.coordenadas = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        self.coordenadas_todas = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
        self.posiciones_agentes = {}
        self.posiciones = []

        #Dimension del terreno
        self.dimensionBox = QSpinBox()
        self.dimensionBox.setRange(8, 20)

        dimensionLabel = QLabel("Dimension del Terreno:")
        dimensionLabel.setBuddy(self.dimensionBox)
        self.dimensionBox.valueChanged.connect(self.actualizar_dimension)
        self.dimension = self.dimensionBox.value()
        self.campo = []
        self.ubica_equipos()
        print(self.campo)
        self.renderArea = RenderArea(self.dimension, self.campo, self.cant_equipo, self.turnos)
        #self.resize(self.renderArea.width() + 30, self.renderArea.height() + 30)
        #Cantidad de Equipos
        self.cant_equipoBox = QSpinBox()
        self.cant_equipoBox.setRange(2, 5)

        cant_equipoLabel = QLabel("Cantidad de Equipos:")
        cant_equipoLabel.setBuddy(self.cant_equipoBox)
        self.cant_equipoBox.valueChanged.connect(self.actualizar_cantidad_equipos)

        #LineEdit para el nombre de los equipos
        self.nombreLine = QLineEdit()

        nombreLabel = QLabel("Nombre:")
        nombreLabel.setBuddy(self.nombreLine)
        self.nombreLine.textChanged.connect(self.actualizar_nombre_equipos)

        #Boton para guardar el nombre de los equipos
        self.salvar_nombre = QPushButton()
        self.salvar_nombre.setText('Salvar')
        self.salvar_nombre.clicked.connect(self.salvar_nombre_equipo)

        #ComboBox que tiene el nombre de los equipos
        self.nombres = QComboBox()

        nombreComboLabel = QLabel("Equipos:")
        nombreComboLabel.setBuddy(self.nombres)

        #ComboBox que tiene el tipo de agente de los equipos
        self.tipo = QComboBox()
        self.tipo.addItem('Random')
        self.tipo.addItem('Random (F)')
        self.tipo.addItem('Utilidad')
        self.tipo.addItem('Utilidad (F)')
        self.tipo.addItem('Reglas')
        self.tipo.addItem('Reglas (F)')

        tipoComboLabel = QLabel("Categoria:")
        tipoComboLabel.setBuddy(self.tipo)


        #Cantidad de Agentes por equipos
        self.cant_agenteBox = QSpinBox()
        self.cant_agenteBox.setRange(5, 10)

        cant_agenteLabel = QLabel("Agentes:")
        cant_agenteLabel.setBuddy(self.cant_agenteBox)
        self.cant_agenteBox.valueChanged.connect(self.actualizar_cantidad_agentes)


        #Boton para Salvar la cantidad de agentes por equipos
        self.salvar_equipo = QPushButton()
        self.salvar_equipo.setText('Salvar')
        self.salvar_equipo.clicked.connect(self.salvar_agente)

        self.configuracion = QPushButton()
        self.configuracion.setText('Configuracion')
        self.configuracion.clicked.connect(self.show_configuracion)

        self.agente = QPushButton()
        self.agente.setText('Agente')
        self.agente.clicked.connect(self.show_agente)

        self.equipo = QPushButton()
        self.equipo.setText(' Cambiar Turno')
        self.equipo.clicked.connect(self.show_equipo)

        self.penWidthSpinBox = QSpinBox()
        self.penWidthSpinBox.setRange(2, 20)
        self.penWidthSpinBox.setSpecialValueText("2")

        penWidthLabel = QLabel("Pen &Width:")
        penWidthLabel.setBuddy(self.penWidthSpinBox)

        self.penWidthSpinBox.valueChanged.connect(self.penChanged)

        self.mainLayout = QGridLayout()
        self.mainLayout.setColumnStretch(0, 0)
        self.mainLayout.setColumnStretch(7, 0)
        self.mainLayout.addWidget(self.renderArea, 0, 0, 1, 7)
        self.mainLayout.setRowMinimumHeight(1, 6)
        self.mainLayout.addWidget(penWidthLabel, 6, 0, Qt.AlignRight)
        self.mainLayout.addWidget(self.penWidthSpinBox, 6, 1)
        self.mainLayout.addWidget(dimensionLabel, 3, 0, Qt.AlignRight)
        self.mainLayout.addWidget(self.dimensionBox, 3, 1)
        self.mainLayout.addWidget(cant_equipoLabel, 3, 2, Qt.AlignRight)
        self.mainLayout.addWidget(self.cant_equipoBox, 3, 3)
        self.mainLayout.addWidget(nombreLabel, 3, 4, Qt.AlignRight)
        self.mainLayout.addWidget(self.nombreLine, 3, 5)
        self.mainLayout.addWidget(self.salvar_nombre, 3, 6, Qt.AlignRight)
        self.mainLayout.addWidget(nombreComboLabel, 4, 0, Qt.AlignRight)
        self.mainLayout.addWidget(self.nombres, 4, 1)
        self.mainLayout.addWidget(tipoComboLabel, 4, 2, Qt.AlignRight)
        self.mainLayout.addWidget(self.tipo, 4, 3)
        self.mainLayout.addWidget(cant_agenteLabel, 4, 4, Qt.AlignRight)
        self.mainLayout.addWidget(self.cant_agenteBox, 4, 5)
        self.mainLayout.addWidget(self.salvar_equipo, 4, 6)
        self.mainLayout.addWidget(self.configuracion, 6, 6)
        self.mainLayout.addWidget(self.agente, 6, 4)
        self.mainLayout.addWidget(self.equipo, 6, 5)
        self.setLayout(self.mainLayout)

        self.penChanged()

        self.setWindowTitle("Total War")

    def penChanged(self):
        width = self.penWidthSpinBox.value()
        self.renderArea.setPen(QPen(Qt.black, width))

    def actualizar_dimension(self, valor):
        self.dimension = valor
        self.equipos = {}
        self.equipo_agente = {}
        self.validez = {}

    def actualizar_cantidad_equipos(self, valor):
        self.cant_equipo = valor

    def actualizar_nombre_equipos(self, valor):
        self.nombre = valor

    def salvar_nombre_equipo(self):
        self.nombres.addItem(self.nombre)
        count = len(self.equipo_agente.keys())
        self.equipo_agente[self.nombre] = count + 1
        self.equipos[count + 1] = []
        self.validez[count + 1] = []

    def actualizar_cantidad_agentes(self, valor):
        self.cant_agente = valor

    def salvar_agente(self):
        self.tipo_equipo[self.equipo_agente[self.nombres.currentText()]] = self.tipo.currentText()
        for x in range(self.cant_agente):
            self.equipos[self.equipo_agente[self.nombres.currentText()]].append((0, 0))
            self.validez[self.equipo_agente[self.nombres.currentText()]].append(True)

    def show_configuracion(self):
        print('******* Se realizo un nueva configuracion del terreno *******')
        self.ubica_equipos()
        print(self.campo)
        self.renderArea = RenderArea(self.dimension, self.campo, self.cant_equipo, self.turnos)
        self.renderArea.dame_posiciones()
        print('Turnos: ' + str(self.renderArea.posiciones))
        self.mainLayout.addWidget(self.renderArea, 0, 0, 1, 7)
        width = self.penWidthSpinBox.value()
        self.renderArea.setPen(QPen(Qt.black, width))
        #self.resize(self.renderArea.width() + 50, self.renderArea.height() + 30)

    def show_agente(self):
        self.agente_por_equipo()
        self.renderArea = RenderArea(self.dimension, self.campo, self.cant_equipo, self.turnos)
        self.mainLayout.addWidget(self.renderArea, 0, 0, 1, 7)
        width = self.penWidthSpinBox.value()
        self.renderArea.setPen(QPen(Qt.black, width))

    def show_equipo(self):
        self.t += 1
        if self.t == len(self.turnos):
            self.t = 0
        self.orden_de_agentes()
        print('Cambia el Turno para el Equipo: ' + str(self.turnos[self.t]))
        self.imprime_agentes()

    def imprime_agentes(self):
        for a in self.posiciones:
            if self.validez[self.turnos[self.t]][a]:
                print(
                    'Agente: ' + str(a) + ' Se encuentra en la posicion: ' + str(self.equipos[self.turnos[self.t]][a]))

    def ubica_equipos(self):
        self.campo = []
        for x in range(self.dimension):
            self.campo.append([])
            for y in range(self.dimension):
                self.campo[x].append(0)
        for e in self.equipos.keys():
            for a in range(len(self.equipos[e])):
                x = random.randint(0, self.dimension - 1)
                y = random.randint(0, self.dimension - 1)
                while self.campo[y][x] != 0:
                    x = random.randint(0, self.dimension - 1)
                    y = random.randint(0, self.dimension - 1)
                self.campo[y][x] = e
                self.equipos[e][a] = (y, x)
                self.validez[e][a] = True
        self.turnos = []
        for x in self.equipo_agente.keys():
            self.turnos.append(self.equipo_agente[x])
        self.turnos = random.sample(range(1, len(self.turnos) + 1), len(self.turnos))

    def agente_por_equipo(self):
        francotirador = True
        if self.baja_equipo():
            return
        p = 0
        while p < len(self.posiciones):
            rr = random.randint(0, 1)
            if rr == 1:
               ataco = True
            else:
               ataco = False
            pos = self.posiciones[p]
            if not self.validez[self.turnos[self.t]][pos]:
                p += 1
                continue
            #r = random.randint(1, 4)
            print(str(self.equipos[self.turnos[self.t]][pos]))
            if self.tipo_equipo[self.turnos[self.t]] == 'Utilidad (F)':
                francotirador = True
                aux = self.contar_posibles_bajas(self.turnos[self.t], pos, francotirador)
                print('me quedo con ' + str(aux))
                if aux[1] < 0:
                    r = 0
                    p += 1
                    continue
                else:
                    r = aux[0]
            elif self.tipo_equipo[self.turnos[self.t]] == 'Utilidad':
                francotirador = False
                aux = self.contar_posibles_bajas(self.turnos[self.t], pos, francotirador)
                print('me quedo con ' + str(aux))
                if aux[1] < 0:
                    r = 0
                    p += 1
                    continue
                else:
                    r = aux[0]
            elif self.tipo_equipo[self.turnos[self.t]] == 'Random (F)':
                francotirador = True
                r = self.moverse_random()
            elif self.tipo_equipo[self.turnos[self.t]] == 'Random':
                francotirador = False
                r = self.moverse_random()
            elif self.tipo_equipo[self.turnos[self.t]] == 'Reglas':
                francotirador = False
                r = self.moverse_bordes(self.turnos[self.t], pos)
                if r == 5:
                    r = self.moverse_random()
            elif self.tipo_equipo[self.turnos[self.t]] == 'Reglas (F)':
                francotirador = True
                r = self.moverse_bordes(self.turnos[self.t], pos)
                if r == 5:
                    r = self.moverse_random()
            if r == 1:
                self.moverse_arriba(self.turnos[self.t], pos, francotirador, ataco)
                self.equipo_ganador()
                p += 1
                continue
            if r == 2:
                self.moverse_derecha(self.turnos[self.t], pos, francotirador, ataco)
                self.equipo_ganador()
                p += 1
                continue
            if r == 3:
                self.moverse_abajo(self.turnos[self.t], pos, francotirador, ataco)
                self.equipo_ganador()
                p += 1
                continue
            if r == 4:
                self.moverse_izquierda(self.turnos[self.t], pos, francotirador, ataco)
                self.equipo_ganador()
                p += 1
                continue

    def orden_de_agentes(self):
        self.posiciones = []
        for x in range(len(self.equipos[self.turnos[self.t]])):
            self.posiciones.append(x)
        self.posiciones = random.sample(range(0, len(self.posiciones)), len(self.posiciones))
        p = 0

    def baja_equipo(self):
        for x in self.validez[self.turnos[self.t]]:
            if x:
                return False
        return True

    def equipo_ganador(self):
        aux = (0, 0)
        auxiliar = 0
        for e in self.validez.keys():
            auxiliar = 0
            for a in self.validez[e]:
                if a:
                    auxiliar += 1
            if auxiliar > aux[1]:
                aux = (e, auxiliar)
        # for e in self.equipos.keys():
        #     if len(self.equipos[e]) > aux[1]:
        #         aux = (e, len(self.equipos[e]))
        for e in self.equipo_agente.keys():
            if self.equipo_agente[e] == aux[0]:
                print('El Equipo:  ' + str(e) + '[' + str(aux[0]) + ']' + ' es el ganador con: ' + str(
                    aux[1]) + ' agentes')

    def moverse_arriba(self, equipo, pos, francotirador, ataco):
        agente = self.equipos[equipo][pos]
        print('Soy de equipo: ' + str(equipo) + ' --> ' + str(agente) + ' arriba')
        time.sleep(0.05)
        new_fila = agente[0] - 1
        columna = agente[1]
        if new_fila < 0:
            return False
        if self.campo[new_fila][columna] == 0:
            self.campo[new_fila][columna] = equipo
            self.campo[agente[0]][agente[1]] = 0
            self.equipos[equipo][pos] = (new_fila, columna)
            print('Me movi a: ' + str((new_fila, columna)))
            self.renderArea = RenderArea(self.dimension, self.campo, self.cant_equipo, self.turnos)
            self.mainLayout.addWidget(self.renderArea, 0, 0, 1, 7)
            time.sleep(0.5)
            if ataco:
                if francotirador:
                    print('Ataco como francotirador')
                    for c in self.coordenadas:
                        for x in range(1, self.dimension):
                            if c[0] * x + new_fila < 0 or c[0] * x + new_fila >= self.dimension:
                                break
                            elif c[1] * x + agente[1] < 0 or c[1] * x + agente[1] >= self.dimension:
                                break
                            else:
                                e = self.campo[c[0] * x + new_fila][c[1] * x + agente[1]]
                                if e != 0:
                                    for a in range(len(self.equipos[e])):
                                        if self.equipos[e][a][0] == c[0] * x + new_fila and self.equipos[e][a][1] == c[1] * x + \
                                                agente[1] and self.validez[e][a]:
                                            self.validez[e][a] = False
                                            #self.equipos[e].remove((c[0] * x + new_fila, c[1] * x + agente[1]))
                                            self.campo[c[0] * x + new_fila][c[1] * x + agente[1]] = 0
                else:
                    print('Ataco en mis casillas adyacentes')
                    for c in self.coordenadas_todas:
                        x = 1
                        if c[0] * x + new_fila < 0 or c[0] * x + new_fila >= self.dimension:
                            continue
                        elif c[1] * x + agente[1] < 0 or c[1] * x + agente[1] >= self.dimension:
                            continue
                        else:
                            e = self.campo[c[0] * x + new_fila][c[1] * x + agente[1]]
                            if e != 0:
                                for a in range(len(self.equipos[e])):
                                    if self.equipos[e][a][0] == c[0] * x + new_fila and self.equipos[e][a][1] == c[1] * x + \
                                            agente[1] and self.validez[e][a]:
                                        self.validez[e][a] = False
                                        #self.equipos[e].remove((c[0] * x + new_fila, c[1] * x + agente[1]))
                                        self.campo[c[0] * x + new_fila][c[1] * x + agente[1]] = 0

    def moverse_abajo(self, equipo, pos, francotirador, ataco):
        agente = self.equipos[equipo][pos]
        print('Soy de equipo: ' + str(equipo) + '--> ' + str(agente) + ' abajo')
        time.sleep(0.05)
        new_fila = agente[0] + 1
        columna = agente[1]
        if new_fila >= self.dimension:
            return False
        if self.campo[new_fila][columna] == 0:
            self.campo[new_fila][columna] = equipo
            self.campo[agente[0]][columna] = 0
            self.equipos[equipo][pos] = (new_fila, columna)
            print('Me movi a: ' + str((new_fila, columna)))
            self.posiciones_agentes[pos] = (new_fila, columna)
            self.renderArea = RenderArea(self.dimension, self.campo, self.cant_equipo, self.turnos)
            self.mainLayout.addWidget(self.renderArea, 0, 0, 1, 7)
            time.sleep(0.5)
            if ataco:
                if francotirador:
                    print('Ataco como francotirador')
                    for c in self.coordenadas:
                        for x in range(1, self.dimension):
                            if c[0] * x + new_fila < 0 or c[0] * x + new_fila >= self.dimension:
                                break
                            elif c[1] * x + columna < 0 or c[1] * x + columna >= self.dimension:
                                break
                            else:
                                e = self.campo[c[0] * x + new_fila][c[1] * x + columna]
                                if e != 0:
                                    for a in range(len(self.equipos[e])):
                                        if self.equipos[e][a][0] == c[0] * x + new_fila and self.equipos[e][a][1] == c[1] * x + \
                                                agente[1] and self.validez[e][a]:
                                            self.validez[e][a] = False
                                            #self.equipos[e].remove((c[0] * x + new_fila, c[1] * x + agente[1]))
                                            self.campo[c[0] * x + new_fila][c[1] * x + agente[1]] = 0
                else:
                    print('Ataco a mis casillas adyacentes')
                    for c in self.coordenadas_todas:
                        x = 1
                        if c[0] * x + new_fila < 0 or c[0] * x + new_fila >= self.dimension:
                            continue
                        elif c[1] * x + columna < 0 or c[1] * x + columna >= self.dimension:
                            continue
                        else:
                            e = self.campo[c[0] * x + new_fila][c[1] * x + columna]
                            if e != 0:
                                for a in range(len(self.equipos[e])):
                                    if self.equipos[e][a][0] == c[0] * x + new_fila and self.equipos[e][a][1] == c[1] * x + \
                                            agente[1] and self.validez[e][a]:
                                        self.validez[e][a] = False
                                        #self.equipos[e].remove((c[0] * x + new_fila, c[1] * x + agente[1]))
                                        self.campo[c[0] * x + new_fila][c[1] * x + agente[1]] = 0

    def moverse_derecha(self, equipo, pos, francotirador, ataco):
        agente = self.equipos[equipo][pos]
        print('Soy de equipo: ' + str(equipo) + '--> ' + str(agente) + ' derecha')
        time.sleep(0.05)
        newcolumna = agente[1] + 1
        fila = agente[0]
        if newcolumna >= self.dimension:
            return False
        if self.campo[fila][newcolumna] == 0:
            self.campo[fila][newcolumna] = equipo
            self.campo[fila][agente[1]] = 0
            self.equipos[equipo][pos] = (fila, newcolumna)
            print('Me movi a: ' + str((fila, newcolumna)))
            self.posiciones_agentes[pos] = (fila, newcolumna)
            self.renderArea = RenderArea(self.dimension, self.campo, self.cant_equipo, self.turnos)
            self.mainLayout.addWidget(self.renderArea, 0, 0, 1, 7)
            time.sleep(0.5)
            if ataco:
                if francotirador:
                    print('Ataco como francotirador')
                    for c in self.coordenadas:
                        for x in range(1, self.dimension):
                            if c[0] * x + fila < 0 or c[0] * x + fila >= self.dimension:
                                break
                            elif c[1] * x + newcolumna < 0 or c[1] * x + newcolumna >= self.dimension:
                                break
                            else:
                                e = self.campo[c[0] * x + fila][c[1] * x + newcolumna]
                                if e != 0:
                                    for a in range(len(self.equipos[e])):
                                        if self.equipos[e][a][0] == c[0] * x + fila and self.equipos[e][a][1] == c[
                                            1] * x + newcolumna and self.validez[e][a]:
                                            self.validez[e][a] = False
                                            #self.equipos[e].remove((c[0] * x + new_fila, c[1] * x + agente[1]))
                                            self.campo[c[0] * x + fila][c[1] * x + newcolumna] = 0
                else:
                    print('Ataco a mis casillas adyacentes')
                    for c in self.coordenadas_todas:
                        x = 1
                        if c[0] * x + fila < 0 or c[0] * x + fila >= self.dimension:
                            continue
                        elif c[1] * x + newcolumna < 0 or c[1] * x + newcolumna >= self.dimension:
                            continue
                        else:
                            e = self.campo[c[0] * x + fila][c[1] * x + newcolumna]
                            if e != 0:
                                for a in range(len(self.equipos[e])):
                                    if self.equipos[e][a][0] == c[0] * x + fila and self.equipos[e][a][1] == c[1] * x + newcolumna and self.validez[e][a]:
                                        self.validez[e][a] = False
                                        #self.equipos[e].remove((c[0] * x + new_fila, c[1] * x + agente[1]))
                                        self.campo[c[0] * x + fila][c[1] * x + newcolumna] = 0

    def moverse_izquierda(self, equipo, pos, francotirador, ataco):
        agente = self.equipos[equipo][pos]
        print('Soy de equipo: ' + str(equipo) + '--> ' + str(agente) + ' izquierda')
        time.sleep(0.05)
        newcolumna = agente[1] - 1
        fila = agente[0]
        if newcolumna < 0:
            return False
        if self.campo[fila][newcolumna] == 0:
            self.campo[fila][newcolumna] = equipo
            self.campo[fila][agente[1]] = 0
            self.equipos[equipo][pos] = (fila, newcolumna)
            print('Me movi a: ' + str((fila, newcolumna)))
            self.posiciones_agentes[pos] = (fila, newcolumna)
            self.renderArea = RenderArea(self.dimension, self.campo, self.cant_equipo, self.turnos)
            self.mainLayout.addWidget(self.renderArea, 0, 0, 1, 7)
            time.sleep(0.5)
            if ataco:
                if francotirador:
                    print('Ataco como francotirador')
                    for c in self.coordenadas:
                        for x in range(1, self.dimension):
                            if c[0] * x + fila < 0 or c[0] * x + fila >= self.dimension:
                                break
                            elif c[1] * x + newcolumna < 0 or c[1] * x + newcolumna >= self.dimension:
                                break
                            else:
                                e = self.campo[c[0] * x + fila][c[1] * x + newcolumna]
                                if e != 0:
                                    for a in range(len(self.equipos[e])):
                                        if self.equipos[e][a][0] == c[0] * x + fila and self.equipos[e][a][1] == c[1] * x + newcolumna and self.validez[e][a]:
                                            self.validez[e][a] = False
                                            #self.equipos[e].remove((c[0] * x + new_fila, c[1] * x + agente[1]))
                                            self.campo[c[0] * x + fila][c[1] * x + newcolumna] = 0
                else:
                    print('Ataco a mis casillas adyacentes')
                    for c in self.coordenadas_todas:
                        x = 1
                        if c[0] * x + fila < 0 or c[0] * x + fila >= self.dimension:
                            continue
                        elif c[1] * x + newcolumna < 0 or c[1] * x + newcolumna >= self.dimension:
                            continue
                        else:
                            e = self.campo[c[0] * x + fila][c[1] * x + newcolumna]
                            if e != 0:
                                for a in range(len(self.equipos[e])):
                                    if self.equipos[e][a][0] == c[0] * x + fila and self.equipos[e][a][1] == c[1] * x + newcolumna and self.validez[e][a]:
                                        self.validez[e][a] = False
                                        #self.equipos[e].remove((c[0] * x + new_fila, c[1] * x + agente[1]))
                                        self.campo[c[0] * x + fila][c[1] * x + newcolumna] = 0

    def moverse_random(self):
        return random.randint(1, 4)

    #se va a mover a la posicion donde pueda matar la mayor cantidad de agentes del otro bando
    def moverse_bordes(self, equipo, pos):
        agente = self.equipos[equipo][pos]
        if agente[0] == 0:
            return 3
        if agente[1] == self.dimension - 1:
            return 4
        if agente[0] == self.dimension - 1:
            return 1
        if agente[1] == 0:
            return 2
        else:
            return 5

    def contar_posibles_bajas(self, equipo, pos, francotirador):
        posiciones = [self.bajas_arriba(equipo, pos, francotirador), self.bajas_derecha(equipo, pos, francotirador),
                      self.bajas_abajo(equipo, pos, francotirador), self.bajas_izquierda(equipo, pos, francotirador)]
        r = 0
        dif = 0
        es_cero = True
        for x in range(len(posiciones)):
            if posiciones[x][0] != 0 or posiciones[x][1] != 0:
                es_cero = False
        if not es_cero:
            for x in range(len(posiciones)):
                #print(str(x))
                #print(str(posiciones[x]))
                if (posiciones[x][1] - posiciones[x][0]) >= dif and (posiciones[x][1] - posiciones[x][0]) >= 0 and ((posiciones[x][1] != posiciones[x][0])  or ((posiciones[x][1] == posiciones[x][0])  and posiciones[x][1] == 0)):
                    dif = posiciones[x][1] - posiciones[x][0]
                    r = x + 1
        else:
            r = random.randint(1, 4)
        return r, dif

    def bajas_arriba(self, equipo, pos, francotirador):
        bajas_mi_equipo = 0
        bajas_otro_equipo = 0
        agente = self.equipos[equipo][pos]
        new_fila = agente[0] - 1
        columna = agente[1]
        if new_fila < 0:
            return bajas_mi_equipo, bajas_otro_equipo
        if self.campo[new_fila][columna] == 0:
            self.campo[new_fila][columna] = equipo
            self.campo[agente[0]][agente[1]] = 0
            self.equipos[equipo][pos] = (new_fila, columna)
            if francotirador:
                for c in self.coordenadas:
                    for x in range(1, self.dimension):
                        if c[0] * x + new_fila < 0 or c[0] * x + new_fila >= self.dimension:
                            break
                        elif c[1] * x + agente[1] < 0 or c[1] * x + agente[1] >= self.dimension:
                            break
                        else:
                            e = self.campo[c[0] * x + new_fila][c[1] * x + agente[1]]
                            if e != 0:
                                for a in range(len(self.equipos[e])):
                                    if self.equipos[e][a][0] == c[0] * x + new_fila and self.equipos[e][a][1] == c[1] * x + \
                                            agente[1] and self.validez[e][a]:
                                        if equipo == e:
                                            bajas_mi_equipo += 1
                                        else:
                                            bajas_otro_equipo += 1
            else:
                x = 1
                for c in self.coordenadas_todas:
                    if c[0] * x + new_fila < 0 or c[0] * x + new_fila >= self.dimension:
                        break
                    elif c[1] * x + agente[1] < 0 or c[1] * x + agente[1] >= self.dimension:
                        break
                    else:
                        e = self.campo[c[0] * x + new_fila][c[1] * x + agente[1]]
                        if e != 0:
                            for a in range(len(self.equipos[e])):
                                if self.equipos[e][a][0] == c[0] * x + new_fila and self.equipos[e][a][1] == c[1] * x + \
                                        agente[1] and self.validez[e][a]:
                                    if equipo == e:
                                        bajas_mi_equipo += 1
                                    else:
                                        bajas_otro_equipo += 1
            self.campo[new_fila][columna] = 0
            self.campo[agente[0]][agente[1]] = equipo
            self.equipos[equipo][pos] = (agente[0], agente[1])
        return bajas_mi_equipo, bajas_otro_equipo

    def bajas_abajo(self, equipo, pos, francotirador):
        bajas_mi_equipo = 0
        bajas_otro_equipo = 0
        agente = self.equipos[equipo][pos]
        new_fila = agente[0] + 1
        columna = agente[1]
        if new_fila >= self.dimension:
            return bajas_mi_equipo, bajas_otro_equipo
        if self.campo[new_fila][columna] == 0:
            self.campo[new_fila][columna] = equipo
            self.campo[agente[0]][agente[1]] = 0
            self.equipos[equipo][pos] = (new_fila, columna)
            if francotirador:
                for c in self.coordenadas:
                    for x in range(1, self.dimension):
                        if c[0] * x + new_fila < 0 or c[0] * x + new_fila >= self.dimension:
                            break
                        elif c[1] * x + agente[1] < 0 or c[1] * x + agente[1] >= self.dimension:
                            break
                        else:
                            e = self.campo[c[0] * x + new_fila][c[1] * x + agente[1]]
                            if e != 0:
                                for a in range(len(self.equipos[e])):
                                    if self.equipos[e][a][0] == c[0] * x + new_fila and self.equipos[e][a][1] == c[1] * x + \
                                            agente[1] and self.validez[e][a]:
                                        if equipo == e:
                                            bajas_mi_equipo += 1
                                        else:
                                            bajas_otro_equipo += 1
            else:
                x = 1
                for c in self.coordenadas_todas:
                    if c[0] * x + new_fila < 0 or c[0] * x + new_fila >= self.dimension:
                        break
                    elif c[1] * x + agente[1] < 0 or c[1] * x + agente[1] >= self.dimension:
                        break
                    else:
                        e = self.campo[c[0] * x + new_fila][c[1] * x + agente[1]]
                        if e != 0:
                            for a in range(len(self.equipos[e])):
                                if self.equipos[e][a][0] == c[0] * x + new_fila and self.equipos[e][a][1] == c[1] * x + \
                                        agente[1] and self.validez[e][a]:
                                    if equipo == e:
                                        bajas_mi_equipo += 1
                                    else:
                                        bajas_otro_equipo += 1
            self.campo[new_fila][columna] = 0
            self.campo[agente[0]][agente[1]] = equipo
            self.equipos[equipo][pos] = (agente[0], agente[1])
        return bajas_mi_equipo, bajas_otro_equipo

    def bajas_derecha(self,equipo, pos, francotirador):
        bajas_mi_equipo = 0
        bajas_otro_equipo = 0
        agente = self.equipos[equipo][pos]
        new_fila = agente[0]
        columna = agente[1] + 1
        if columna >= self.dimension:
            return bajas_mi_equipo, bajas_otro_equipo
        if self.campo[new_fila][columna] == 0:
            self.campo[new_fila][columna] = equipo
            self.campo[agente[0]][agente[1]] = 0
            self.equipos[equipo][pos] = (new_fila, columna)
            if francotirador:
                for c in self.coordenadas:
                    for x in range(1, self.dimension):
                        if c[0] * x + new_fila < 0 or c[0] * x + new_fila >= self.dimension:
                            break
                        elif c[1] * x + columna < 0 or c[1] * x + columna >= self.dimension:
                            break
                        else:
                            e = self.campo[c[0] * x + new_fila][c[1] * x + columna]
                            if e != 0:
                                for a in range(len(self.equipos[e])):
                                    if self.equipos[e][a][0] == c[0] * x + new_fila and self.equipos[e][a][1] == c[1] * x + \
                                            columna and self.validez[e][a]:
                                        if equipo == e:
                                            bajas_mi_equipo += 1
                                        else:
                                            bajas_otro_equipo += 1
            else:
                x = 1
                for c in self.coordenadas:
                    if c[0] * x + new_fila < 0 or c[0] * x + new_fila >= self.dimension:
                        break
                    elif c[1] * x + columna < 0 or c[1] * x + columna >= self.dimension:
                        break
                    else:
                        e = self.campo[c[0] * x + new_fila][c[1] * x + columna]
                        if e != 0:
                            for a in range(len(self.equipos[e])):
                                if self.equipos[e][a][0] == c[0] * x + new_fila and self.equipos[e][a][1] == c[1] * x + \
                                        agente[1] and self.validez[e][a]:
                                    if equipo == e:
                                        bajas_mi_equipo += 1
                                    else:
                                        bajas_otro_equipo += 1
            self.campo[new_fila][columna] = 0
            self.campo[agente[0]][agente[1]] = equipo
            self.equipos[equipo][pos] = (agente[0], agente[1])
        return bajas_mi_equipo, bajas_otro_equipo

    def bajas_izquierda(self,equipo, pos, francotirador):
        bajas_mi_equipo = 0
        bajas_otro_equipo = 0
        agente = self.equipos[equipo][pos]
        new_fila = agente[0]
        columna = agente[1] - 1
        if columna < 0:
            return bajas_mi_equipo, bajas_otro_equipo
        if self.campo[new_fila][columna] == 0:
            self.campo[new_fila][columna] = equipo
            self.campo[agente[0]][agente[1]] = 0
            self.equipos[equipo][pos] = (new_fila, columna)
            if francotirador:
                for c in self.coordenadas:
                    for x in range(1, self.dimension):
                        if c[0] * x + new_fila < 0 or c[0] * x + new_fila >= self.dimension:
                            break
                        elif c[1] * x + columna < 0 or c[1] * x + columna >= self.dimension:
                            break
                        else:
                            e = self.campo[c[0] * x + new_fila][c[1] * x + columna]
                            if e != 0:
                                for a in range(len(self.equipos[e])):
                                    if self.equipos[e][a][0] == c[0] * x + new_fila and self.equipos[e][a][1] == c[1] * x + \
                                            columna and self.validez[e][a]:
                                        if equipo == e:
                                            bajas_mi_equipo += 1
                                        else:
                                            bajas_otro_equipo += 1
            else:
                x = 1
                for c in self.coordenadas:
                    if c[0] * x + new_fila < 0 or c[0] * x + new_fila >= self.dimension:
                        break
                    elif c[1] * x + columna < 0 or c[1] * x + columna >= self.dimension:
                        break
                    else:
                        e = self.campo[c[0] * x + new_fila][c[1] * x + columna]
                        if e != 0:
                            for a in range(len(self.equipos[e])):
                                if self.equipos[e][a][0] == c[0] * x + new_fila and self.equipos[e][a][1] == c[1] * x + \
                                        columna and self.validez[e][a]:
                                    if equipo == e:
                                        bajas_mi_equipo += 1
                                    else:
                                        bajas_otro_equipo += 1
            self.campo[new_fila][columna] = 0
            self.campo[agente[0]][agente[1]] = equipo
            self.equipos[equipo][pos] = (agente[0], agente[1])
        return bajas_mi_equipo, bajas_otro_equipo

app = QApplication(sys.argv)
m = Window()
m.show()
app.exec_()

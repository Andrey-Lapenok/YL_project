import sys
import sqlite3
import random
import os
import shutil

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableView,  QInputDialog, QFileDialog, QComboBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel


class InvalidInputNecessary(Exception):
    pass


class InvalidInputTitle(Exception):
    pass


class EmptyInput(Exception):
    pass


class Main:
    def set_scenario(self, scenario):
        self.scenario = scenario + '/'

    def get_scenario(self):
        return self.scenario

    def interface(self):
        self.widg = Interface()
        self.widg.show()

    def redactor(self):
        self.widg.close()
        self.widg = Redactor()
        self.widg.show()

    def create_card(self, title):
        self.widg.close()
        self.widg = CreateCard(title)
        self.widg.show()

    def open_game(self):
        self.widg = OneGame()
        self.widg.show()

    def start(self):
        self.widg = Start()
        self.widg.show()

    def redactor_scenario(self, title):
        self.widg.close()
        self.widg = RedactorScenario(title)
        self.widg.show()

    def redactor_scenario_to_creating(self, title):
        self.widg = RedactorScenario(title)
        self.widg.show()


class Start(QMainWindow, Main):
    def __init__(self):
        try:
            QMainWindow.__init__(self)
            uic.loadUi('start.ui', self)

            self.open.clicked.connect(self.open_scenario)
            self.exit.clicked.connect(self._exit)
            self.create_scenario.clicked.connect(self._create_scenario)
            self.delete_scenario.clicked.connect(self._delete_scenario)

        except Exception:
            self.error("__init__")

    def _exit(self):
        sys.exit()

    def _delete_scenario(self):
        try:
            dlg = QFileDialog()
            dlg.setFileMode(QFileDialog.Directory)

            if dlg.exec_():
                shutil.rmtree(dlg.selectedFiles()[0])

        except Exception:
            self.error("delete_scenario")

    def open_scenario(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.Directory)

        if dlg.exec_():
            scenario = dlg.selectedFiles()
            Main.set_scenario(Main, scenario[0].split('/')[-1])
            Main.interface(Main)

    def _create_scenario(self):
        Main.redactor_scenario_to_creating(Main, None)

    def error(self, mes):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText(mes)
        msg.setInformativeText('Эх, опять воркинг-воркинг')
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()


class OneGame(QMainWindow, Main):
    def __init__(self):
        try:
            QMainWindow.__init__(self)
            uic.loadUi('game.ui', self)

            self.con = sqlite3.connect(Main.get_scenario(self) + "DB.sqlite")
            self.cur = self.con.cursor()

            self.f = open(Main.get_scenario(self) + "information.txt", encoding="utf-8")
            self.stats_label = self.f.readlines()[1].strip().split('|')
            self.l_1.setText(self.stats_label[0])
            self.l_2.setText(self.stats_label[1])
            self.l_3.setText(self.stats_label[2])
            self.l_4.setText(self.stats_label[3])
            self.l_5.setText(self.stats_label[4])
            self.l_6.setText(self.stats_label[5])
            self.f.seek(0)
            self.stats = list(map(int, self.f.readlines(0)[2].strip().split('|')))


            self._exit.clicked.connect(self.exit)
            self.start_cards = []
            for i in self.cur.execute("""SELECT title FROM cards WHERE available = 'true'""").fetchall():
                self.start_cards.append(i[0])

            self.f.seek(0)
            inf = list(map(lambda y: y.strip(), self.f.readlines()))
            self.label.setText(' '.join(inf[inf.index('<') + 1:inf.index('>')]))
            self.f.seek(0)
            self.picture.setPixmap(QPixmap(f"{Main.get_scenario(self)}{self.f.readlines()[-1].strip()}.png"))

            self.label_2.setText('')
            self.label_3.setText('')
            self.bt_1.setText("Далее")
            self.bt_1.clicked.connect(self._continue)
            self.bt_2.setText("Далее")
            self.bt_2.clicked.connect(self._continue)

            self.print_stats()
        except Exception:
            self.error("__init__")

    def set_all(self):
        try:
            self.event = self.cur.execute("""SELECT event FROM cards WHERE
                                                title = ?""", (self.title,)).fetchone()[0]
            self.var_1 = self.cur.execute("""SELECT var_1 FROM cards WHERE
                                                title = ?""", (self.title,)).fetchone()[0]
            self.var_2 = self.cur.execute("""SELECT var_2 FROM cards WHERE
                                                title = ?""", (self.title,)).fetchone()[0]
            self.mes_1 = self.cur.execute("""SELECT mes_1 FROM cards WHERE
                                                title = ?""", (self.title,)).fetchone()[0]
            self.mes_2 = self.cur.execute("""SELECT mes_2 FROM cards WHERE
                                                title = ?""", (self.title,)).fetchone()[0]
            self.ch_stats_1 = self.cur.execute("""SELECT d_pop_1, d_cor_1, d_inf_1, d_arm_1, d_econ_1, d_bud_1 FROM cards WHERE
                                                title = ?""", (self.title,)).fetchone()
            self.ch_stats_2 = self.cur.execute("""SELECT d_pop_2, d_cor_2, d_inf_2, d_arm_2, d_econ_2, d_bud_2  FROM cards WHERE
                                                title = ?""", (self.title,)).fetchone()
            self.image = self.cur.execute("""SELECT image FROM cards WHERE
                                                title = ?""", (self.title,)).fetchone()[0]
            self.cur.execute("""UPDATE cards
                                SET available = 'false'
                                WHERE title = ?""", (self.title,))
            self.cur.execute("""UPDATE cards
                                SET on_table = 'true'
                                WHERE title = ?""", (self.title,))
        except Exception:
            self.error("set_all")

    def get_card(self):
        try:
            self.title = list(self.cur.execute("""SELECT * FROM cards WHERE
                                    available = 'true' AND on_table = 'false'""").fetchall())

            self.title = list(filter(lambda x: self.check_cards(self.stats, x[21:27]), self.title))

            self.title = random.choice(self.title)[3]
            self.set_all()

            self.bt_1.clicked.disconnect()
            self.bt_1.clicked.connect(self._var_1)
            self.bt_2.clicked.disconnect()
            self.bt_2.clicked.connect(self._var_2)

        except Exception:
            self.recircle()
            self.error("get_card")

    def check_card(self, stat, nec_stat):
        try:
            if nec_stat == '.':
                return True
            if nec_stat[0] == '>' and stat > int(nec_stat[1:]):
                return True
            if nec_stat[0] == '<' and stat < int(nec_stat[1:]):
                return True
            return False
        except Exception:
            self.error("check_card")

    def check_cards(self, stats, nec_stats):
        try:
            return all([self.check_card(stats[i], nec_stats[i]) for i in range(6)])
        except Exception:
            self.error("check_cards")

    def print_event(self):
        try:
            self.label.setText(self.event)
            self.label_2.setText(self.var_1)
            self.label_3.setText(self.var_2)
            self.bt_1.setText("Выбрать первый вариант")
            self.bt_2.setText("Выбрать второй вариант")
            self.picture.setPixmap(QPixmap(f"{Main.get_scenario(self)}{self.image}.png"))
        except Exception:
            self.error("print_event")

    def print_stats(self):
        try:
            self.lb_1.setText(str(self.stats[0]))
            self.lb_2.setText(str(self.stats[1]))
            self.lb_3.setText(str(self.stats[2]))
            self.lb_4.setText(str(self.stats[3]))
            self.lb_5.setText(str(self.stats[4]))
            self.lb_6.setText(str(self.stats[5]))
        except Exception:
            self.error("print_stats")

    def _continue(self):
        try:
            self.get_card()
            self.print_stats()
            self.print_event()
            self.check_stats()
        except Exception:
            self.error("_continue")

    def _var_1(self):
        try:
            for i in range(6):
                self.stats[i] += self.ch_stats_1[i]
            self.label.setText(self.mes_1)
            self.print_stats()

            self.label_2.setText("")
            self.bt_1.setText("Далее")
            self.bt_1.clicked.disconnect()
            self.bt_1.clicked.connect(self._continue)
            self.label_3.setText("")
            self.bt_2.setText("Далее")
            self.bt_2.clicked.disconnect()
            self.bt_2.clicked.connect(self._continue)
            for i in self.cur.execute("""SELECT * FROM descent WHERE
                                id = (SELECT make_av_1 FROM cards WHERE 
                                            title = ?)""", (self.title,)).fetchone()[1:]:
                self.cur.execute("""UPDATE cards
                                    SET available = 'true'
                                    WHERE title = ?""", (i,))

            for i in self.cur.execute("""SELECT * FROM descent WHERE
                                id = (SELECT make_unav_1 FROM cards WHERE 
                                            title = ?)""", (self.title,)).fetchone()[1:]:
                self.cur.execute("""UPDATE cards
                                    SET available = 'false'
                                    WHERE title = ?""", (i,))
        except Exception:
            self.error("_var_1")

    def _var_2(self):
        try:
            for i in range(6):
                self.stats[i] += self.ch_stats_2[i]
            self.label.setText(self.mes_2)
            self.print_stats()

            self.label_2.setText("")
            self.bt_1.setText("Далее")
            self.bt_1.clicked.disconnect()
            self.bt_1.clicked.connect(self._continue)
            self.label_3.setText("")
            self.bt_2.setText("Далее")
            self.bt_2.clicked.disconnect()
            self.bt_2.clicked.connect(self._continue)

            for i in self.cur.execute("""SELECT * FROM descent WHERE
                                id = (SELECT make_av_2 FROM cards WHERE 
                                            title = ?)""", (self.title,)).fetchone()[1:]:
                self.cur.execute("""UPDATE cards
                                    SET available = 'true'
                                    WHERE title = ?""", (i,))

            for i in self.cur.execute("""SELECT * FROM descent WHERE
                                id = (SELECT make_unav_2 FROM cards WHERE 
                                            title = ?)""", (self.title,)).fetchone()[1:]:
                self.cur.execute("""UPDATE cards
                                    SET available = 'false'
                                    WHERE title = ?""", (i,))
        except Exception:
            self.error("_var_2")

    def check_stats(self):
        try:
            for i in range(6):
                self.stats[i] = max(self.stats[i], 0)
                self.stats[i] = min(self.stats[i], 100)

            for i in range(6):
                condition = self.cur.execute("""SELECT condition FROM finals WHERE
                                            id = ?""", (i + 1, )).fetchone()[0]
                if eval(f'{self.stats[i]}{condition}'):
                    self.final_event = self.cur.execute("""SELECT event FROM finals WHERE
                                            id = ?""", (i + 1, )).fetchone()[0]
                    x = self.cur.execute("""SELECT image FROM finals WHERE
                                                                id = ?""", (i + 1,)).fetchone()[0]
                    self.picture.setPixmap(QPixmap(f'{Main.get_scenario(self)}{x}'))
                    self.end()

        except Exception:
            self.error("check_stats")

    def end(self):
        try:
            self.label.setText(self.final_event)
            self.label_2.setText('Начать заново')
            self.label_3.setText('Выйти')

            self.bt_1.clicked.disconnect()
            self.bt_1.clicked.connect(self.retry)
            self.bt_2.clicked.disconnect()
            self.bt_2.clicked.connect(self.final_end)

            self.recircle()
        except Exception:
            self.error("end")

    def recircle(self):
        self.cur.execute("""UPDATE cards
                                        SET available = 'false'""")
        self.cur.execute("""UPDATE cards
                                        SET on_table = 'false'""")
        for i in self.start_cards:
            self.cur.execute("""UPDATE cards
                                SET available = 'true'
                                WHERE title = ?""", (i,))
            self.cur.execute("""UPDATE cards
                                SET on_table = 'false'
                                WHERE title = ?""", (i,))

    def retry(self):
        try:
            self.f = open(Main.get_scenario(self) + "information.txt", encoding="utf-8")
            self.stats_label = self.f.readlines()[1].strip().split('|')
            self.l_1.setText(self.stats_label[0])
            self.l_2.setText(self.stats_label[1])
            self.l_3.setText(self.stats_label[2])
            self.l_4.setText(self.stats_label[3])
            self.l_5.setText(self.stats_label[4])
            self.l_6.setText(self.stats_label[5])
            self.f.seek(0)
            self.stats = list(map(int, self.f.readlines(0)[2].strip().split('|')))

            self._exit.clicked.connect(self.exit)
            self.start_cards = []
            for i in self.cur.execute("""SELECT title FROM cards WHERE available = 'true'""").fetchall():
                self.start_cards.append(i[0])

            self.f.seek(0)
            inf = list(map(lambda y: y.strip(), self.f.readlines()))
            self.label.setText(' '.join(inf[inf.index('<') + 1:inf.index('>')]))
            self.f.seek(0)
            self.picture.setPixmap(QPixmap(f"{Main.get_scenario(self)}{self.f.readlines()[-1].strip()}.png"))

            self.label_2.setText('')
            self.label_3.setText('')
            self.bt_1.setText("Далее")
            self.bt_1.clicked.disconnect()
            self.bt_1.clicked.connect(self._continue)
            self.bt_2.setText("Далее")
            self.bt_2.clicked.disconnect()
            self.bt_2.clicked.connect(self._continue)

            self.print_stats()
        except Exception:
            self.error("retry")

    def final_end(self):
        try:
            self.recircle()
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Question)
            msg.setText("Вы уверены?")
            msg.setInformativeText('Кажется вы хотите прекратить играть, мы протестуем, мы требуем, чтобы вы вернулись и сыграли еще раз')
            msg.setWindowTitle("Неееееееет")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msg.buttonClicked.connect(self.msg_click)
            msg.exec_()
        except Exception:
            self.error("final_end")

    def msg_click(self, i):
        if i.text() == "OK":
            Main.interface(Main)
            self.con.close()
            self.close()

    def error(self, mes):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText(mes)
        msg.setInformativeText('Эх, опять воркинг-воркинг')
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.buttonClicked.connect(self.msg_click)
        msg.exec_()

    def exit(self):
        self.recircle()
        self.con.close()
        Main.interface(Main)
        self.close()


class Redactor(QMainWindow, Main):
    def __init__(self):
        try:
            QMainWindow.__init__(self)
            uic.loadUi('redactor.ui', self)

            self.con = sqlite3.connect(Main.get_scenario(self) + "DB.sqlite")
            self.cur = self.con.cursor()

            self.update()

            self.bt_1.clicked.connect(self.exit)
            self.bt_2.clicked.connect(self.delete_card)
            self.bt_3.clicked.connect(self.create_card)
            self.bt_4.clicked.connect(self.delete_descent)
            self.bt_5.clicked.connect(self.update_card)
            self.bt_6.clicked.connect(self.redactor_scenario)

        except Exception:
            self.error("__init__")

    def update(self):
        self.db = QSqlDatabase.addDatabase('QSQLITE')
        self.db.setDatabaseName(Main.get_scenario(self) + 'DB.sqlite')
        self.db.open()

        self.model = QSqlTableModel(self, self.db)
        self.model.setTable('cards')
        self.model.select()
        self.tv_1.setModel(self.model)

        self.model_descent = QSqlTableModel(self, self.db)
        self.model_descent.setTable('descent')
        self.model_descent.select()
        self.tv_2.setModel(self.model_descent)

        self.model_finals = QSqlTableModel(self, self.db)
        self.model_finals.setTable('finals')
        self.model_finals.select()
        self.tv_3.setModel(self.model_finals)

    def create_card(self):
        Main.create_card(Main, None)

    def redactor_scenario(self):
        Main.redactor_scenario(Main, '1')

    def update_card(self):
        try:
            name, ok_pressed = QInputDialog.getText(self, "Изменение карточки",
                                                    "Какую карточку вы хотите изменить? (введите title карточки)")
            if ok_pressed:
                if len(list(self.cur.execute("SELECT title FROM cards WHERE title = ?", (name,)))) != 0:
                    Main.create_card(Main, name)
                    self.con.close()
                    self.close()

        except Exception:
            self.error("udate_card")

    def delete_descent(self):
        name, ok_pressed = QInputDialog.getText(self, "Удаление descent",
                                                "Какой descent вы хотите удалить? (введите id descent)")
        if ok_pressed:
            self.cur.execute("""DELETE FROM descent
                                        WHERE id = ?""", (name,))
            self.con.commit()
            self.update()

    def delete_card(self):
        try:
            name, ok_pressed = QInputDialog.getText(self, "Удаление карточки",
                                                    "Какую карточку вы хотите удалить? (введите title карточки)")
            if ok_pressed:
                self.cur.execute("""DELETE FROM cards
                                WHERE title = ?""", (name,))
                self.con.commit()
                self.update()

        except Exception:
            self.error("delete_card")

    def exit(self):
        Main.interface(Main)
        self.con.close()
        self.close()

    def error(self, mes):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText(mes)
        msg.setInformativeText('Эх, опять воркинг-воркинг')
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.buttonClicked.connect(self.msg_click)
        msg.exec_()

    def msg_click(self, i):
        if i.text() == "OK":
            self.con.close()
            self.close()


class CreateCard(QMainWindow, Main):
    def __init__(self, title):
        QMainWindow.__init__(self)
        uic.loadUi('create_card.ui', self)
        self.con = sqlite3.connect(Main.get_scenario(self) + "DB.sqlite")
        self.cur = self.con.cursor()
        self.cb.addItems(['Да', 'Нет'])
        self.bt.clicked.connect(self.select_picture)
        self.exit.clicked.connect(self._exit)
        self.creat.clicked.connect(self._create)
        self._picture = ''

        if title:
            self.title.setText(title)
            self.event.setText(self.cur.execute("SELECT event FROM cards WHERE title = ?", (title,)).fetchone()[0])
            self.var_1.setText(self.cur.execute("SELECT var_1 FROM cards WHERE title = ?", (title,)).fetchone()[0])
            self.var_2.setText(self.cur.execute("SELECT var_2 FROM cards WHERE title = ?", (title,)).fetchone()[0])
            self.mes_1.setText(self.cur.execute("SELECT mes_1 FROM cards WHERE title = ?", (title,)).fetchone()[0])
            self.mes_2.setText(self.cur.execute("SELECT mes_2 FROM cards WHERE title = ?", (title,)).fetchone()[0])
            self.picture.setPixmap(QPixmap(Main.get_scenario(self) + self.cur.execute("SELECT image FROM cards WHERE title = ?", (title,)).fetchone()[0]))

            self.ch_pop_1.setText(
                str(self.cur.execute("SELECT d_pop_1 FROM cards WHERE title = ?", (title,)).fetchone()[0]))
            self.ch_cor_1.setText(
                str(self.cur.execute("SELECT d_cor_1 FROM cards WHERE title = ?", (title,)).fetchone()[0]))
            self.ch_inf_1.setText(
                str(self.cur.execute("SELECT d_inf_1 FROM cards WHERE title = ?", (title,)).fetchone()[0]))
            self.ch_arm_1.setText(
                str(self.cur.execute("SELECT d_arm_1 FROM cards WHERE title = ?", (title,)).fetchone()[0]))
            self.ch_econ_1.setText(
                str(self.cur.execute("SELECT d_econ_1 FROM cards WHERE title = ?", (title,)).fetchone()[0]))
            self.ch_bud_1.setText(
                str(self.cur.execute("SELECT d_bud_1 FROM cards WHERE title = ?", (title,)).fetchone()[0]))

            self.ch_pop_2.setText(
                str(self.cur.execute("SELECT d_pop_2 FROM cards WHERE title = ?", (title,)).fetchone()[0]))
            self.ch_cor_2.setText(
                str(self.cur.execute("SELECT d_cor_2 FROM cards WHERE title = ?", (title,)).fetchone()[0]))
            self.ch_inf_2.setText(
                str(self.cur.execute("SELECT d_inf_2 FROM cards WHERE title = ?", (title,)).fetchone()[0]))
            self.ch_arm_2.setText(
                str(self.cur.execute("SELECT d_arm_2 FROM cards WHERE title = ?", (title,)).fetchone()[0]))
            self.ch_econ_2.setText(
                str(self.cur.execute("SELECT d_econ_2 FROM cards WHERE title = ?", (title,)).fetchone()[0]))
            self.ch_bud_2.setText(
                str(self.cur.execute("SELECT d_bud_2 FROM cards WHERE title = ?", (title,)).fetchone()[0]))

            self.nec_pop.setText(
                str(self.cur.execute("SELECT nec_pop FROM cards WHERE title = ?", (title,)).fetchone()[0]))
            self.nec_cor.setText(
                str(self.cur.execute("SELECT nec_cor FROM cards WHERE title = ?", (title,)).fetchone()[0]))
            self.nec_inf.setText(
                str(self.cur.execute("SELECT nec_inf FROM cards WHERE title = ?", (title,)).fetchone()[0]))
            self.nec_arm.setText(
                str(self.cur.execute("SELECT nec_arm FROM cards WHERE title = ?", (title,)).fetchone()[0]))
            self.nec_econ.setText(
                str(self.cur.execute("SELECT nec_econ FROM cards WHERE title = ?", (title,)).fetchone()[0]))
            self.nec_bud.setText(
                str(self.cur.execute("SELECT nec_bud FROM cards WHERE title = ?", (title,)).fetchone()[0]))


            _make_av_1 = self.cur.execute("""SELECT * FROM descent WHERE id IN (
                                            SELECT make_av_1 FROM cards WHERE title = ?)""", (title,)).fetchall()[0][1:]
            make_av_1_edits = [self.make_av_1_1, self.make_av_2_1, self.make_av_3_1, self.make_av_4_1]
            for i in range(len(_make_av_1)):
                if _make_av_1[i]:
                    make_av_1_edits[i].setText(_make_av_1[i])

            _make_av_2 = self.cur.execute("""SELECT * FROM descent WHERE id IN (
                                                        SELECT make_av_2 FROM cards WHERE title = ?)""",
                                          (title,)).fetchall()[0][1:]
            make_av_2_edits = [self.make_av_1_2, self.make_av_2_2, self.make_av_3_2, self.make_av_4_2]
            for i in range(len(_make_av_2)):
                if _make_av_2[i]:
                    make_av_2_edits[i].setText(_make_av_2[i])

            _make_un_1 = self.cur.execute("""SELECT * FROM descent WHERE id IN (
                                                        SELECT make_unav_1 FROM cards WHERE title = ?)""",
                                          (title,)).fetchall()[0][1:]
            make_un_1_edits = [self.make_un_1_1, self.make_un_2_1, self.make_un_3_1, self.make_un_4_1]
            for i in range(len(_make_un_1)):
                if _make_un_1[i]:
                    make_un_1_edits[i].setText(_make_un_1[i])

            _make_un_2 = self.cur.execute("""SELECT * FROM descent WHERE id IN (
                                                        SELECT make_unav_2 FROM cards WHERE title = ?)""",
                                          (title,)).fetchall()[0][1:]
            make_un_2_edits = [self.make_un_1_2, self.make_un_2_2, self.make_un_3_2, self.make_un_4_2]
            for i in range(len(_make_un_2)):
                if _make_un_2[i]:
                    make_un_2_edits[i].setText(_make_un_2[i])

    def select_picture(self):
        self._picture = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '')[0][:-4]
        self._picture = '/'.join(self._picture.split('/')[-2:])
        self.picture.setPixmap(QPixmap(Main.get_scenario(self) + self._picture + '.png'))

    def _create(self):
        try:
            _title = self.title.text()
            _event = self.event.text()
            _var_1 = self.var_1.text()
            _var_2 = self.var_2.text()
            _mes_1 = self.mes_1.text()
            _mes_2 = self.mes_2.text()

            _ch_pop_1 = int(self.ch_pop_1.text())
            _ch_cor_1 = int(self.ch_cor_1.text())
            _ch_inf_1 = int(self.ch_inf_1.text())
            _ch_arm_1 = int(self.ch_arm_1.text())
            _ch_econ_1 = int(self.ch_econ_1.text())
            _ch_bud_1 = int(self.ch_bud_1.text())

            _ch_pop_2 = int(self.ch_pop_2.text())
            _ch_cor_2 = int(self.ch_cor_2.text())
            _ch_inf_2 = int(self.ch_inf_2.text())
            _ch_arm_2 = int(self.ch_arm_2.text())
            _ch_econ_2 = int(self.ch_econ_2.text())
            _ch_bud_2 = int(self.ch_bud_2.text())

            _nec_pop = self.nec_pop.text()
            _nec_cor = self.nec_cor.text()
            _nec_inf = self.nec_inf.text()
            _nec_arm = self.nec_arm.text()
            _nec_econ = self.nec_econ.text()
            _nec_bud = self.nec_bud.text()

            _make_av_1_1 = self.make_av_1_1.text()
            _make_av_2_1 = self.make_av_2_1.text()
            _make_av_3_1 = self.make_av_3_1.text()
            _make_av_4_1 = self.make_av_4_1.text()

            _make_av_1_2 = self.make_av_1_2.text()
            _make_av_2_2 = self.make_av_2_2.text()
            _make_av_3_2 = self.make_av_3_2.text()
            _make_av_4_2 = self.make_av_4_2.text()

            _make_un_1_1 = self.make_un_1_1.text()
            _make_un_2_1 = self.make_un_2_1.text()
            _make_un_3_1 = self.make_un_3_1.text()
            _make_un_4_1 = self.make_un_4_1.text()

            _make_un_1_2 = self.make_un_1_2.text()
            _make_un_2_2 = self.make_un_2_2.text()
            _make_un_3_2 = self.make_un_3_2.text()
            _make_un_4_2 = self.make_un_4_2.text()

            for i in [_nec_bud, _nec_econ, _nec_arm, _nec_inf, _nec_cor, _nec_pop]:
                if not i or not (i == '.' or (i[0] in ['>', '<'] and i[1:].isdigit())):
                    raise InvalidInputNecessary

            if self.cb.currentText() == 'Да':
                _available = 'true'
            else:
                _available = 'false'

            if len(list(self.cur.execute("""SELECT title FROM cards WHERE title = ?""", (_title,)))) != 0:
                raise InvalidInputTitle

            _id_1 = list(self.cur.execute("""SELECT id FROM cards"""))[-1][0]
            _id_2 = list(self.cur.execute("""SELECT id FROM descent"""))[-1][0]

            if len(list(filter(lambda x: x == '', [_make_av_1_1, _make_av_2_1, _make_av_3_1, _make_av_4_1]))) == 4:
                _id_1_2 = 0
            else:
                self.cur.execute("""INSERT INTO descent VALUES (?, ?, ?, ?, ?)""",
                                 (_id_2 + 1, _make_av_1_1, _make_av_2_1, _make_av_3_1, _make_av_4_1))
                _id_1_2 = _id_2 + 1

            if len(list(filter(lambda x: x == '', [_make_av_1_2, _make_av_2_2, _make_av_3_2, _make_av_4_2]))) == 4:
                _id_2_2 = 0
            else:
                self.cur.execute("""INSERT INTO descent VALUES (?, ?, ?, ?, ?)""",
                                 (_id_2 + 2, _make_av_1_2, _make_av_2_2, _make_av_3_2, _make_av_4_2))
                _id_2_2 = _id_2 + 2

            if len(list(filter(lambda x: x == '', [_make_un_1_1, _make_un_2_1, _make_un_3_1, _make_un_4_1]))) == 4:
                _id_3_2 = 0
            else:
                self.cur.execute("""INSERT INTO descent VALUES (?, ?, ?, ?, ?)""",
                                 (_id_2 + 3, _make_un_1_1, _make_un_2_1, _make_un_3_1, _make_un_4_1))
                _id_3_2 = _id_2 + 3

            if len(list(filter(lambda x: x == '', [_make_un_1_2, _make_un_2_2, _make_un_3_2, _make_un_4_2]))) == 4:
                _id_4_2 = 0
            else:
                self.cur.execute("""INSERT INTO descent VALUES (?, ?, ?, ?, ?)""",
                                 (_id_2 + 4, _make_un_1_2, _make_un_2_2, _make_un_3_2, _make_un_4_2))
                _id_4_2 = _id_2 + 4

            self.cur.execute(
                """INSERT INTO cards VALUES (?, ?, 'false', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (_id_1 + 1, _available, _title, _event, _var_1, _mes_1, _ch_pop_1, _ch_cor_1, _ch_inf_1,
                 _ch_arm_1, _ch_econ_1, _ch_bud_1, _var_2, _mes_2, _ch_pop_2, _ch_cor_2, _ch_inf_2,
                 _ch_arm_2, _ch_econ_2, _ch_bud_2, _nec_pop, _nec_cor, _nec_inf, _nec_arm, _nec_econ,
                 _nec_bud, _id_1_2, _id_2_2, _id_3_2, _id_4_2, self._picture))

            self.con.commit()
            Main.redactor(Main)
            self.close()

        except ValueError:
            self.msg_error('В качестве изменений характеристик нужно вводить целые числа')

        except InvalidInputNecessary:
            self.msg_error(
                'Требования к характеристикам должны быть либо точкой (это будет означать отсутстве усдовие) либо иметь ввид ">/< {целое число}"')

        except InvalidInputTitle:
            self.msg_title()

    def msg_error(self, where):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Ошибка в вводе данных")
        msg.setInformativeText(where)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def msg_title(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText("Уже существует карточка с таким названием")
        msg.setInformativeText("")
        msg.setWindowTitle("Information")
        msg.setStandardButtons(QMessageBox.Ok|QMessageBox.Cancel)
        msg.buttonClicked.connect(self.msg_click)
        msg.exec_()

    def msg_click(self, i):
        if i.text() == 'OK':
            try:
                _title = self.title.text()
                _event = self.event.text()
                _var_1 = self.var_1.text()
                _var_2 = self.var_2.text()
                _mes_1 = self.mes_1.text()
                _mes_2 = self.mes_2.text()

                _ch_pop_1 = int(self.ch_pop_1.text())
                _ch_cor_1 = int(self.ch_cor_1.text())
                _ch_inf_1 = int(self.ch_inf_1.text())
                _ch_arm_1 = int(self.ch_arm_1.text())
                _ch_econ_1 = int(self.ch_econ_1.text())
                _ch_bud_1 = int(self.ch_bud_1.text())

                _ch_pop_2 = int(self.ch_pop_2.text())
                _ch_cor_2 = int(self.ch_cor_2.text())
                _ch_inf_2 = int(self.ch_inf_2.text())
                _ch_arm_2 = int(self.ch_arm_2.text())
                _ch_econ_2 = int(self.ch_econ_2.text())
                _ch_bud_2 = int(self.ch_bud_2.text())

                _nec_pop = self.nec_pop.text()
                _nec_cor = self.nec_cor.text()
                _nec_inf = self.nec_inf.text()
                _nec_arm = self.nec_arm.text()
                _nec_econ = self.nec_econ.text()
                _nec_bud = self.nec_bud.text()

                _make_av_1_1 = self.make_av_1_1.text()
                _make_av_2_1 = self.make_av_2_1.text()
                _make_av_3_1 = self.make_av_3_1.text()
                _make_av_4_1 = self.make_av_4_1.text()

                _make_av_1_2 = self.make_av_1_2.text()
                _make_av_2_2 = self.make_av_2_2.text()
                _make_av_3_2 = self.make_av_3_2.text()
                _make_av_4_2 = self.make_av_4_2.text()

                _make_un_1_1 = self.make_un_1_1.text()
                _make_un_2_1 = self.make_un_2_1.text()
                _make_un_3_1 = self.make_un_3_1.text()
                _make_un_4_1 = self.make_un_4_1.text()

                _make_un_1_2 = self.make_un_1_2.text()
                _make_un_2_2 = self.make_un_2_2.text()
                _make_un_3_2 = self.make_un_3_2.text()
                _make_un_4_2 = self.make_un_4_2.text()

                for i in [_nec_bud, _nec_econ, _nec_arm, _nec_inf, _nec_cor, _nec_pop]:
                    if not (i == '.' or (i[0] in ['>', '<'] and i[1:].isdigit())):
                        raise InvalidInputNecessary

                if self.cb.currentText() == 'Да':
                    _available = 'true'
                else:
                    _available = 'false'

                _id_1 = list(self.cur.execute("""SELECT id FROM cards"""))[-1][0]
                _id_2 = list(self.cur.execute("""SELECT id FROM descent"""))[-1][0]

                if len(list(filter(lambda x: x == '', [_make_av_1_1, _make_av_2_1, _make_av_3_1, _make_av_4_1]))) == 4:
                    _id_1_2 = 0
                else:
                    self.cur.execute("""INSERT INTO descent VALUES (?, ?, ?, ?, ?)""",
                                     (_id_2 + 1, _make_av_1_1, _make_av_2_1, _make_av_3_1, _make_av_4_1))
                    _id_1_2 = _id_2 + 1

                if len(list(filter(lambda x: x == '', [_make_av_1_2, _make_av_2_2, _make_av_3_2, _make_av_4_2]))) == 4:
                    _id_2_2 = 0
                else:
                    self.cur.execute("""INSERT INTO descent VALUES (?, ?, ?, ?, ?)""",
                                     (_id_2 + 2, _make_av_1_2, _make_av_2_2, _make_av_3_2, _make_av_4_2))
                    _id_2_2 = _id_2 + 2

                if len(list(filter(lambda x: x == '', [_make_un_1_1, _make_un_2_1, _make_un_3_1, _make_un_4_1]))) == 4:
                    _id_3_2 = 0
                else:
                    self.cur.execute("""INSERT INTO descent VALUES (?, ?, ?, ?, ?)""",
                                     (_id_2 + 3, _make_un_1_1, _make_un_2_1, _make_un_3_1, _make_un_4_1))
                    _id_3_2 = _id_2 + 3

                if len(list(filter(lambda x: x == '', [_make_un_1_2, _make_un_2_2, _make_un_3_2, _make_un_4_2]))) == 4:
                    _id_4_2 = 0
                else:
                    self.cur.execute("""INSERT INTO descent VALUES (?, ?, ?, ?, ?)""",
                                     (_id_2 + 4, _make_un_1_2, _make_un_2_2, _make_un_3_2, _make_un_4_2))
                    _id_4_2 = _id_2 + 4

                self.cur.execute("""DELETE FROM cards WHERE title = ?""", (_title,))
                self.cur.execute(
                    """INSERT INTO cards VALUES (?, ?, 'false', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (_id_1 + 1, _available, _title, _event, _var_1, _mes_1, _ch_pop_1, _ch_cor_1, _ch_inf_1,
                     _ch_arm_1, _ch_econ_1, _ch_bud_1, _var_2, _mes_2, _ch_pop_2, _ch_cor_2, _ch_inf_2,
                     _ch_arm_2, _ch_econ_2, _ch_bud_2, _nec_pop, _nec_cor, _nec_inf, _nec_arm, _nec_econ,
                     _nec_bud, _id_1_2, _id_2_2, _id_3_2, _id_4_2, self._picture))

                self.con.commit()
                Main.redactor(Main)
                self.close()

            except Exception:
                self.msg_error('Что-то пошло не так')

    def _exit(self):
        self.con.close()
        Main.redactor(Main)
        self.close()


class RedactorScenario(QMainWindow, Main):
    def __init__(self, scenario):
        self._scenario = scenario
        QMainWindow.__init__(self)
        uic.loadUi('redactor_scenario.ui', self)
        self.name_of_stats = [self.le_1, self.le_2, self.le_3, self.le_4, self.le_5, self.le_6]
        self.stats = [self.le_7, self.le_8, self.le_9, self.le_10, self.le_11, self.le_12]
        self.titles_of_finals = [self.edit_title_of_final_1, self.edit_title_of_final_2, self.edit_title_of_final_3,
                                 self.edit_title_of_final_4, self.edit_title_of_final_5, self.edit_title_of_final_6]
        self.events_of_finals = [self.edit_event_of_final_1, self.edit_event_of_final_2, self.edit_event_of_final_3,
                                 self.edit_event_of_final_4, self.edit_event_of_final_5, self.edit_event_of_final_6]
        self.conditions_of_finals = [self.edit_condition_of_final_1, self.edit_condition_of_final_2, self.edit_condition_of_final_3,
                                     self.edit_condition_of_final_4, self.edit_condition_of_final_5, self.edit_condition_of_final_6]
        self.finals_pictures = [self.final_picture_1, self.final_picture_2, self.final_picture_3, self.final_picture_4,
                               self.final_picture_5, self.final_picture_6]
        self.exit.clicked.connect(self._exit_2)
        self.save.clicked.connect(self._create)
        self.pictures = {self.select_picture: self.start_picture, self.select_picture_of_finals_1: self.final_picture_1,
                         self.select_picture_of_finals_2: self.final_picture_2, self.select_picture_of_finals_3: self.final_picture_3,
                         self.select_picture_of_finals_4: self.final_picture_4, self.select_picture_of_finals_5: self.final_picture_5,
                         self.select_picture_of_finals_6: self.final_picture_6}
        for i in self.pictures:
            i.clicked.connect(self._select_picture)

        if scenario:
            self.exit.clicked.connect(self._exit_1)
            self.f = open(Main.get_scenario(self) + "information.txt", encoding="utf-8")
            self.con = sqlite3.connect(Main.get_scenario(self) + "DB.sqlite")
            self.cur = self.con.cursor()
            self.edit_name.setText(self.f.readline())
            self.f.seek(0)
            self.start_picture.setText(self.f.readlines()[-1].strip())

            for i in range(len(self.name_of_stats)):
                self.f.seek(0)
                self.name_of_stats[i].setText(self.f.readlines()[1].strip().split('|')[i])

            for i in range(len(self.stats)):
                self.f.seek(0)
                self.stats[i].setText(self.f.readlines()[2].strip().split('|')[i])

            self.f.seek(0)
            inf = list(map(lambda y: y.strip(), self.f.readlines()))
            self.edit_start_event.setText(' '.join(inf[inf.index('<') + 1:inf.index('>')]))

            self.f.seek(0)
            self.start_picture.setText(inf[inf.index('>') + 1])

            for i in range(1, 7):
                self.titles_of_finals[i - 1].setText(self.cur.execute("""SELECT title FROM finals
                                                                        WHERE id = ?""", (i,)).fetchone()[0])

            for i in range(1, 7):
                self.events_of_finals[i - 1].setText(self.cur.execute("""SELECT event FROM finals
                                                                        WHERE id = ?""", (i,)).fetchone()[0])

            for i in range(1, 7):
                self.conditions_of_finals[i - 1].setText(self.cur.execute("""SELECT condition FROM finals
                                                                        WHERE id = ?""", (i,)).fetchone()[0])

            for i in range(1, 7):
                self.finals_pictures[i - 1].setText(self.cur.execute("""SELECT image FROM finals
                                                                                        WHERE id = ?""",
                                                                          (i,)).fetchone()[0])

    def _select_picture(self):
        self._select_picture = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '')[0]
        self._select_picture = '/'.join(self._select_picture.split('/')[-2:])[:-4]
        self.pictures[self.sender()].setText(self._select_picture)

    def _create(self):
        try:
            if not self.edit_name.text():
                raise EmptyInput
            for i in self.stats + self.name_of_stats + self.titles_of_finals + self.events_of_finals + self.conditions_of_finals:
                if not i:
                    raise EmptyInput
            if not self._scenario:
                if os.path.exists(self.edit_name.text()):
                    shutil.rmtree(self.edit_name.text())

                os.mkdir(self.edit_name.text())
                os.mkdir(f"{self.edit_name.text()}\pictures")
                self.con = sqlite3.connect(self.edit_name.text() + '/' + "DB.sqlite")
                self.cur = self.con.cursor()
                self.cur.execute("""CREATE TABLE descent (
                                    id INTEGER PRIMARY KEY,
                                    card_1 TEXT,
                                    card_2 TEXT,
                                    card_3 TEXT,
                                    card_4 TEXT)""")
                self.cur.execute("""CREATE TABLE finals (
                                    id INTEGER PRIMARY KEY,
                                    title TEXT,
                                    event TEXT,
                                    condition TEXT,
                                    image TEXT)""")
                self.cur.execute("""CREATE TABLE cards (
                                    id INTEGER PRIMARY KEY,
                                    available TEXT,
                                    on_table TEXT,
                                    title TEXT,
                                    event TEXT,
                                    var_1 TEXT,
                                    mes_1 TEXT,
                                    d_pop_1 TEXT,
                                    d_cor_1 TEXT,
                                    d_inf_1 TEXT,
                                    d_arm_1 TEXT,
                                    d_econ_1 TEXT,
                                    d_bud_1 TEXT,
                                    var_2 TEXT,
                                    mes_2 TEXT,
                                    d_pop_2 TEXT,
                                    d_cor_2 TEXT,
                                    d_inf_2 TEXT,
                                    d_arm_2 TEXT,
                                    d_econ_2 TEXT,
                                    d_bud_2 TEXT,
                                    nec_pop TEXT,
                                    nec_cor TEXT,
                                    nec_inf TEXT,
                                    nec_arm TEXT,
                                    nec_econ TEXT,
                                    nec_bud TEXT,
                                    make_av_1 INT,
                                    make_unav_1 INT,
                                    make_av_2 INT,
                                    make_unav_2 INT,
                                    image TEXT)""")
                for i in range(6):
                    self.con.execute("""INSERT INTO finals VALUES (?, '-', '-', '-', '-')""", (i + 1,))

                self.f = open(self.edit_name.text() + '/' + "information.txt", 'w+', encoding="utf-8")

            else:
                self.f = open(Main.get_scenario(self) + "information.txt", 'w+', encoding="utf-8")

            for i in self.conditions_of_finals:
                if not i.text() or not (i.text()[0] in ['>', '<'] and i.text()[1:].isdigit()):
                    raise InvalidInputNecessary
            self.f.write(self.edit_name.text() + '\n')
            self.f.write('|'.join([i.text() for i in self.name_of_stats]) + '\n')
            for i in self.stats:
                int(i.text())
            self.f.write('|'.join([i.text() for i in self.stats]) + '\n')
            self.f.write('<' + '\n')
            self.f.write(self.edit_start_event.text() + '\n')
            self.f.write('>' + '\n')
            self.f.write(self.start_picture.text() + '\n')
            self.f.close()

            for i in range(6):
                self.cur.execute("""UPDATE finals
                                    SET title = ? WHERE id = ?""", (self.titles_of_finals[i].text(), i + 1))
                self.cur.execute("""UPDATE finals
                                   SET event = ? WHERE id = ?""", (self.events_of_finals[i].text(), i + 1))
                self.cur.execute("""UPDATE finals
                                    SET condition = ? WHERE id = ?""", (self.conditions_of_finals[i].text(), i + 1))
                self.cur.execute("""UPDATE finals
                                    SET image = ? WHERE id = ?""", (self.finals_pictures[i].text(), i + 1))
            self.con.commit()
            Main.set_scenario(Main, self.edit_name.text())
            Main.redactor(Main)
            self.con.close()
            self.close()

        except InvalidInputNecessary:
            self.msg_error('Условия должы иметь вид ">/< {число типа int}"')

        except ValueError:
            self.msg_error('Начальные значениями характристик должны быть числа типа int')

        except EmptyInput:
            self.msg_error('Все поля должны быть заполнены')

        except Exception:
            self.msg_error('Ошибка')

    def msg_error(self, where):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Ошибка в вводе данных")
        msg.setInformativeText(where)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def msg_click(self, i):
        if i.text() == 'OK':
            try:
                _title = self.title.text()
                _event = self.event.text()
                _var_1 = self.var_1.text()
                _var_2 = self.var_2.text()
                _mes_1 = self.mes_1.text()
                _mes_2 = self.mes_2.text()

                _ch_pop_1 = int(self.ch_pop_1.text())
                _ch_cor_1 = int(self.ch_cor_1.text())
                _ch_inf_1 = int(self.ch_inf_1.text())
                _ch_arm_1 = int(self.ch_arm_1.text())
                _ch_econ_1 = int(self.ch_econ_1.text())
                _ch_bud_1 = int(self.ch_bud_1.text())

                _ch_pop_2 = int(self.ch_pop_2.text())
                _ch_cor_2 = int(self.ch_cor_2.text())
                _ch_inf_2 = int(self.ch_inf_2.text())
                _ch_arm_2 = int(self.ch_arm_2.text())
                _ch_econ_2 = int(self.ch_econ_2.text())
                _ch_bud_2 = int(self.ch_bud_2.text())

                _nec_pop = self.nec_pop.text()
                _nec_cor = self.nec_cor.text()
                _nec_inf = self.nec_inf.text()
                _nec_arm = self.nec_arm.text()
                _nec_econ = self.nec_econ.text()
                _nec_bud = self.nec_bud.text()

                _make_av_1_1 = self.make_av_1_1.text()
                _make_av_2_1 = self.make_av_2_1.text()
                _make_av_3_1 = self.make_av_3_1.text()
                _make_av_4_1 = self.make_av_4_1.text()

                _make_av_1_2 = self.make_av_1_2.text()
                _make_av_2_2 = self.make_av_2_2.text()
                _make_av_3_2 = self.make_av_3_2.text()
                _make_av_4_2 = self.make_av_4_2.text()

                _make_un_1_1 = self.make_un_1_1.text()
                _make_un_2_1 = self.make_un_2_1.text()
                _make_un_3_1 = self.make_un_3_1.text()
                _make_un_4_1 = self.make_un_4_1.text()

                _make_un_1_2 = self.make_un_1_2.text()
                _make_un_2_2 = self.make_un_2_2.text()
                _make_un_3_2 = self.make_un_3_2.text()
                _make_un_4_2 = self.make_un_4_2.text()

                for i in [_nec_bud, _nec_econ, _nec_arm, _nec_inf, _nec_cor, _nec_pop]:
                    if not (i == '.' or (i[0] in ['>', '<'] and i[1:].isdigit())):
                        raise InvalidInputNecessary

                if self.cb.currentText() == 'Да':
                    _available = 'true'
                else:
                    _available = 'false'

                _id_1 = list(self.cur.execute("""SELECT id FROM cards"""))[-1][0]
                _id_2 = list(self.cur.execute("""SELECT id FROM descent"""))[-1][0]

                if len(list(filter(lambda x: x == '', [_make_av_1_1, _make_av_2_1, _make_av_3_1, _make_av_4_1]))) == 4:
                    _id_1_2 = 0
                else:
                    self.cur.execute("""INSERT INTO descent VALUES (?, ?, ?, ?, ?)""",
                                     (_id_2 + 1, _make_av_1_1, _make_av_2_1, _make_av_3_1, _make_av_4_1))
                    _id_1_2 = _id_2 + 1

                if len(list(filter(lambda x: x == '', [_make_av_1_2, _make_av_2_2, _make_av_3_2, _make_av_4_2]))) == 4:
                    _id_2_2 = 0
                else:
                    self.cur.execute("""INSERT INTO descent VALUES (?, ?, ?, ?, ?)""",
                                     (_id_2 + 2, _make_av_1_2, _make_av_2_2, _make_av_3_2, _make_av_4_2))
                    _id_2_2 = _id_2 + 2

                if len(list(filter(lambda x: x == '', [_make_un_1_1, _make_un_2_1, _make_un_3_1, _make_un_4_1]))) == 4:
                    _id_3_2 = 0
                else:
                    self.cur.execute("""INSERT INTO descent VALUES (?, ?, ?, ?, ?)""",
                                     (_id_2 + 3, _make_un_1_1, _make_un_2_1, _make_un_3_1, _make_un_4_1))
                    _id_3_2 = _id_2 + 3

                if len(list(filter(lambda x: x == '', [_make_un_1_2, _make_un_2_2, _make_un_3_2, _make_un_4_2]))) == 4:
                    _id_4_2 = 0
                else:
                    self.cur.execute("""INSERT INTO descent VALUES (?, ?, ?, ?, ?)""",
                                     (_id_2 + 4, _make_un_1_2, _make_un_2_2, _make_un_3_2, _make_un_4_2))
                    _id_4_2 = _id_2 + 4

                self.cur.execute("""DELETE FROM cards WHERE title = ?""", (_title,))
                self.cur.execute(
                    """INSERT INTO cards VALUES (?, ?, 'false', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (_id_1 + 1, _available, _title, _event, _var_1, _mes_1, _ch_pop_1, _ch_cor_1, _ch_inf_1,
                     _ch_arm_1, _ch_econ_1, _ch_bud_1, _var_2, _mes_2, _ch_pop_2, _ch_cor_2, _ch_inf_2,
                     _ch_arm_2, _ch_econ_2, _ch_bud_2, _nec_pop, _nec_cor, _nec_inf, _nec_arm, _nec_econ,
                     _nec_bud, _id_1_2, _id_2_2, _id_3_2, _id_4_2, self._picture))

                self.con.commit()
                Main.redactor(Main)
                self.close()

            except Exception:
                self.msg_error('Что-то пошло не так')

    def _exit_1(self):
        self.con.close()
        Main.redactor(Main)
        self.close()

    def _exit_2(self):
        Main.start(Main)
        self.close()


class Interface(QMainWindow, Main):
    def __init__(self):
        QMainWindow.__init__(self)
        uic.loadUi('interface.ui', self)
        self.bt_1.clicked.connect(self.start_game)
        self.bt_2.clicked.connect(self._close)
        self.bt_3.clicked.connect(self.open_redactor)

    def start_game(self):
        try:
            Main.open_game(Main)
        except Exception:
            self.error("start_game")

    def _close(self):
        self.close()

    def open_redactor(self):
        try:
            Main.redactor(Main)
        except Exception:
            self.error("open_redactor")

    def error(self, mes):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText(mes)
        msg.setInformativeText('Эх, опять воркинг-воркинг')
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.buttonClicked.connect(self.msg_click)
        msg.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    a = Main()
    a.start()
    sys.exit(app.exec_())
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QDialog
)
from PyQt5.QtCore import Qt
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuración de SQLAlchemy
Base = declarative_base()
engine = create_engine("sqlite:///gestor_contrasenas_sqlalchemy.db")
Session = sessionmaker(bind=engine)
session = Session()


class Contrasena(Base):
    __tablename__ = 'contrasenas'
    id = Column(Integer, primary_key=True)
    servicio = Column(String, nullable=False)
    usuario = Column(String, nullable=False)
    contrasena = Column(String, nullable=False)


# Crear las tablas si no existen
Base.metadata.create_all(engine)


class InicioSesion(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inicio de Sesión")
        self.resize(400, 250)
        self.centrar_ventana()
        self.setup_ui()

    def centrar_ventana(self):
        qr = self.frameGeometry()
        cp = QApplication.desktop().screenGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def setup_ui(self):
        layout = QVBoxLayout()

        self.usuario_input = QLineEdit()
        self.usuario_input.setPlaceholderText("Usuario")
        self.contrasena_input = QLineEdit()
        self.contrasena_input.setPlaceholderText("Contraseña")
        self.contrasena_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Iniciar Sesión")
        self.login_button.setFixedSize(200, 50)
        self.login_button.setStyleSheet(
            "background-color: #4CAF50; color: white; font-size: 16px; border-radius: 10px;")
        self.login_button.clicked.connect(self.validar_credenciales)

        layout.addWidget(self.usuario_input)
        layout.addWidget(self.contrasena_input)
        layout.addWidget(self.login_button)
        self.setLayout(layout)

    def validar_credenciales(self):
        usuario = self.usuario_input.text()
        contrasena = self.contrasena_input.text()

        if usuario == "papita123" and contrasena == "camote123":
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Usuario o contraseña incorrectos.")


class GestorContrasenas(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestor de Contraseñas")
        self.resize(900, 600)
        self.centrar_ventana()
        self.setup_ui()

    def centrar_ventana(self):
        qr = self.frameGeometry()
        cp = QApplication.desktop().screenGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def setup_ui(self):
        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Servicio", "Usuario", "Contraseña"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        button_layout = QHBoxLayout()
        self.add_button = self.crear_boton("Añadir", "#4CAF50", self.abrir_ventana_anadir)
        self.edit_button = self.crear_boton("Editar", "#2196F3", self.abrir_ventana_editar)
        self.delete_button = self.crear_boton("Eliminar", "#F44336", self.eliminar_contrasena)
        self.show_password_button = self.crear_boton("Mostrar Contraseña", "#FFC107", self.mostrar_contrasena)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.show_password_button)

        layout.addWidget(self.table)
        layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.listar_contrasenas()

    def crear_boton(self, texto, color, funcion):
        boton = QPushButton(texto)
        boton.setFixedSize(200, 50)
        boton.setStyleSheet(f"background-color: {color}; color: white; font-size: 16px; border-radius: 10px;")
        boton.clicked.connect(funcion)
        return boton

    def listar_contrasenas(self):
        contrasenas = session.query(Contrasena).all()
        self.table.setRowCount(len(contrasenas))
        for row_idx, contrasena in enumerate(contrasenas):
            self.table.setItem(row_idx, 0, QTableWidgetItem(contrasena.servicio))
            self.table.setItem(row_idx, 1, QTableWidgetItem(contrasena.usuario))
            self.table.setItem(row_idx, 2, QTableWidgetItem("******"))  # Ocultar contraseña

    def mostrar_contrasena(self):
        selected_row = self.table.currentRow()
        if selected_row != -1:
            id_contrasena = session.query(Contrasena).all()[selected_row].id
            contrasena = session.query(Contrasena).filter(Contrasena.id == id_contrasena).first().contrasena
            autenticado = self.autenticar_usuario()
            if autenticado:
                QMessageBox.information(self, "Contraseña", f"La contraseña es: {contrasena}")
        else:
            QMessageBox.warning(self, "Error", "Selecciona una fila para mostrar la contraseña.")

    def autenticar_usuario(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Autenticación Administrador")
        layout = QVBoxLayout()

        usuario_input = QLineEdit()
        usuario_input.setPlaceholderText("Usuario Administrador")
        contrasena_input = QLineEdit()
        contrasena_input.setPlaceholderText("Contraseña")
        contrasena_input.setEchoMode(QLineEdit.Password)

        confirmar_button = QPushButton("Confirmar")
        confirmar_button.clicked.connect(dialog.accept)

        layout.addWidget(usuario_input)
        layout.addWidget(contrasena_input)
        layout.addWidget(confirmar_button)
        dialog.setLayout(layout)

        if dialog.exec() == QDialog.Accepted:
            usuario = usuario_input.text()
            contrasena = contrasena_input.text()
            return usuario == "papita123" and contrasena == "camote123"
        return False

    def abrir_ventana_anadir(self):
        self.anadir_window = VentanaAnadir(self)
        self.anadir_window.show()

    def abrir_ventana_editar(self):
        selected_row = self.table.currentRow()
        if selected_row != -1:
            id_contrasena = session.query(Contrasena).all()[selected_row].id
            self.editar_window = VentanaEditar(self, id_contrasena)
            self.editar_window.show()
        else:
            QMessageBox.warning(self, "Error", "Selecciona una fila para editar.")

    def eliminar_contrasena(self):
        selected_row = self.table.currentRow()
        if selected_row != -1:
            autenticado = self.autenticar_usuario()
            if autenticado:
                id_contrasena = session.query(Contrasena).all()[selected_row].id
                confirm = QMessageBox.question(
                    self, "Confirmar", "¿Estás seguro de eliminar esta contraseña?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if confirm == QMessageBox.Yes:
                    session.query(Contrasena).filter(Contrasena.id == id_contrasena).delete()
                    session.commit()
                    QMessageBox.information(self, "Éxito", "Contraseña eliminada con éxito.")
                    self.listar_contrasenas()
        else:
            QMessageBox.warning(self, "Error", "Selecciona una fila para eliminar.")


class VentanaAnadir(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Añadir Contraseña")
        self.resize(400, 250)
        self.centrar_ventana()
        self.setup_ui()

    def centrar_ventana(self):
        qr = self.frameGeometry()
        cp = QApplication.desktop().screenGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def setup_ui(self):
        layout = QVBoxLayout()
        self.servicio_input = QLineEdit()
        self.servicio_input.setPlaceholderText("Servicio")
        self.usuario_input = QLineEdit()
        self.usuario_input.setPlaceholderText("Usuario")
        self.contrasena_input = QLineEdit()
        self.contrasena_input.setPlaceholderText("Contraseña")
        self.contrasena_input.setEchoMode(QLineEdit.Password)  # Ocultar contraseña

        self.add_button = QPushButton("Guardar")
        self.add_button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 14px;")
        self.add_button.clicked.connect(self.anadir_contrasena)

        layout.addWidget(self.servicio_input)
        layout.addWidget(self.usuario_input)
        layout.addWidget(self.contrasena_input)
        layout.addWidget(self.add_button)
        self.setLayout(layout)

    def anadir_contrasena(self):
        servicio = self.servicio_input.text()
        usuario = self.usuario_input.text()
        contrasena = self.contrasena_input.text()

        if servicio and usuario and contrasena:
            nueva_contrasena = Contrasena(servicio=servicio, usuario=usuario, contrasena=contrasena)
            session.add(nueva_contrasena)
            session.commit()
            QMessageBox.information(self, "Éxito", "Contraseña añadida con éxito.")
            self.parent().listar_contrasenas()
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Por favor, llena todos los campos.")


class VentanaEditar(QDialog):
    def __init__(self, parent, id_contrasena):
        super().__init__(parent)
        self.setWindowTitle("Editar Contraseña")
        self.resize(400, 250)
        self.id_contrasena = id_contrasena
        self.centrar_ventana()
        self.setup_ui()
        self.cargar_datos()

    def centrar_ventana(self):
        qr = self.frameGeometry()
        cp = QApplication.desktop().screenGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def setup_ui(self):
        layout = QVBoxLayout()
        self.servicio_input = QLineEdit()
        self.servicio_input.setPlaceholderText("Servicio")
        self.usuario_input = QLineEdit()
        self.usuario_input.setPlaceholderText("Usuario")
        self.contrasena_input = QLineEdit()
        self.contrasena_input.setPlaceholderText("Contraseña")
        self.contrasena_input.setEchoMode(QLineEdit.Password)  # Ocultar contraseña

        self.save_button = QPushButton("Guardar")
        self.save_button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 14px;")
        self.save_button.clicked.connect(self.editar_contrasena)

        layout.addWidget(self.servicio_input)
        layout.addWidget(self.usuario_input)
        layout.addWidget(self.contrasena_input)
        layout.addWidget(self.save_button)
        self.setLayout(layout)

    def cargar_datos(self):
        contrasena = session.query(Contrasena).filter(Contrasena.id == self.id_contrasena).first()
        self.servicio_input.setText(contrasena.servicio)
        self.usuario_input.setText(contrasena.usuario)
        self.contrasena_input.setText(contrasena.contrasena)

    def editar_contrasena(self):
        servicio = self.servicio_input.text()
        usuario = self.usuario_input.text()
        contrasena = self.contrasena_input.text()

        if servicio and usuario and contrasena:
            contrasena_obj = session.query(Contrasena).filter(Contrasena.id == self.id_contrasena).first()
            contrasena_obj.servicio = servicio
            contrasena_obj.usuario = usuario
            contrasena_obj.contrasena = contrasena
            session.commit()
            QMessageBox.information(self, "Éxito", "Contraseña editada con éxito.")
            self.parent().listar_contrasenas()
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Por favor, llena todos los campos.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = InicioSesion()
    if login.exec() == QDialog.Accepted:
        gestor = GestorContrasenas()
        gestor.show()
        sys.exit(app.exec())


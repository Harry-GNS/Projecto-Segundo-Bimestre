import os
import sys
from datetime import datetime
from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QPlainTextEdit,
    QFileDialog,
    QLabel,
    QLineEdit,
    QSplitter,
    QMessageBox,
    QStatusBar,
    QComboBox,
)

from parser import analizar_pseudocodigo
from generator import generar_lmc
from utils import escribir_texto, asegurar_directorio


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Transpilador LMC")
        self.resize(1000, 600)

        self.current_input_path: Optional[str] = None

        # Top controls
        self.load_btn = QPushButton("Cargar .txt")
        self.load_btn.clicked.connect(self.cargar_archivo)

        self.output_name_edit = QLineEdit()
        self.output_name_edit.setPlaceholderText("Nombre de salida (sin extensión)")

        self.generate_btn = QPushButton("Generar LMC")
        self.generate_btn.setDefault(True)
        self.generate_btn.clicked.connect(self.generar)

        # Destino de guardado
        self.dest_combo = QComboBox()
        self.dest_combo.addItems(["Harry", "Juan", "Anthony", "Luis"])

        top_bar = QHBoxLayout()
        top_bar.addWidget(self.load_btn)
        top_bar.addWidget(QLabel("Nombre salida:"))
        top_bar.addWidget(self.output_name_edit, stretch=1)
        top_bar.addWidget(QLabel("Guardar en:"))
        top_bar.addWidget(self.dest_combo)
        top_bar.addWidget(self.generate_btn)

        # Editors in splitter
        self.input_edit = QPlainTextEdit()
        self.input_edit.setPlaceholderText("Escribe tu pseudo-código aquí o carga un archivo .txt...")
        self.output_edit = QPlainTextEdit()
        self.output_edit.setReadOnly(True)
        self.output_edit.setPlaceholderText("Código LMC generado")

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.input_edit)
        splitter.addWidget(self.output_edit)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        # Layout
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.addLayout(top_bar)
        layout.addWidget(splitter)
        self.setCentralWidget(root)

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)

    def raiz_proyecto(self) -> str:
        return os.path.dirname(os.path.dirname(__file__))

    def carpeta_salida(self) -> str:
        # Carpeta seleccionada por el usuario (Harry/Juan/Anthony/Luis) dentro de output_lmc
        dest = self.dest_combo.currentText()
        return os.path.join(self.raiz_proyecto(), "output_lmc", dest)

    def cargar_archivo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Selecciona .txt", self.raiz_proyecto(), "Text Files (*.txt);;All Files (*.*)")
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.input_edit.setPlainText(content)
            self.current_input_path = path
            base = os.path.splitext(os.path.basename(path))[0]
            self.output_name_edit.setText(base)
            self.status.showMessage(f"Cargado: {path}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el archivo:\n{e}")

    def generar(self):
        text = self.input_edit.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Vacío", "Ingresa pseudo-código o carga un archivo.")
            return
        try:
            lines = text.splitlines()
            ops = analizar_pseudocodigo(lines)
            lmc = generar_lmc(ops)
            self.output_edit.setPlainText(lmc)

            asegurar_directorio(self.carpeta_salida())
            # Determine output name
            base = self.output_name_edit.text().strip()
            if not base:
                if self.current_input_path:
                    base = os.path.splitext(os.path.basename(self.current_input_path))[0]
                else:
                    base = f"manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            out_path = os.path.join(self.carpeta_salida(), f"{base}.lmc")

            escribir_texto(out_path, lmc)
            self.status.showMessage(f"Generado y guardado en: {out_path}", 5000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al generar LMC:\n{e}")


def run():
    app = QApplication(sys.argv)
    # Use Fusion style for a clean look
    app.setStyle("Fusion")
    win = VentanaPrincipal()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run()

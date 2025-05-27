from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox, QMessageBox
from core.niko_client import Settings

class SettingsDialog(QDialog):
    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.settings = Settings(niko_ip=settings.niko_ip)  # Copy to avoid mutating original
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Niko Controller IP:"))
        self.ip_edit = QLineEdit(self.settings.niko_ip)
        layout.addWidget(self.ip_edit)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def accept(self):
        ip = self.ip_edit.text().strip()
        if not ip:
            QMessageBox.warning(self, "Invalid", "IP address cannot be empty.")
            return
        self.settings.niko_ip = ip
        super().accept()

    def get_settings(self) -> Settings:
        return self.settings
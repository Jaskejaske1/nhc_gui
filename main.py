import sys
from PySide6.QtWidgets import QApplication
from controller.app_controller import AppController
from ui.mainwindow import MainWindow
from core.niko_client import Settings

# ---- Set IP of your Niko controller here ----
NIKO_IP = "192.168.111.16"

def main():
    app = QApplication(sys.argv)
    settings = Settings(niko_ip=NIKO_IP)
    controller = AppController(settings)
    win = MainWindow(controller)
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
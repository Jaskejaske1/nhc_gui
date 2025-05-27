from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QListWidget, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QListWidgetItem, QMessageBox, QInputDialog, QSlider, QDialog,
    QDialogButtonBox
)
from PySide6.QtCore import Qt, QTimer
from controller.app_controller import AppController, NikoDevice, NikoLocation, NikoError
from ui.settingsdialog import SettingsDialog

class BrightnessDialog(QDialog):
    def __init__(self, device: NikoDevice, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Set Brightness - {device.name}")
        self.setMinimumWidth(320)
        layout = QVBoxLayout(self)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(100)
        # Map existing value1 (0-255) to 0-100 scale for UI
        initial = int((int(device.value1) if device.value1 else 100) * 100 / 255)
        self.slider.setValue(initial if initial > 0 else 100)
        layout.addWidget(QLabel("Select brightness:"))
        layout.addWidget(self.slider)

        self.value_label = QLabel(f"{self.slider.value()}%")
        layout.addWidget(self.value_label)
        self.slider.valueChanged.connect(self._update_label)

        btn_layout = QHBoxLayout()
        self.on_button = QPushButton("ON (100%)")
        self.off_button = QPushButton("OFF (0%)")
        btn_layout.addWidget(self.on_button)
        btn_layout.addWidget(self.off_button)
        layout.addLayout(btn_layout)

        self.on_button.clicked.connect(self._on_on)
        self.off_button.clicked.connect(self._on_off)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._result_value = None

    def _update_label(self, value):
        self.value_label.setText(f"{value}%")

    def _on_on(self):
        self.slider.setValue(100)
        self._result_value = 100
        self.accept()

    def _on_off(self):
        self.slider.setValue(0)
        self._result_value = 0
        self.accept()

    def get_brightness(self):
        # If ON/OFF was pressed, return that; else slider value
        return self._result_value if self._result_value is not None else self.slider.value()


class MainWindow(QMainWindow):
    def __init__(self, controller: AppController):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Niko Home Control v1 GUI")
        self.resize(900, 540)
        self._init_ui()
        self._populate_locations()
        self.devices_list.itemClicked.connect(self._on_device_selected)

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout()
        central.setLayout(layout)

        # Locations list
        self.locations_list = QListWidget()
        self.locations_list.setMaximumWidth(220)
        self.locations_list.itemClicked.connect(self._on_location_selected)
        layout.addWidget(self.locations_list)

        # Devices list
        self.devices_list = QListWidget()
        layout.addWidget(self.devices_list)

        # Info label and refresh/settings
        info_layout = QVBoxLayout()
        self.info_label = QLabel("Select a room to see devices.")
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self._refresh)
        info_layout.addWidget(self.refresh_button)

        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self._open_settings)
        info_layout.addWidget(self.settings_button)

        layout.addLayout(info_layout)

    def _populate_locations(self):
        self.locations_list.clear()
        try:
            self.controller.refresh_data()
        except NikoError as e:
            QMessageBox.critical(self, "Error", f"Could not contact Niko controller:\n{e.message}")
            return
        # Filter out Location 0!
        for loc in self.controller.locations:
            if loc.id == 0:
                continue
            item = QListWidgetItem(loc.name or f"Location {loc.id}")
            item.setData(Qt.UserRole, loc)
            self.locations_list.addItem(item)
        self.info_label.setText("Select a room to see devices.")

    def _on_location_selected(self, item):
        loc: NikoLocation = item.data(Qt.UserRole)
        devices = self.controller.get_devices_for_location(loc.id)
        self.devices_list.clear()
        for dev in devices:
            # Show name + type + state for status feedback
            dev_type = "Dimmable" if self.controller.is_device_dimmable(dev) else ("Socket" if self.controller.is_device_socket(dev) else "Switch")
            state = self.controller.get_device_state_text(dev)
            dev_item = QListWidgetItem(f"{dev.name} [{dev_type}] — {state}")
            dev_item.setData(Qt.UserRole, dev)
            self.devices_list.addItem(dev_item)
        self.info_label.setText(f"Devices in {loc.name or 'Unnamed'}:")

    def _on_device_selected(self, item):
        dev: NikoDevice = item.data(Qt.UserRole)
        dev_type = "Dimmable" if self.controller.is_device_dimmable(dev) else ("Socket" if self.controller.is_device_socket(dev) else "Switch")
        state = self.controller.get_device_state_text(dev)
        # Dimmable
        if self.controller.is_device_dimmable(dev):
            dlg = BrightnessDialog(dev, self)
            if dlg.exec() == QDialog.Accepted:
                value = dlg.get_brightness()
                self._set_device(dev, value)
        # Socket/Switch
        else:
            msg = f"Device: {dev.name}\nType: {dev_type}\nCurrent: {state}\n\nTurn ON (Yes), OFF (No), or Cancel?"
            btn = QMessageBox.question(
                self, "Toggle Device",
                msg,
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            if btn == QMessageBox.Yes:
                self._set_device(dev, 255)
            elif btn == QMessageBox.No:
                self._set_device(dev, 0)
            # Cancel: do nothing

    def _set_device(self, dev: NikoDevice, value: int, extra_feedback: str = None):
        try:
            # For dimmers: send value1 as 0–100 (not 0–255)
            if self.controller.is_device_dimmable(dev):
                value = int(value)
                if value > 100:
                    value = 100
                if value < 0:
                    value = 0
            self.controller.execute_device_action(dev, value)
            def do_refresh():
                self._refresh()
            QTimer.singleShot(400, do_refresh)  # 400ms delay
        except NikoError as e:
            QMessageBox.critical(self, "Error", f"Failed to set device:\n{e.message}")

    def _refresh(self, device_feedback: str = None):
        # Try to keep current location selected
        loc_item = self.locations_list.currentItem()
        selected_loc_id = None
        if loc_item:
            loc: NikoLocation = loc_item.data(Qt.UserRole)
            selected_loc_id = loc.id
        self._populate_locations()
        if selected_loc_id:
            # Find and re-select
            for i in range(self.locations_list.count()):
                item = self.locations_list.item(i)
                loc = item.data(Qt.UserRole)
                if loc.id == selected_loc_id:
                    self.locations_list.setCurrentItem(item)
                    self._on_location_selected(item)
                    break
        if device_feedback:
            self.info_label.setText(device_feedback)

    def _open_settings(self):
        dlg = SettingsDialog(self.controller.settings, self)
        if dlg.exec() == QDialog.Accepted:
            new_settings = dlg.get_settings()
            self.controller.update_settings(new_settings)
            self._refresh()
            self.info_label.setText("Settings updated. Refreshed data.")
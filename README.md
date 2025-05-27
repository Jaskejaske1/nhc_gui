# Niko Home Control v1 GUI

A modern, modular, and robust graphical user interface for controlling the Niko Home Control v1 system, written in Python using PySide6 (Qt for Python).

---

## **Project Vision**

- **User-friendly**: A simple, intuitive dashboard to control your Niko Home Control v1 devices from your computer.
- **Modular & Expandable**: Protocol logic, data models, UI, and controller logic are fully separated for easy maintenance and future growth.
- **Cross-platform**: Works on modern Linux and Windows (and macOS, with PySide6).
- **Modern codebase**: Uses Python 3.11+ and best practices.

---

## **Features**

- **Device Discovery**: Automatically lists all actions/devices and locations from your Niko system.
- **Room-based Control**: Control devices room-by-room (toggle, dim, scenes, etc.).
- **Robust Error Handling**: Survives connection drops, protocol quirks, and malformed data.
- **Expandable UI**: Easily add new views (e.g., scenes, thermostat, schedules) as you wish.

*Planned:*
- Device and scene icons.
- Status updates and feedback.
- Theming (light/dark).
- Optional web interface or mobile-friendly view.
- Automation and scheduling.

---

## **Directory Structure**

```
nhc_gui/
├── core/
│   └── niko_client.py      # Protocol logic & data models (pure Python, no UI)
├── ui/
│   ├── mainwindow.py       # Main window and widgets
│   └── widgets/            # Custom widgets for devices, locations, etc.
├── controller/
│   └── app_controller.py   # Connects core and UI, handles app logic
├── resources/
│   └── icons/              # (Optional) Device and room icons
├── main.py                 # Entry point for launching the app
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

---

## **Installation**

### **1. Dependencies**

- Python 3.11 or higher
- [PySide6](https://pypi.org/project/PySide6/)
- (Optional) `pip` for managing packages

### **2. Install Requirements**

```bash
pip install -r requirements.txt
```
Or, if you’re starting from scratch:
```bash
pip install PySide6
```

---

## **Usage**

1. **Configure your Niko Home Control v1 Controller IP**  
   Edit `main.py` to set the correct IP address of your Niko controller on your LAN.

2. **Launch the app**
   ```bash
   python main.py
   ```

3. **Enjoy the dashboard!**  
   - Browse rooms and devices
   - Toggle lights, run scenes, etc.
   - Errors and feedback will be shown in the UI

---

## **Development Philosophy**

- **Separation of concerns:** Protocol code is totally decoupled from UI code. The controller mediates between them.
- **Testability:** All protocol and data logic can be tested independently, enabling future unit/integration tests.
- **Expandable:** Add new device types, views, or even a web/CLI interface without rewriting protocol code.
- **Secure and robust:** No unsafe operations; all user and network input is validated and errors are handled gracefully.

---

## **Contributing & Extending**

- Want a new view, device type, or automation? Implement a widget in `ui/widgets/`, update the controller, and you’re done.
- Want a web or CLI interface in the future? Just reuse the `core/` logic.
- Suggestions, bug reports, and PRs are welcome!

---

## **License**

[MIT License](LICENSE)
---

## **Acknowledgments**

- Inspired by the Niko Home Control community, and built with Qt for Python (PySide6).

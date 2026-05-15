import hou
import os
import datetime
import re
import json

# Auto-compatible with Houdini 19 (PySide2) and Houdini 20 (PySide6)
try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide6 import QtWidgets, QtCore, QtGui


# ==========================================
# 1. Global Configurations & Utilities
# ==========================================
PREF_FILE = os.path.join(hou.homeHoudiniDirectory(), "ming_cpio_prefs.json")
DEFAULT_PATH = r"S:\temp\MING\cpio"

def load_paths():
    if os.path.exists(PREF_FILE):
        try:
            with open(PREF_FILE, 'r') as f:
                return json.load(f).get("paths", [])
        except:
            pass
    return [DEFAULT_PATH] 

def save_paths(paths):
    with open(PREF_FILE, 'w') as f:
        json.dump({"paths": paths}, f, indent=4)


# ==========================================
# 2. Module API: Copy Selected Nodes
# ==========================================
def copy_selected_nodes():
    """Function to copy selected nodes and save as a CPIO file."""
    nodes = hou.selectedNodes()
    if not nodes:
        hou.ui.displayMessage("Please select nodes to copy first!", severity=hou.severityType.Warning)
        return

    current_paths = load_paths()
    save_dir = current_paths[0] if current_paths else DEFAULT_PATH

    if not os.path.exists(save_dir):
        try:
            os.makedirs(save_dir)
        except Exception as e:
            hou.ui.displayMessage(f"Failed to create folder: {e}", severity=hou.severityType.Error)
            return
            
    button_idx, input_str = hou.ui.readInput(
        f"Saving to: {save_dir}\n\nPlease enter a name for this node package:\n(The system will automatically prepend the timestamp)",
        buttons=('Save', 'Cancel'),
        title="Save Nodes to Library",
        default_choice=0, close_choice=1
    )
    
    if button_idx == 0 and input_str.strip():
        safe_name = re.sub(r'[\\/*?:"<>|]', "", input_str.strip()).replace(" ", "_")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{timestamp}_{safe_name}.cpio"
        file_path = os.path.join(save_dir, file_name)
        
        parent = nodes[0].parent()
        parent.saveItemsToFile(nodes, file_path)

        metadata = {
            "context_path": parent.path(),
            "node_count": len(nodes),
            "author": hou.userName()
        }
        json_path = file_path.replace(".cpio", ".json")
        try:
            with open(json_path, 'w') as jf:
                json.dump(metadata, jf, indent=4)
        except:
            pass 
        
        hou.ui.displayMessage(f"Packaged successfully!\nFile saved as: {file_name}")
        
    elif button_idx == 0 and not input_str.strip():
        hou.ui.displayMessage("Name cannot be empty. Save cancelled.", severity=hou.severityType.Warning)


# ==========================================
# 3. UI Classes
# ==========================================
class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setWindowTitle("CPIO Read Path Settings")
        self.resize(450, 250)

        self.paths = load_paths()

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel("Configure folders to scan (multiple supported):"))

        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.addItems(self.paths)
        layout.addWidget(self.list_widget)

        bottom_layout = QtWidgets.QHBoxLayout()

        self.btn_add = QtWidgets.QPushButton()
        self.btn_add.setIcon(hou.qt.Icon("BUTTONS_add"))
        self.btn_add.setToolTip("Add Path")
        self.btn_add.setFixedSize(28, 28)

        self.btn_remove = QtWidgets.QPushButton()
        self.btn_remove.setIcon(hou.qt.Icon("BUTTONS_remove")) 
        self.btn_remove.setToolTip("Remove Selected Path")
        self.btn_remove.setFixedSize(28, 28)

        self.btn_save = QtWidgets.QPushButton("Save")
        self.btn_cancel = QtWidgets.QPushButton("Cancel")

        bottom_layout.addWidget(self.btn_add)
        bottom_layout.addWidget(self.btn_remove)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.btn_save)
        bottom_layout.addWidget(self.btn_cancel)

        layout.addLayout(bottom_layout)

        self.btn_add.clicked.connect(self.add_path)
        self.btn_remove.clicked.connect(self.remove_path)
        self.btn_save.clicked.connect(self.save_and_close)
        self.btn_cancel.clicked.connect(self.reject)

    def add_path(self):
        dir_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select CPIO folder to add")
        if dir_path and dir_path not in self.paths:
            dir_path = os.path.normpath(dir_path)
            self.paths.append(dir_path)
            self.list_widget.addItem(dir_path)

    def remove_path(self):
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            self.list_widget.takeItem(current_row)
            self.paths.pop(current_row)

    def save_and_close(self):
        save_paths(self.paths)
        self.accept()


class CleanListDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(CleanListDialog, self).__init__(parent)
        self.setWindowTitle("Select Nodes to Paste")
        self.resize(660, 900) # defaule size

        self.selected_file_path = None
        self.file_mapping = {}

        layout = QtWidgets.QVBoxLayout(self)
        label = QtWidgets.QLabel("Node History:\nPlease select a node package to paste (Double-click to paste)")
        layout.addWidget(label)

        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        layout.addWidget(self.list_widget)

        btn_layout = QtWidgets.QHBoxLayout()

        self.btn_settings = QtWidgets.QPushButton()
        self.btn_settings.setIcon(hou.qt.Icon("BUTTONS_gear"))
        self.btn_settings.setToolTip("Configure CPIO Scan Folders")
        self.btn_settings.setFixedSize(28, 28)

        # ==========================================
        # REVERTED: Using native BUTTONS_minus icon
        # ==========================================
        self.btn_delete = QtWidgets.QPushButton()
        self.btn_delete.setIcon(hou.qt.Icon("BUTTONS_minus")) 
        self.btn_delete.setToolTip("Delete Selected Package")
        self.btn_delete.setFixedSize(28, 28)

        self.btn_accept = QtWidgets.QPushButton("Accept")
        self.btn_cancel = QtWidgets.QPushButton("Cancel")
        self.btn_accept.setDefault(True)

        btn_layout.addWidget(self.btn_settings)
        btn_layout.addWidget(self.btn_delete) 
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_accept)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

        self.btn_settings.clicked.connect(self.open_settings)
        self.btn_delete.clicked.connect(self.delete_selected_package) 
        self.btn_accept.clicked.connect(self.accept_selection)
        self.btn_cancel.clicked.connect(self.reject)
        self.list_widget.itemDoubleClicked.connect(self.accept_selection)

        self.refresh_list()

    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog_exec = getattr(dialog, 'exec_', dialog.exec)
        if dialog_exec():
            self.refresh_list()

    def delete_selected_package(self):
        current_item = self.list_widget.currentItem()
        if not current_item or "No .cpio files found" in current_item.text():
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select a package to delete.")
            return

        display_text = current_item.text()
        cpio_path = self.file_mapping.get(display_text)

        if not cpio_path or not os.path.exists(cpio_path):
            QtWidgets.QMessageBox.critical(self, "Error", "File not found or already deleted.")
            return

        file_name = os.path.basename(cpio_path)
        
        # Safe Qt native modal dialog
        reply = QtWidgets.QMessageBox.warning(
            self,
            "Confirm Delete",
            f"Are you sure you want to permanently delete this package?\n\n{file_name}",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel,
            QtWidgets.QMessageBox.Cancel # Default safety focus
        )

        if reply == QtWidgets.QMessageBox.Yes:
            json_path = cpio_path.replace(".cpio", ".json")
            try:
                os.remove(cpio_path)
                if os.path.exists(json_path):
                    os.remove(json_path)
                self.refresh_list()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to delete file: {e}")


    def refresh_list(self):
        self.list_widget.clear()
        self.file_mapping.clear()
        paths = load_paths()
        all_files_data = []

        for d in paths:
            if os.path.exists(d):
                for f in os.listdir(d):
                    if f.endswith('.cpio'):
                        fp = os.path.join(d, f)
                        
                        context_path = ""
                        json_path = fp.replace(".cpio", ".json")
                        if os.path.exists(json_path):
                            try:
                                with open(json_path, 'r') as jf:
                                    meta = json.load(jf)
                                    context_path = meta.get("context_path", "")
                            except:
                                pass
                                
                        all_files_data.append({
                            'abs_path': fp,
                            'name': f,
                            'mtime': os.path.getmtime(fp),
                            'context': context_path 
                        })

        if not all_files_data:
            self.list_widget.addItem("No .cpio files found in configured paths!")
            return

        all_files_data.sort(key=lambda x: x['mtime'], reverse=True)

        for item in all_files_data:
            time_str = datetime.datetime.fromtimestamp(item['mtime']).strftime('%Y-%m-%d %H:%M:%S')
            
            if item['context']:
                display_text = f"{time_str}  |  [{item['context']}]  |  {item['name']}"
            else:
                display_text = f"{time_str}  |  {item['name']}" 
                
            self.list_widget.addItem(display_text)
            self.file_mapping[display_text] = item['abs_path']

    def accept_selection(self):
        current_item = self.list_widget.currentItem()
        if current_item and "No .cpio files found" not in current_item.text():
            self.selected_file_path = self.file_mapping.get(current_item.text())
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please select a valid node package!")


# ==========================================
# 4. Module API: Show Paste UI
# ==========================================
def show_paste_ui():
    """Function to launch the paste UI and load selected CPIO."""
    dialog = CleanListDialog(hou.qt.mainWindow())
    dialog_exec = getattr(dialog, 'exec_', dialog.exec)

    if dialog_exec() and dialog.selected_file_path:
        pane = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
        if pane:
            current_context = pane.pwd()
            try:
                current_context.loadItemsFromFile(dialog.selected_file_path)
            except Exception as e:
                hou.ui.displayMessage(f"Load failed: {e}", severity=hou.severityType.Error)
        else:
            hou.ui.displayMessage("Paste failed! Please hover your mouse over a Network Editor.", severity=hou.severityType.Warning)
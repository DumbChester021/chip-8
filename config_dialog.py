from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QSpinBox, QDoubleSpinBox, QPushButton, QColorDialog,
                           QGroupBox, QCheckBox)
from PyQt6.QtCore import Qt

class ConfigDialog(QDialog):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Emulator Configuration")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # CPU Settings
        cpu_group = QGroupBox("CPU Settings")
        cpu_layout = QVBoxLayout()
        
        # CPU Frequency
        freq_layout = QHBoxLayout()
        freq_layout.addWidget(QLabel("CPU Frequency (Hz):"))
        self.freq_spin = QSpinBox()
        self.freq_spin.setRange(100, 2000)
        self.freq_spin.setValue(self.config.cpu_frequency)
        freq_layout.addWidget(self.freq_spin)
        cpu_layout.addLayout(freq_layout)
        
        cpu_group.setLayout(cpu_layout)
        layout.addWidget(cpu_group)
        
        # Display Settings
        display_group = QGroupBox("Display Settings")
        display_layout = QVBoxLayout()
        
        # Scale
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("Display Scale:"))
        self.scale_spin = QSpinBox()
        self.scale_spin.setRange(1, 20)
        self.scale_spin.setValue(self.config.display_scale)
        scale_layout.addWidget(self.scale_spin)
        display_layout.addLayout(scale_layout)
        
        # Colors
        colors_layout = QHBoxLayout()
        self.fg_button = QPushButton("Foreground Color")
        self.bg_button = QPushButton("Background Color")
        self.fg_button.clicked.connect(self.choose_fg_color)
        self.bg_button.clicked.connect(self.choose_bg_color)
        colors_layout.addWidget(self.fg_button)
        colors_layout.addWidget(self.bg_button)
        display_layout.addLayout(colors_layout)
        
        # Add optimize display checkbox
        optimize_layout = QHBoxLayout()
        self.optimize_check = QCheckBox("Optimize Display Updates")
        self.optimize_check.setChecked(self.config.optimize_display_updates)
        optimize_layout.addWidget(self.optimize_check)
        display_layout.addLayout(optimize_layout)
        
        display_group.setLayout(display_layout)
        layout.addWidget(display_group)
        
        # Sound Settings
        sound_group = QGroupBox("Sound Settings")
        sound_layout = QVBoxLayout()
        
        # Frequency
        sound_freq_layout = QHBoxLayout()
        sound_freq_layout.addWidget(QLabel("Sound Frequency (Hz):"))
        self.sound_freq_spin = QSpinBox()
        self.sound_freq_spin.setRange(20, 2000)
        self.sound_freq_spin.setValue(self.config.sound_frequency)
        sound_freq_layout.addWidget(self.sound_freq_spin)
        sound_layout.addLayout(sound_freq_layout)
        
        # Volume
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("Volume:"))
        self.volume_spin = QDoubleSpinBox()
        self.volume_spin.setRange(0, 1)
        self.volume_spin.setSingleStep(0.1)
        self.volume_spin.setValue(self.config.sound_volume)
        volume_layout.addWidget(self.volume_spin)
        sound_layout.addLayout(volume_layout)
        
        sound_group.setLayout(sound_layout)
        layout.addWidget(sound_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
    
    def choose_fg_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.config.foreground_color = (color.red(), color.green(), color.blue())
    
    def choose_bg_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.config.background_color = (color.red(), color.green(), color.blue())
    
    def get_config(self):
        self.config.cpu_frequency = self.freq_spin.value()
        self.config.display_scale = self.scale_spin.value()
        self.config.sound_frequency = self.sound_freq_spin.value()
        self.config.sound_volume = self.volume_spin.value()
        self.config.optimize_display_updates = self.optimize_check.isChecked()
        return self.config 
import os
import subprocess
import minecraft_launcher_lib
import platform
import pathlib
from packaging import version

from PyQt6.QtCore import QThread, QWaitCondition, QMutex, pyqtSignal
from src import file_work, folder
from src.env import *


class Launcher(QThread):
    progress_signal = pyqtSignal(int, int, str)
    state_signal = pyqtSignal(bool)
    progress = 0
    progress_max = 0
    progress_label = ''
    status = False
    mutex = QMutex()
    wait_condition = QWaitCondition()

    def release_wait(self):
        self.mutex.lock()
        self.wait_condition.wakeAll()
        self.mutex.unlock()

    def update_progress_label(self, value):
        self.progress_label = value
        self.progress_signal.emit(self.progress, self.progress_max, self.progress_label)

    def update_progress(self, value):
        self.progress = value
        self.progress_signal.emit(self.progress, self.progress_max, self.progress_label)

    def update_progress_max(self, value):
        self.progress_max = value
        self.progress_signal.emit(self.progress, self.progress_max, self.progress_label)

    @staticmethod
    def split_forge_version(text):
        lists = text.split('-')
        lists[0] += '-forge-'
        lists[0] += lists[1]
        return lists[0]

    @staticmethod
    def split_fabric_version(text):
        fabric = 'fabric-loader-' + minecraft_launcher_lib.fabric.get_latest_loader_version() + '-' + text
        return fabric

    @staticmethod
    def split_qulit_version(text):
        qulit = 'quilt-loader-' + minecraft_launcher_lib.quilt.get_latest_loader_version() + '-' + text
        return qulit

    def run(self):
        self.state_signal.emit(True)

        if options['username'] == '':
            return

        appdata = os.path.join(pathlib.Path.home(), '.local', 'share')
        os.makedirs(os.path.join(appdata, 'launch'), exist_ok=True)

        if settings['mods'] == 'Forge':
            if settings['minecraft_directory'] == '':
                os.makedirs(os.path.join(appdata, 'launch', f'Forge {settings['version']}'), exist_ok=True)
                settings['minecraft_directory'] = os.path.join(appdata, 'launch', f'Forge {settings['version']}')
            else:
                settings['minecraft_directory'] += f'/{os.path.join('launch', f'Forge {settings['version']}')}'
        elif settings['mods'] == 'Fabric':
            if settings['minecraft_directory'] == '':
                os.makedirs(os.path.join(appdata, 'launch', f'Fabric {settings['version']}'), exist_ok=True)
                settings['minecraft_directory'] = os.path.join(appdata, 'launch', f'Fabric {settings['version']}')
            else:
                settings['minecraft_directory'] += f'/{os.path.join('launch', f'Fabric {settings['version']}')}'
        elif settings['mods'] == 'Qulit':
            if settings['minecraft_directory'] == '':
                os.makedirs(os.path.join(appdata, 'launch', f'Qulit {settings['version']}'), exist_ok=True)
                settings['minecraft_directory'] = os.path.join(appdata, 'launch', f'Qulit {settings['version']}')
            else:
                settings['minecraft_directory'] += f'/{os.path.join('launch', f'Qulit {settings['version']}')}'
        else:
            if settings['minecraft_directory'] == '':
                os.makedirs(os.path.join(appdata, 'launch', settings['version']), exist_ok=True)
                settings['minecraft_directory'] = os.path.join(appdata, 'launch', settings['version'])
            else:
                settings['minecraft_directory'] += f'/{os.path.join('launch', f'/{settings['version']}')}'

        file = file_work.FileLog()

        core = ''
        if platform.system() == "Windows":
            if platform.architecture()[0] == "32bit":
                core = "windows-x86"
            else:
                core = "windows-x64"
        elif platform.system() == "Linux":
            if platform.architecture()[0] == "32bit":
                core = "linux-i386"
            else:
                core = "linux"
        elif platform.system() == "Darwin":
            if platform.machine() == "arm64":
                core = "mac-os-arm64"
            else:
                core = "mac-os"

        runtime = ''
        if version.parse('1.20.6') <= version.parse(settings['version']) <= version.parse('1.21'):
            runtime = 'java-runtime-delta'
        elif version.parse('1.19') <= version.parse(settings['version']) <= version.parse('1.20.4'):
            runtime = 'java-runtime-gamma'
        elif version.parse('1.18') <= version.parse(settings['version']) <= version.parse('1.18.2'):
            runtime = 'java-runtime-beta'
        elif version.parse('1.17.1') == version.parse(settings['version']):
            runtime = 'java-runtime-alpha'
        elif version.parse('1.13.2') <= version.parse(settings['version']) <= version.parse('1.16.5'):
            runtime = 'jre-legacy'

        minecraft_directory = settings['minecraft_directory']
        if file.read_version(minecraft_directory):
            file.write_version(minecraft_directory)
            self.status = True
            if settings['mods'] == "Vanilla":
                minecraft_launcher_lib.install.install_minecraft_version(versionid=settings['version'],
                                                                         minecraft_directory=
                                                                         settings['minecraft_directory'],
                                                                         callback={
                                                                         'setStatus': self.update_progress_label,
                                                                         'setProgress': self.update_progress,
                                                                         'setMax': self.update_progress_max})
                folder.moving_folder_resources()
            elif settings['mods'] == "Forge":
                minecraft_launcher_lib.forge.install_forge_version(minecraft_launcher_lib.forge.find_forge_version(settings['version']),
                                                                   settings['minecraft_directory'],
                                                                   callback={
                                                                   'setStatus': self.update_progress_label,
                                                                   'setProgress': self.update_progress,
                                                                   'setMax': self.update_progress_max},
                                                                   java=f'{minecraft_directory}/runtime/{runtime}/{core}/{runtime}/bin/java')
                self.progress = self.progress_max
                self.progress_signal.emit(self.progress, self.progress_max, self.progress_label)
            elif settings['mods'] == "Fabric":
                minecraft_launcher_lib.fabric.install_fabric(settings['version'],
                                                             settings['minecraft_directory'],
                                                             callback={
                                                             'setStatus': self.update_progress_label,
                                                             'setProgress': self.update_progress,
                                                             'setMax': self.update_progress_max},
                                                             java=f'{minecraft_directory}/runtime/{runtime}/{core}/{runtime}/bin/java')
            elif settings['mods'] == "Qulit":
                minecraft_launcher_lib.quilt.install_quilt(settings['version'],
                                                           settings['minecraft_directory'],
                                                           callback={
                                                           'setStatus': self.update_progress_label,
                                                           'setProgress': self.update_progress,
                                                           'setMax': self.update_progress_max},
                                                           java=f'{minecraft_directory}/runtime/{runtime}/{core}/{runtime}/bin/java')

            self.state_signal.emit(False)

            self.mutex.lock()
            self.wait_condition.wait(self.mutex)
            self.mutex.unlock()

        if len(settings['version']) >= 6:
            if settings['version'][:6] == '1.16.5':
                options['jvmArguments'].append('-Dminecraft.api.env=custom')
                options['jvmArguments'].append('-Dminecraft.api.auth.host=https://invalid.invalid/')
                options['jvmArguments'].append('-Dminecraft.api.account.host=https://invalid.invalid/')
                options['jvmArguments'].append('-Dminecraft.api.session.host=https://invalid.invalid/')
                options['jvmArguments'].append('-Dminecraft.api.services.host=https://invalid.invalid/')

        versions = ''
        if settings['mods'] == 'Vanilla':
            versions = settings['version']
        elif settings['mods'] == "Forge":
            versions = '1.8-forge1.8-11.14.4.1577'
        elif settings['mods'] == 'Fabric':
            versions = self.split_fabric_version(settings['version'])
        elif settings['mods'] == 'Qulit':
            versions = self.split_qulit_version(settings['version'])

        command = minecraft_launcher_lib.command.get_minecraft_command(version=versions,
                                                                       minecraft_directory=
                                                                       minecraft_directory,
                                                                       options=options)

        if settings['console']:
            subprocess.Popen(command)
        else:
            subprocess.Popen(command)

        options['jvmArguments'] = []
        self.state_signal.emit(False)

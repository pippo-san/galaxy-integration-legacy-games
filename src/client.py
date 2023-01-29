import asyncio
import subprocess
import utils
from pathlib import Path

from galaxy.proc_tools import process_iter

class LegacyGamesClient:
    _CLIENT_NAME_ = 'Legacy Games'
    install_location = None

    def __init__(self):
        self._get_install_location()

    def _get_install_location(self):
        self.install_location = utils.get_launcher_path()

    @staticmethod
    def start_client():
        subprocess.call(
            ['runas', '/user:Administrator', LegacyGamesClient.install_location + r"\Legacy Games Launcher.exe"])

    @staticmethod
    def _exec(args, cwd=None):
        subprocess.Popen(
            args,
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW,
            cwd=cwd,
            shell=False
        )

    async def _aexec(self, args, cwd=None):
        proc = await asyncio.create_subprocess_exec(*args)
        return await proc.wait()

    @property
    def is_running(self):
        for proc in process_iter():
            if proc.binary_path and Path(proc.binary_path).resolve() == self.exec_path:
                return True

        return False

    @property
    def exec_path(self):
        if not self.install_location:
            return ''

        return self.install_location.joinpath("Legacy Games Launcher.exe")

    def stop_client(self):
        if self.is_running:
            LegacyGamesClient._exec(f'taskkill /t /f /im "Legacy Games Launcher.exe"')

# -*- mode: python -*-

block_cipher = None

import shutil
from PyInstaller.utils.hooks import collect_submodules
try:
    shutil.rmtree('dist')
except FileNotFoundError:
    print('dist folder not found!')
try:
    shutil.rmtree('distTest')
except FileNotFoundError:
    print('distTest folder not found!')

version_str = str('v1.2.0')

added_hiddenimports = collect_submodules('sqlalchemy')
added_hiddenimports.extend(collect_submodules('discord'))
added_hiddenimports.extend(collect_submodules('swagger-client'))
added_hiddenimports.extend(collect_submodules('SQLAlchemy-Utils'))
added_hiddenimports.extend(collect_submodules('cryptography'))

a = Analysis(['../Insight/__main__.py'],
             pathex=['./Insight'],
             binaries=[],
             datas=[],
             hiddenimports=added_hiddenimports,
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Insight',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True)

from sys import platform
import os
os.mkdir('{}/EVE-Insight'.format(DISTPATH))
shutil.copy('README.md','{}/EVE-Insight/README.md'.format(DISTPATH))
shutil.copy('LICENSE.md','{}/EVE-Insight/LICENSE.md'.format(DISTPATH))
shutil.copy('Insight/default-config.ini','{}/EVE-Insight/default-config.ini'.format(DISTPATH))
shutil.copy('CCP.md','{}/EVE-Insight/CCP.md'.format(DISTPATH))
shutil.copy('Installation.md','{}/EVE-Insight/Installation.md'.format(DISTPATH))
shutil.copy('ChangeLog.md','{}/EVE-Insight/ChangeLog.md'.format(DISTPATH))
shutil.copy('sqlite-latest.sqlite','{}/EVE-Insight/sqlite-latest.sqlite'.format(DISTPATH))
shutil.copytree('Insight/callback','{}/EVE-Insight/callback'.format(DISTPATH))
shutil.copytree('docs','{}/EVE-Insight/docs'.format(DISTPATH))
if platform == "win32":
    archive_name = 'Insight-{}-Windows'.format(version_str)
    archive_file = '{}.zip'.format(archive_name)
    shutil.move('{}/Insight.exe'.format(DISTPATH),'{}/EVE-Insight/Insight.exe'.format(DISTPATH))
    print("This is Windows. Making a zip of file.")
    shutil.make_archive(archive_name,'zip','{}'.format(DISTPATH))
    shutil.move(archive_file,'{}/{}'.format(DISTPATH,archive_file))
elif platform.startswith('linux'):
    archive_name = 'Insight-{}-Linux'.format(version_str)
    archive_file = '{}.tar.gz'.format(archive_name)
    shutil.move('{}/Insight'.format(DISTPATH),'{}/EVE-Insight/Insight'.format(DISTPATH))
    print("This is Linux. Making a tar of file.")
    shutil.make_archive(archive_name,'gztar','{}'.format(DISTPATH))
    shutil.move(archive_file,'{}/{}'.format(DISTPATH,archive_file))
else:
    print("Unsupported os")
shutil.copytree('{}/EVE-Insight'.format(DISTPATH),'distTest')
try:
    shutil.copy('config.ini','distTest/config.ini')
except FileNotFoundError:
    print("No testing config file found")
try:
    shutil.copy('Database.db','distTest/Database.db')
except FileNotFoundError:
    print("No testing database found.")
print("Done! Test the program by running it in the distTest folder.")

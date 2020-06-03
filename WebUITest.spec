# -*- mode: python ; coding: utf-8 -*-
# pyinstaller -F WebUITest.spec

block_cipher = None


a = Analysis(['WebUITest.py'],
             pathex=['C:\\Users\\mrich\\Documents\\WebUI'],
             binaries=[],
             datas=[('favicon.ico','.'),
                    ('js/test.js', 'js')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='WebUITest',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )

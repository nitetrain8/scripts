# -*- mode: python -*-

block_cipher = None


a = Analysis(['src\\verify_files\\verify_files.py'],
             pathex=['.\\src\\verify_files', "..\\filecompare\\src\\filecompare"],
             binaries=[],
             datas=[],
             hiddenimports=['lxml', 'lxml.etree'],
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
          name='verify_files',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )

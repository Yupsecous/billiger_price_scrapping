# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['billiger_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('billiger_price_checker.py', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='BilligerPriceChecker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    name='BilligerPriceChecker',
)

app = BUNDLE(
    coll,
    name='BilligerPriceChecker.app',
    icon=None,
    bundle_identifier='de.billiger.pricechecker',
    info_plist={
        'CFBundleDisplayName': 'Billiger Price Checker',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.15',
    },
)

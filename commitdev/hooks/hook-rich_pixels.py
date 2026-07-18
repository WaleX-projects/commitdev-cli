from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# This forces PyInstaller to collect everything rich_pixels needs to live
datas = collect_data_files('rich_pixels')
hiddenimports = collect_submodules('rich_pixels')

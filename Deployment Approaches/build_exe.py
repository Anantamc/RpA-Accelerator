import PyInstaller.__main__
import os
import shutil

# Make sure PyInstaller is installed
# pip install pyinstaller

# Add this line to your app.py file at the top if it's not already there
# import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Clean previous build artifacts
if os.path.exists('dist'):
    shutil.rmtree('dist')
if os.path.exists('build'):
    shutil.rmtree('build')

# Build the executable
PyInstaller.__main__.run([
    'app.py',
    '--name=PartnerDashboard',
    '--onefile',
    '--windowed',
    '--add-data=config.py;.',
    '--add-data=data.py;.',
    '--add-data=visualization.py;.',
    '--hidden-import=streamlit',
    '--hidden-import=pandas',
    '--hidden-import=numpy',
    '--hidden-import=plotly',
    '--hidden-import=networkx',
    '--hidden-import=pyvis',
])

print("Executable created in the 'dist' folder")

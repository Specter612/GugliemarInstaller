import os
import subprocess

# GugliemarAppフォルダ内に移動
os.chdir(r'C:\GugliemarApp')

# Gugliemar.pyをバックグラウンドで実行
subprocess.Popen(['python', 'Gugliemar.py'], creationflags=subprocess.CREATE_NO_WINDOW)

import os, subprocess
if os.popen("pgrep -f 'bash /content/s32gate[.]sh'").read().strip():
    print("[s32-launch] already running")
else:
    subprocess.Popen("nohup bash /content/s32gate.sh 48397 > /content/s32gate.log 2>&1", shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("[s32-launch] launched")

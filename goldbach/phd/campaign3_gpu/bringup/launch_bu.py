import os, subprocess, sys
if os.popen("pgrep -f 'bash /content/bringup_[a-z0-9]*[.]sh'").read().strip():
    print("[bu-launch] already running")
else:
    subprocess.Popen("nohup bash /content/bringup_rtx491.sh PARTX > /content/bringup.out 2>&1", shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("[bu-launch] launched")

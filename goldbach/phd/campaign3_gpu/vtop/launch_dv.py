import os, subprocess
if os.popen("pgrep -f 'python3 /content/deploy_vtop[.]py'").read().strip():
    print("[dv-launch] already running")
elif "--vector-place" in open("/content/deep_env_v89").read():
    print("[dv-launch] deep_env_v89 already has --vector-place; not launching")
else:
    subprocess.Popen("nohup python3 /content/deploy_vtop.py > /content/deploy_vtop.log 2>&1", shell=True, start_new_session=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("[dv-launch] launched")

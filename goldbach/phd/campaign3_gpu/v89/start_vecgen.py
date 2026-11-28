# Unpack the 89-moduli cover tools to /content/cover89 (if not there) and start this card's vector producer (vecgen.sh) unless it already runs.
#   PART from /content/vec_part (0 gold-g4, 1 gold-g4b, 2 gold-g4c), NPART 3; vectors to /content/vec89 for the vector campaign in /content/c170v.
import os, subprocess
if not os.path.isdir("/content/cover89"):
    subprocess.run("tar -xzf /content/cover89.tgz -C /content", shell=True, check=True)
part = open("/content/vec_part").read().strip()
if os.popen("pgrep -f 'bash /content/vecgen[.]sh'").read().strip():
    print("[vg] already running")
else:
    subprocess.Popen(f"nohup bash /content/vecgen.sh /content/vec89 /content/c170v {part} 3 >> /content/vecgen.log 2>&1", shell=True, start_new_session=True,
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("[vg] started, part", part)

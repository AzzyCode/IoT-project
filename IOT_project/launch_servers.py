import subprocess
import signal

try:
    process1 = subprocess.Popen(["python", "server.py"])
    process2 = subprocess.Popen(["python", "server2.py"])
    while True:
        # Keep the main thread alive
        pass
except Exception as e:
    print("An error occurred:", e)
finally:
    # Ensure subprocesses are terminated
    process1.terminate()
    process2.terminate()
    process1.wait()
    process2.wait()
    print("Subprocesses terminated.")
  
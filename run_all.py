import subprocess
import threading
import time
import webbrowser

def run_fastapi():
    subprocess.run(["uvicorn", "app.main:app", "--reload"])

def run_streamlit():
    time.sleep(2)  # wait for FastAPI to start
    webbrowser.open("http://localhost:8501")  # open browser
    subprocess.run(["streamlit", "run", "todo_app.py"])

# Run FastAPI in a thread
t1 = threading.Thread(target=run_fastapi)
t1.start()

# Run Streamlit in another thread
t2 = threading.Thread(target=run_streamlit)
t2.start()

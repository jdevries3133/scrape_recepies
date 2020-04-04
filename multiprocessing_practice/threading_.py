import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

start = time.perf_counter()

def do_something(seconds):
    print(f'Sleeping {seconds} second...')
    time.sleep(seconds)
    return f'Done Sleeping {seconds} seconds.'

# threads = []
# for _ in range(10):
#     t = threading.Thread(target=do_something, args=[1.5])
#     t.start()
#     threads.append(t)


# for thread in threads:
#     thread.join()

with ThreadPoolExecutor() as executor:
    secs = [5, 4, 3, 2, 1]
    threads = [executor.submit(do_something, second) for second in secs]

    for f in as_completed(threads):
        print(f.result())



end = time.perf_counter()

print(f'Finished in {round (end-start, 2)} second(s)')




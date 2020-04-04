import time
import concurrent.futures

start = time.perf_counter()

def do_something(seconds):
    print(f'sleeping {seconds} second...)')
    time.sleep(seconds)
    return f'Done Sleeping... {seconds}'

if __name__ == '__main__':

    with concurrent.futures.ProcessPoolExecutor() as executor:

        # this way is the simplest implementation.
        secs = [5, 4, 3, 2, 1]
        results = executor.map(do_something, secs)

        # this way seems to present more opportunities for logging;
        # less of a black box.
        secs = [5, 4, 3, 2, 1]
        results = [executor.submit(do_something, 1) for secs in secs]

        for f in concurrent.futures.as_completed(results):
            print(f.result())

    finish = time.perf_counter()

    print(f'Finished in {round(finish-start, 2)} second(s)')

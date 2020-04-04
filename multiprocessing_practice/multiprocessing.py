import time
import concurrent.futures
import multiprocessing


def do_something(seconds):
    print(f'Sleeping {seconds} second......')
    time.sleep(seconds)
    return f'Done sleeping after {seconds} second.'



if __name__ == '__main__':
    start = time.perf_counter()

    with concurrent.futures.ProcessPoolExecutor() as executor:

        secs = [5, 4, 3, 2, 1]
    #     results = [executor.submit(do_something, x) for x in secs]


        results = executor.map(do_something, secs)

        for proc in concurrent.futures.as_completed(results):
            print(proc.result())





    end = time.perf_counter()

    print(f'Processes finished in {end} seconds.')

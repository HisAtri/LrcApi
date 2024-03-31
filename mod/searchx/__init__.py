from concurrent import futures

from mod.searchx import api, kugou


def search_all(title, artist, album, timeout=30):
    funcs = [api, kugou]
    results = []

    def request(task):
        res: list = task.search(title, artist, album)
        if isinstance(res, list):
            results.extend(res)

    with futures.ThreadPoolExecutor() as executor:
        _futures = []
        for func in funcs:
            _futures.append(executor.submit(request, func))

        # 等待所有任务完成，或回收超时任务，处理TimeoutError
        for future in futures.as_completed(_futures, timeout=timeout):
            future.result()
        # 回收超时任务
        for future in _futures:
            if future.done() and future.exception():
                future.result()
            else:
                future.cancel()
    return results


if __name__ == "__main__":
    print(search_all("大地", "Beyond", ""))

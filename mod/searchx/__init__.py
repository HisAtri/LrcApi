from concurrent import futures

from mod.searchx import api, kugou, netease


def search_all(title, artist, album, timeout=15):
    funcs = [api, kugou, netease]
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
        try:
            for future in futures.as_completed(_futures, timeout=timeout):
                future.result()
        except futures.TimeoutError:
            # 记录超时任务
            pass

        # 回收超时任务
        for future in _futures:
            if future.done():
                if future.exception():
                    # 处理异常任务
                    pass
            else:
                future.cancel()

    return results

if __name__ == "__main__":
    print(search_all("大地", "Beyond", ""))

import time
import threading


class Benchmark:
    def __init__(self, threads=1, rounds=1000):
        # 初始化时指定线程数和测试轮数
        # 总测试次数 = 线程数 * 轮数
        self.threads = threads
        self.rounds = rounds

    def _work(self, func, *args, **kwargs):
        # 单线程测试
        for i in range(self.rounds):
            func(*args, **kwargs)
        return

    def run(self, func, *args, **kwargs):
        """
        多线程测试,每个线程测试指定轮数，返回平均耗时和总耗时
        :param func:
        :param args:
        :param kwargs:
        :return:
        """
        # 创建多个线程
        threads = []
        for i in range(self.threads):
            t = threading.Thread(target=self._work, args=(func, *args), kwargs=kwargs)
            threads.append(t)
        # 计时开始
        start = time.time()
        # 启动所有线程
        for t in threads:
            t.start()
        # 等待所有线程结束
        for t in threads:
            t.join()
        # 计时结束
        end = time.time()
        all_time = end - start
        avg_time = all_time / (self.threads*self.rounds)
        return all_time, avg_time
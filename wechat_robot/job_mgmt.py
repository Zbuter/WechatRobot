# -*- coding: utf-8 -*-
import time
from typing import Any, Callable, List

import schedule


class Job(object):
    def __init__(self) -> None:
        pass

    def onEverySeconds(self, seconds: int, task: Callable[..., Any], *args, **kwargs) -> schedule.Job:
        """
        每 seconds 秒执行
        :param seconds: 间隔，秒
        :param task: 定时执行的方法
        :return: None
        """
        return schedule.every(seconds).seconds.do(task, *args, **kwargs)

    def onEveryWeek(self, week: int, atTime: str, task: Callable[..., Any], *args, **kwargs) -> schedule.Job or None:
        """
        每周执行
        :param week: 每周几
        :param task: 定时执行的方法
        :return: None
        """
        every = schedule.every(1)

        mapWeek = {
            1: every.monday,
            2: every.tuesday,
            3: every.wednesday,
            4: every.thursday,
            5: every.friday,
            6: every.saturday,
            7: every.sunday,
        }

        weekJob = mapWeek.get(week)

        if weekJob is None:
            return None

        return weekJob.at(atTime).do(task, *args, **kwargs)

    def onEveryMinutes(self, minutes: int, task: Callable[..., Any], *args, **kwargs) -> schedule.Job:
        """
        每 minutes 分钟执行
        :param minutes: 间隔，分钟
        :param task: 定时执行的方法
        :return: None
        """

        return schedule.every(minutes).minutes.do(task, *args, **kwargs)

    def onEveryHours(self, hours: int, task: Callable[..., Any], *args, **kwargs) -> schedule.Job:
        """
        每 hours 小时执行
        :param hours: 间隔，小时
        :param task: 定时执行的方法
        :return: None
        """
        return schedule.every(hours).hours.do(task, *args, **kwargs)

    def onEveryDays(self, days: int, task: Callable[..., Any], *args, **kwargs) -> schedule.Job:
        """
        每 days 天执行
        :param days: 间隔，天
        :param task: 定时执行的方法
        :return: None
        """
        return schedule.every(days).days.do(task, *args, **kwargs)

    def onEveryTime(self, times: str, task: Callable[..., Any], *args, **kwargs) -> schedule.Job or List[schedule.Job]:
        """
        每天定时执行
        :param times: 时间字符串列表，格式:
            - For daily jobs -> HH:MM:SS or HH:MM
            - For hourly jobs -> MM:SS or :MM
            - For minute jobs -> :SS
        :param task: 定时执行的方法
        :return: None

        例子: times=["10:30", "10:45", "11:00"]
        """
        if not isinstance(times, list):
            times = [times]

        jobs = []
        for t in times:
            jobs.append(schedule.every(1).days.at(t).do(task, *args, **kwargs))

        return jobs if len(jobs) > 1 else jobs[0]

    def cancelJob(self, job: schedule.Job):
        schedule.cancel_job(job)

    def runPendingJobs(self) -> None:
        schedule.run_pending()


if __name__ == '__main__':
    def printstr(s):
        print(s)


    job = Job()
    testJob = job.onEverySeconds(3, printstr, "test")
    i = 0
    while True:
        i += 1
        time.sleep(1)

        job.runPendingJobs()
        if i == 40:
            job.cancelJob(testJob)
            print('end')

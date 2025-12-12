import Scheduler


if __name__ == "__main__":
    # simple demo
    def hello(name):
        print(f"[{time.strftime('%X')}] Hello {name}")

    s = Scheduler()

    # helper to schedule with time-of-day and date-range constraints
    def _parse_time(t):
        if t is None:
            return None
        if isinstance(t, str):
            return datetime.strptime(t, "%H:%M").time()
        if isinstance(t, datetime):
            return t.time()
        return t  # assume datetime.time

    def _parse_date(d):
        if d is None:
            return None
        if isinstance(d, str):
            return datetime.strptime(d, "%Y-%m-%d").date()
        if isinstance(d, datetime):
            return d.date()
        return d  # assume datetime.date

    def schedule_with_window(scheduler: Scheduler, interval: float, func: Callable[..., Any], *fargs,
                             start_time=None, end_time=None, start_date=None, end_date=None, **fkwargs) -> int:
        st = _parse_time(start_time)
        et = _parse_time(end_time)
        sd = _parse_date(start_date)
        ed = _parse_date(end_date)

        state = {"eid": None}

        def wrapper(*a, **k):
            now = datetime.now()
            nd = now.date()
            nt = now.time()

            if sd and nd < sd:
                return
            if ed and nd > ed:
                # cancel future runs once beyond end date
                if state["eid"] is not None:
                    scheduler.cancel(state["eid"])
                return

            in_window = True
            if st and et:
                if st <= et:
                    in_window = (st <= nt <= et)
                else:
                    # wraps past midnight
                    in_window = (nt >= st) or (nt <= et)

            if in_window:
                func(*fargs, **fkwargs)

        eid = scheduler.schedule_every(interval, wrapper)
        state["eid"] = eid
        return eid

    # demo: use a time window and a date range
    s.start()
    # schedule 'hello' every 1s but only between now and now+1 day and between HH:MM ranges
    now = datetime.now()
    today = now.date()
    tomorrow = (now + timedelta(days=1)).date()

    # run every 1s between 00:00 and 23:59 today only
    schedule_with_window(s, 1.0, hello, "Windowed",
                         start_time="00:00", end_time="23:59",
                         start_date=today, end_date=today)

    time.sleep(5)
    s.stop()
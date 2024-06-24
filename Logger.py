import logging

info_log = logging.getLogger("info_logs")
info_log.setLevel(logging.INFO)
file_holder = logging.FileHandler("logs/info_logs", mode="a")
logs_format = logging.Formatter("%(asctime)s %(levelname)s %(funcName)s: %(message)s")
file_holder.setFormatter(logs_format)
info_log.addHandler(file_holder)


error_log = logging.getLogger("error_logs")
error_log.setLevel(logging.ERROR)
file_holder1 = logging.FileHandler("logs/error_logs", mode="a")
file_holder1.setFormatter(logs_format)
error_log.addHandler(file_holder1)


rec_log = logging.getLogger("rec_log")
rec_log.setLevel(logging.INFO)
file_holder2 = logging.FileHandler("logs/rec_log", mode = "a")
file_holder2.setFormatter(logs_format)
rec_log.addHandler(file_holder2)









import logging

class MysqlSender:
    pass 

class MysqlHandler(logging.Handler):
    def emit(self, record):
        #print dir(self)
        #print self.formatter.format(record)
        print "emit runs"

class CommonHandler(logging.Handler):
    def emit(self, record):
        if record.getMessage() != "":
            print self.formatter.format(record)
        else:
            print ""
        #print "emit runs"

def init_log():
        format_str = '%(asctime)s [%(filename)s:%(lineno)d ] [%(levelname)s] %(message)s'
        date_str = '%Y-%m-%d %H:%M:%S'
        formatter = logging.Formatter(format_str, date_str)

        logging.basicConfig(
            level = logging.DEBUG,
            format = format_str,
            datefmt = date_str,
            filename = 'log/test_tool.log',
            filemode = 'a'
        )
        base_logger = logging.getLogger()

        common_handler = CommonHandler()
        common_handler.setLevel(logging.INFO)
        common_handler.setFormatter(formatter)
        #base_logger.addHandler(common_handler)

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(formatter)
        base_logger.addHandler(console)

        #console = MysqlHandler()
        #console.setLevel(logging.INFO)
        #console.setFormatter(formatter)
        #base_logger.addHandler(console)
        

def test_log():
        logging.debug("hello world")
        logging.info("hello world")
        logging.warning("hello world")
        logging.error("hello world")
        logging.critical("hello world")
        logging.info("")

if __name__ == "__main__":
    init_log()
    test_log()


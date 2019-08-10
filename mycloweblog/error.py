class EmailSendError(Exception):
    def __init__(self, errorinfo):
        super().__init__(self)                      # 初始化父类
        self.error_info = errorinfo

    def __str__(self):
        return self.error_info

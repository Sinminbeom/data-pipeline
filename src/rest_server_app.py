import time

from Log.cLogger import cLogger, E_LOG

from App.AppObject import cMpAppFromCate
from App.Category.cCateGory import cProcessCate, E_CATE

class cRestServer(cMpAppFromCate):
    def __init__(self, *_cate):
        super().__init__(E_CATE.REST_SERVER, *_cate)

    def Init(self):
        self.getMP().Start()

    def OnRun(self):
        time.sleep(0.1)
        pass


def main():
    try:
        cProcessCate.instance().RegisterRestServer()

        app = cRestServer(E_CATE.REST_SERVER)
        app.Init()
        app.Run()
    except Exception as e:
        cLogger.instance().Print(E_LOG.EXCEPTION, "Rest Server Not Launched")
        raise e


if __name__ == '__main__':
    main()
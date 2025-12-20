import time

from Log.cLogger import cLogger, E_LOG

from App.AppObject import cMpAppFromCate
from App.Category.cCateGory import cProcessCate, E_CATE


class cMessageBridge(cMpAppFromCate):

    def __init__(self, *_cate):
        super().__init__(E_CATE.MESSAGE_BRIDGE, *_cate)

        pass

    def Init(self):
        self.getMP().Start()

    def OnRun(self):
        time.sleep(0.1)
        pass



def main():
    try:
        cProcessCate.instance().RegisterMessageBridge()

        app = cMessageBridge(E_CATE.MESSAGE_BRIDGE)
        app.Init()
        app.Run()

    except Exception as e:
        cLogger.instance().Print(E_LOG.EXCEPTION, "Message Bridge Not Launched")
        raise e



if __name__ == '__main__':
    main()

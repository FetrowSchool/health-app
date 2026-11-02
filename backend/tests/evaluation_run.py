"""Run existing/current mocked backend checks and export outcome IDs, not secrets."""
import io
import json
import sys
import time
import unittest
from pathlib import Path


class Results(unittest.TextTestResult):
    def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.records=[]
    def startTest(self,test):self.started=time.monotonic();super().startTest(test)
    def record(self,test,status):self.records.append({'test_id':test.id(),'result':status,'seconds':round(time.monotonic()-self.started,6)})
    def addSuccess(self,test):super().addSuccess(test);self.record(test,'PASS')
    def addFailure(self,test,error):super().addFailure(test,error);self.record(test,'FAIL')
    def addError(self,test,error):super().addError(test,error);self.record(test,'ERROR')
    def addSkip(self,test,reason):super().addSkip(test,reason);self.record(test,'NOT RUN')


if __name__=='__main__':
    target=Path(sys.argv[1]);stream=io.StringIO()
    result=unittest.TextTestRunner(stream=stream,resultclass=Results,verbosity=2).run(unittest.defaultTestLoader.discover('backend/tests'))
    target.write_text(json.dumps({'method':'Fresh deterministic backend tests; temporary fictional databases and mocked provider transports','tests_run':result.testsRun,'successful':result.wasSuccessful(),'records':result.records},indent=2)+'\n')
    print('Backend:',result.testsRun,'tests; success=',result.wasSuccessful())
    if not result.wasSuccessful():print(stream.getvalue())
    sys.exit(0 if result.wasSuccessful() else 1)

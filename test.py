print '########################################################'
print '# BEGIN TEST OUTPUT                                    #'
print '########################################################\n'

import threading

import comms.protocols as protocols
import comms.protocols.IFreeEMS_Vanilla.v0_0_1.receive as receive

rec = None

###############################################################################
# Stub classes implementing minimal functionality
class test_controller:

    fails = 0
    passes = 0

    watcher = None
    
    def __init__(self):
        self.watcher = self.printer


    def wantsResult(self, watcher):
        self.watcher = watcher


    def action(self, action, data):

        while data['queue']:
            packet = data['queue'].pop(0)
            self.watcher('Packet returned: %s' % packet.getHex())


    def log(self, module, type, message, data):
        string = '%s msg from %s: %s' % (type, module, message)

        if data:
            string += ' [%s]' % data

        self.watcher(string)


    def printer(self, message):
        print message


###############################################################################
# Test definitions
class test_definition:

    _lock = None

    name = 'No test name set!'
    packet = ''
    results = None
    _actual_results = []
    

    def _sendTestPacket(self):
        global rec
        rec.received(self.packet)


    def _log(self, message):
        if isinstance(message, list):
            message = "\n".join(message)

        print message


    def __init__(self, controller):
        '''
        Do stuff pre test
        '''
        self._lock = threading.Event()

        self.controller = controller

        self._actual_results = []
        self.controller.wantsResult(self.getResult)

        self._log('')
        self._log('TEST: %s' % self.name)

    
    def getResult(self, result):
        '''
        Sets result
        '''
        self._actual_results.append(result)


    def _checkResults(self):
        '''
        Compares actual results to expected results
        '''

        self._log(self._actual_results)

        if self.results == self._actual_results:
            self.controller.passes += 1
            self._log('PASS!')
        else:
            self.controller.fails += 1
            self._log('FAIL!!')
            self._log('Expected:')
            self._log(self.results)


    def run(self):
        '''
        Run test
        '''
        self._sendTestPacket()
        
        self._lock.wait(0.5)
        self._lock.clear()

        self._checkResults()


class test_good(test_definition):
    name = 'Good Packet w/length'
    packet = "\xAA\x08\x00\x05\x00\x02\x00\xFF\x0E\xCC"
    results = ['Packet returned: 0xAA,0x08,0x00,0x05,0x00,0x02,0x00,0xFF,0x0E,0xCC']


class test_doubleStart(test_definition):
    name = 'Double start bytes'
    packet = "\xAA\xAA\x08\x00\x05\x00\x02\x01\xFF\x0F\xCC"
    results = ['ERROR msg from test_receive: processReceiveBuffer could not parse buffer. Bad/incomplete packet found in buffer 0xAA',
               'Packet returned: 0xAA,0x08,0x00,0x05,0x00,0x02,0x01,0xFF,0x0F,0xCC']


class test_oneBadByte(test_definition):
    name = 'One bad byte'
    packet = "\x00"
    results = ['ERROR msg from test_receive: processReceiveBuffer could not parse buffer. Bad/incomplete packet found in buffer 0x00']


class test_twoBadBytes(test_definition):
    name = 'Two bad bytes'
    packet = "\x00\x01"
    results = ['ERROR msg from test_receive: processReceiveBuffer could not parse buffer. Bad/incomplete packet found in buffer 0x00,0x01']


class test_badByteBeforePacket(test_definition):
    name = 'Bad byte before packet'
    packet = "\x01\xAA\x08\x00\x05\x00\x02\x00\xFE\x0D\xCC"
    results = ['ERROR msg from test_receive: processReceiveBuffer could not parse buffer. Bad/incomplete packet found in buffer before start byte 0x01 [0xAA,0x08,0x00,0x05,0x00,0x02,0x00,0xFE,0x0D,0xCC]',
               'Packet returned: 0xAA,0x08,0x00,0x05,0x00,0x02,0x00,0xFE,0x0D,0xCC']


tests = [
    test_good,
    test_doubleStart,
    test_oneBadByte,
    test_twoBadBytes,
    test_badByteBeforePacket
]
    
    
###############################################################################
# Run tests
ctrl = test_controller()

try:
    # Create receive thread for testing
    rec = receive.thread('test_receive', ctrl, 'comms')

    for test in tests:
        instance = test(ctrl)
        instance.run()

    ctrl.printer('')
    ctrl.printer('%d passes, %d fails' % (ctrl.passes, ctrl.fails))

except Exception:
    raise

finally:
    print ''
    if rec:
        ctrl.watcher = ctrl.printer
        rec.exit()

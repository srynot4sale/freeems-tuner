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



class test_badChecksum(test_definition):
    name = 'Bad Checksum'
    packet = '\xAA\x08\x01\x91\x00\x60\x63\x25\x64\x5E\x00\x00\x62\x80\xF3\x1C\x43\x7C\xE3\x51\x60\x63\x25\x64\x5E\x00\x00\x62\x80\xF3\x1C\x43\x7C\xE3\x51\x71\xCA\x27\x10\x80\x00\x00\x03\x00\x00\x00\x00\xFD\xD4\x00\x00\x00\x00\xF3\x1C\xFD\xD3\x5F\xC8\x34\x89\x34\x27\x3F\x3B\x00\x00\x00\x00\x00\x00\x3F\x3B\x3F\x3B\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x86\x03\x6F\x02\x32\x02\x13\x03\x63\x03\x98\x03\xD5\x02\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xA0\xCC'
    results = ['ERROR msg from test_receive: processReceiveBuffer could not parse buffer. Checksum is incorrect! Provided: 160, generated: 46, packet: [0x08,0x01,0x91,0x00,0x60,0x63,0x25,0x64,0x5E,0x00,0x00,0x62,0x80,0xF3,0x1C,0x43,0x7C,0xE3,0x51,0x60,0x63,0x25,0x64,0x5E,0x00,0x00,0x62,0x80,0xF3,0x1C,0x43,0x7C,0xE3,0x51,0x71,0xCA,0x27,0x10,0x80,0x00,0x00,0x03,0x00,0x00,0x00,0x00,0xFD,0xD4,0x00,0x00,0x00,0x00,0xF3,0x1C,0xFD,0xD3,0x5F,0xC8,0x34,0x89,0x34,0x27,0x3F,0x3B,0x00,0x00,0x00,0x00,0x00,0x00,0x3F,0x3B,0x3F,0x3B,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x03,0x86,0x03,0x6F,0x02,0x32,0x02,0x13,0x03,0x63,0x03,0x98,0x03,0xD5,0x02,0x07,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xA0]']


class test_good(test_definition):
    name = 'Good packet w/length'
    packet = "\xAA\x08\x00\x05\x00\x02\x00\xFF\x0E\xCC"
    results = ['Packet returned: 0xAA,0x08,0x00,0x05,0x00,0x02,0x00,0xFF,0x0E,0xCC']


class test_threeGood(test_definition):
    name = 'THree good packets w/length'
    packet = "\xAA\x08\x00\x05\x00\x02\x00\xFF\x0E\xCC" * 3
    results = ['Packet returned: 0xAA,0x08,0x00,0x05,0x00,0x02,0x00,0xFF,0x0E,0xCC'] * 3


class test_doubleStart(test_definition):
    name = 'Double start bytes'
    packet = "\xAA\xAA\x08\x00\x05\x00\x02\x01\xFF\x0F\xCC"
    results = ['ERROR msg from test_receive: processReceiveBuffer could not parse buffer. Bad/incomplete packet found in buffer missing end byte 0xAA',
               'Packet returned: 0xAA,0x08,0x00,0x05,0x00,0x02,0x01,0xFF,0x0F,0xCC']


class test_incompleteFirst(test_definition):
    name = 'Incomplete packet before good packet'
    packet = "\xAA\x08\x00\x05\x00\x02\x01\xFF\x0F\xAA\x08\x00\x05\x00\x02\x01\xFF\x0F\xCC"
    results = ['ERROR msg from test_receive: processReceiveBuffer could not parse buffer. Bad/incomplete packet found in buffer missing end byte 0xAA,0x08,0x00,0x05,0x00,0x02,0x01,0xFF,0x0F',
               'Packet returned: 0xAA,0x08,0x00,0x05,0x00,0x02,0x01,0xFF,0x0F,0xCC']


class test_twoIncompleteFirst(test_definition):
    name = 'Incomplete packet before good packet'
    packet = "\xAA\x08\x00\x05\x00\x02\x01\xFF\x0F\xAA\x08\x00\x05\x00\x02\x01\xFF\x0F\xAA\x08\x00\x05\x00\x02\x01\xFF\x0F\xCC"
    results = ['ERROR msg from test_receive: processReceiveBuffer could not parse buffer. Bad/incomplete packet found in buffer missing end byte 0xAA,0x08,0x00,0x05,0x00,0x02,0x01,0xFF,0x0F',
               'ERROR msg from test_receive: processReceiveBuffer could not parse buffer. Bad/incomplete packet found in buffer missing end byte 0xAA,0x08,0x00,0x05,0x00,0x02,0x01,0xFF,0x0F',
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
    results = ['ERROR msg from test_receive: processReceiveBuffer could not parse buffer. Bad/incomplete packet found in buffer before start byte 0x01',
               'Packet returned: 0xAA,0x08,0x00,0x05,0x00,0x02,0x00,0xFE,0x0D,0xCC']


class test_badBytesBetweenPackets(test_definition):
    name = 'Bad bytes between packets'
    packet = "\xAA\x08\x00\x05\x00\x02\x00\xFE\x0D\xCC\xAA\xAA\xAA\x08\x00\x05\x00\x02\x00\xFE\x0D\xCC\x56\xAA\x08\x00\x05\x00\x02\x00\xFE\x0D\xCC\xAA\x08\x00\x05\x00\x02\x00\xFE\x0D\xCC"
    results = ['Packet returned: 0xAA,0x08,0x00,0x05,0x00,0x02,0x00,0xFE,0x0D,0xCC',
               'ERROR msg from test_receive: processReceiveBuffer could not parse buffer. Bad/incomplete packet found in buffer missing end byte 0xAA',
               'ERROR msg from test_receive: processReceiveBuffer could not parse buffer. Bad/incomplete packet found in buffer missing end byte 0xAA',
               'Packet returned: 0xAA,0x08,0x00,0x05,0x00,0x02,0x00,0xFE,0x0D,0xCC',
               'ERROR msg from test_receive: processReceiveBuffer could not parse buffer. Bad/incomplete packet found in buffer before start byte 0x56',
               'Packet returned: 0xAA,0x08,0x00,0x05,0x00,0x02,0x00,0xFE,0x0D,0xCC',
               'Packet returned: 0xAA,0x08,0x00,0x05,0x00,0x02,0x00,0xFE,0x0D,0xCC']

tests = [
    test_badChecksum,
    test_twoIncompleteFirst,
    test_incompleteFirst,
    test_good,
    test_threeGood,
    test_doubleStart,
    test_oneBadByte,
    test_twoBadBytes,
    test_badByteBeforePacket,
    test_badBytesBetweenPackets
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

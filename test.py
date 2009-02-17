print '########################################################'
print '# BEGIN TEST OUTPUT                                    #'
print '########################################################\n'

import time

import comms.protocols as protocols
import comms.protocols.IFreeEMS_Vanilla.v0_0_1.receive as receive

packets = {
    
    'Good Packet w/length': "\xAA\x08\x00\x05\x00\x02\x00\xFF\x0E\xCC",
    'Double start bytes':   "\xAA\xAA\x08\x00\x05\x00\x02\x00\xFF\x0E\xCC"

}


###############################################################################
# Stub classes implementing minimal functionality
class test_controller:

    def action(self, action, data):

        for packet in data['queue']:
            print 'Packet returned: %s' % packet.getHex()

    def log(self, module, type, message, data):
        print 'Log msg from %s (%s): %s %s' % (module, type, message, data)


###############################################################################
# Run tests
ctrl = test_controller()

try:
    # Create receive thread for testing
    rec = receive.thread('test_receive', ctrl, 'comms')

    for (test_name, test_packet) in packets.iteritems():
        print ''
        print 'Test: %s' % test_name
        print 'Sending test binary: %s' % protocols.toHex(test_packet)
        rec.received(test_packet)

        time.sleep(2)

except Exception:
    raise

finally:
    print ''
    rec.exit()

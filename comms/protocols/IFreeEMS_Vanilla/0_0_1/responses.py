


    class response(packet):
        '''Reponse packet'''

        _validation_rules = {}

        def __init__(self):
            '''Set defaults'''

            self._validation_rules = {
                'preset_payload_length': False,
                'requires_length': False,
                'firmware_type': False,
            }


        def validate(self):
            '''Validate packet based on validation rules'''
            
            rules = self._validation_rules
            pid = self.getPayloadIdInt()

            if rules['preset_payload_length']:
                # Check payload is the required length
                if rules['preset_payload_length'] != self.getPayloadLengthInt():
                    raise Exception, 'Packet type %d preset length of %s does not match the actual payload length of %s' % (pid, rules['preset_payload_length'], self.getPayloadLengthInt())
            
            if rules['requires_length']:
                # Check a length was supplied and the payload matches
                if not self.hasHeaderLengthFlag():
                    raise Exception, 'Packet type %s was expecting a length flag to be set' % pid

                length = self.getPayloadLengthParsed()
                if not length:
                    raise Exception, 'Packet type %s was expecting a length to be set' % pid

                if self.getPayloadLengthInt() != length:
                    raise Exception, 'Packet type %s, payload length of %s does not match parsed length of %s' % (pid, self.getPayloadLengthInt(), length)

            if rules['firmware_type']:
                # Check firmware type flag is set
                if self.hasHeaderProtocolFlag():
                    raise Exception, 'Packet type %s requires the firmware flag is set' % pid


        def parsePayload(self, payload):
            '''Parse the payload'''

            if self.hasHeaderLengthFlag():
                # If length set, account for 2 length bytes
                self.setPayloadLengthParsed(payload[0:2])
                self.setPayload(payload[2:])

            else:
                self.setPayload(payload)


    class responseGeneric(response):
        '''Generic EMS response for bad/not yet implemented packets'''

        def __init__(self):
            protocol.response.__init__(self)


    class responseInterfaceVersion(response):
        '''EMS response to interface version request'''

        def __init__(self):
            protocol.response.__init__(self)
            rules = self._validation_rules
            rules['requires_length'] = True


    class responseFirmwareVersion(response):
        '''EMS response to firmware version request'''

        def __init__(self):
            protocol.response.__init__(self)
            rules = self._validation_rules
            rules['requires_length'] = True


    class responseMaxPacketSize(response):
        '''EMS response to max packet length request'''

        def __init__(self):
            protocol.response.__init__(self)
            rules = self._validation_rules
            rules['preset_payload_length'] = 2

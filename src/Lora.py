import RPIlora as RPILora

class Lora():
    #port="/dev/ttyAMA0"
    #verbosity=2
    rpilora = None

    def __init__(self, port, verbosity):
        Lora.rpilora = RPILora.RPIlora(port, verbosity)
        Lora.rpilora.open()


    def get_devEUI(self , port="/dev/ttyAMA0", verbosity=1 ):
      #rpilora = RPILora.RPIlora(port, verbosity)
      if Lora.rpilora.open() :
        received = Lora.rpilora.sendCommand('sys get hweui')
        print("LoRa received message: ",received)
      else:
        errorCode = 12
      Lora.rpilora.close()


    def unlock(self,port="/dev/ttyAMA0", verbosity=1):
      #rpilora = RPILora.RPIlora(port, verbosity)
      if Lora.rpilora.open() :
        received = Lora.rpilora.sendCommand('mac forceENABLE')
        print('command: mac forceENABLE   received: '+received)
      else:
        errorCode = 12
      Lora.rpilora.close()


    def set_spreadingFactor(self ,spreadingFactor = "sf7", port="/dev/ttyAMA0", verbosity=1 ):
      #rpilora = RPILora.RPIlora(port, verbosity)
      if Lora.rpilora.open() :
        '''get channels info'''
        received = Lora.rpilora.sendCommand('mac get ch status 0')
        print('command: mac get ch status 0   received: '+received)
        received = ''
        received = Lora.rpilora.sendCommand('mac get ch status 1')
        print('command: mac get ch status 1   received: '+received)
        received = ''
        received = Lora.rpilora.sendCommand('mac get ch status 2')
        print('command: mac get ch status 2   received: '+received)
        received = ''
        received = Lora.rpilora.sendCommand('mac get ch status 3')
        print('command: mac get ch status 3   received: '+received)
        received = ''
        received = Lora.rpilora.sendCommand('mac get ch status 4')
        print('command: mac get ch status 4   received: '+received)
        received = ''
        '''frecuency'''
        received = Lora.rpilora.sendCommand('mac set ch freq 3 864000000')
        print('command: mac set ch freq 3 864000000   received: '+received)
        received = ''
        '''data rate'''
        received = Lora.rpilora.sendCommand('mac set ch drrange 3 0 7')
        print('command: mac set ch drrange 3 0 7   received: '+received)
        received = ''
        '''duty cycle'''
        received = Lora.rpilora.sendCommand('mac set ch dcycle 3 4')
        print('command: mac set ch dcycle 3 4   received: '+received)
        received = ''
        '''save'''
        received = Lora.rpilora.sendCommand('mac save')
        print('command: mac save  received: '+received)
        received = ''
        '''activate'''
        received = Lora.rpilora.sendCommand('mac set ch status 3 on')
        print('command: mac set ch status 3 on  received: '+received)
        received = ''
        '''spreading factor'''
        received = Lora.rpilora.sendCommand('radio set sf '+spreadingFactor)
        print('command: radio set sf '+spreadingFactor + '  received: '+received)
        '''adaptative data rate'''
        received = Lora.rpilora.sendCommand('mac set adr off')
        print('command: mac set adr off'+ '  received: '+received)
      else:
        errorCode = 12
      Lora.rpilora.close()


    def loRaJoin(self, deveui, appeui, appkey, port="/dev/ttyAMA0", verbosity=1):
      #rpilora = RPILora.RPIlora(port,verbosity)
      if Lora.rpilora.open() :
        Lora.rpilora.sendCommand('sys reset')
        received = Lora.rpilora.sendCommand('mac set deveui ' + deveui)
        if received == 'ok':
          received = Lora.rpilora.sendCommand('mac set appeui ' + appeui)
          if received == 'ok':
            received = Lora.rpilora.sendCommand('mac set appkey ' + appkey)
            if received == 'ok':
              received = Lora.rpilora.sendCommand('mac join otaa')
              if received == 'ok':
                received = Lora.rpilora.ReceiveUntil('\r\n', 'ERROR', 20).replace('\r\n', '')
                if received == 'accepted':
                  if rpilora.verbosity >= 1 : print('join successful')
                  received = Lora.rpilora.sendCommand('mac save')
                  if received != 'ok':
                    errorMessage = 'mac save failed: ' + received
                    errorCode = 1
                else:
                  errorMessage = 'mac join otaa failed: ' + received
                  errorCode = 2
              else:
                errorMessage = 'mac join otaa failed: ' + received
                errorCode = 3
            else:
              errorMessage = 'mac set appkey failed: ' + received
              errorCode = 4
          else:
            errorMessage = 'mac set appeui failed: ' + received
            errorCode = 5
        else:
          errorMessage = 'mac set deveui failed: ' + received
          errorCode = 6
      else:
        errorCode = 12
      Lora.rpilora.close()

    def send(self, send, receive = False, channel= 1, port="/dev/ttyAMA0", verbosity=1):
      #rpilora = RPILora.RPIlora(port,verbosity)
      if Lora.rpilora.open() :
        command_string = 'mac tx '
        if not receive:
            command_string += 'un'
       # if not receive:
         # command_string += 'un'
        #command_string += 'uncnf ' + str(channel) + ' ' + send
        command_string += 'cnf ' + str(channel) + ' ' + send
        if Lora.rpilora.verbosity >= 2: print("LoRa Send command: ",command_string)
        print("")
        received = Lora.rpilora.sendCommand(command_string)
        if Lora.rpilora.verbosity >= 2: print("LoRa Response received = ", received)
        if received == 'ok':
          # send command syntax OK at this point
          if receive:
            # rx data present before mac_tx_ok
            print('LoRa waiting to receive....')
            loop_flag = True
            received_data = ""
            while loop_flag:
              received = Lora.rpilora.ReceiveUntil('\r\n', 'ERROR', 50).replace('\r\n', '')
              if received == 'mac_tx_ok':
                # we are done receiving
                print('LoRa RX data:' + received_data)
                loop_flag = False
                return received_data
              elif received.startswith('mac_rx '):
                received_data += received.split()[1]
              else:
                loop_flag = False
                errorMessage = 'send failed: ' + received
                errorCode = 13
          else:
            received = Lora.rpilora.ReceiveUntil('\r\n', 'ERROR', 20).replace('\r\n', '')
            if received == 'mac_tx_ok':
              if Lora.rpilora.verbosity >= 1 : print('ACK from pycom RECEIVED')
              return None
            else:
              errorMessage = 'send failed: ' + received
              errorCode = 14
        else:
          if Lora.rpilora.verbosity >= 2: print("LoRa Module Error message : ",command_string , " failed: ",received)
          print("")
          errorMessage = command_string + ' failed: ' + received
          errorCode = 15
        #Lora.rpilora.close()

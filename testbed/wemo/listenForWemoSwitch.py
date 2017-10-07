import os, sys, requests, json, time, argparse
from datetime import datetime
from ouimeaux.environment import Environment
from ouimeaux.signals import statechange, receiver
parser = argparse.ArgumentParser()
parser.add_argument("-set", action = "store_true")
parser.add_argument("-isSub", action = "store_true")
parser.add_argument("-port", type = int, default = 10085)
options = parser.parse_args()
env = Environment(bind = "0.0.0.0:{}".format(options.port), with_subscribers = options.isSub)
env.start()
env.discover(5)
switch = env.get_switch('WeMo Switch1')
@receiver(statechange, sender=switch)
def switch_toggle(device, **kwargs):
  print device, kwargs['state']
if options.set:
  switch.on()
  print(time.strftime("%H%M%S"))
  sys.exit(0)
else:
  switch.off()
while switch.get_state(force_update = True) == 0:
  time.sleep(1)
  print(switch.get_state(force_update = True))
print(time.strftime("%H%M%S"))

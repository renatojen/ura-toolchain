#
#  test.py
#  Runs workspace tests defined in inputs.txt
#  and outputs.txt
#  Created by Renato Jensen Filho on 02/07/19.
#  Copyright © 2019 IBM. All rights reserved.
#

import json
from os import getenv
from datetime import datetime
import requests
import sys

wksp_id = getenv("TARGET_WORKSPACE_ID", "")
apikey = getenv("API_KEY_TRG[0]", "")
user = "apikey"
inputs = []
outputs = []
i=0

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

def ts():
  return '{:%Y.%m.%d-%H.%M.%S}'.format(datetime.now())

def loadInputs():
  global inputs
  with open("inputs.txt", "r", encoding='utf-8') as f:
    inputs = f.readlines()

def loadOutputs():
  global outputs
  with open("outputs.txt", "r", encoding='utf-8') as f:
    outputs = f.readlines()

#initialization
def init():
  global inputs, outputs
  loadInputs()
  loadOutputs()
  if wksp_id == "" or apikey == "" or inputs == [] or outputs == [] or len(inputs) != len(outputs):
    print(ts() + " - ERROR: Initialization error")
    print(wksp_id)
    print(apikey)
    print(inputs)
    print(outputs)
    sys.exit(1)

def send_message(_input, context):
  global i
  i+=1
  params = (
    ('version', '2019-02-28'),
  )
  print(ts() + " - Running test #" + str(i) + " with input: " + _input)
  data = {"input": {"text":  _input }, "context": context}
  data = json.dumps(data)
  try:
    r = requests.post('https://gateway.watsonplatform.net/assistant/api/v1/workspaces/' + wksp_id + '/message', params=params, headers=headers, data=data, auth=(user, apikey))
  except:
    print(ts() + " - ERROR: Request failed.")
    sys.exit(2)
  if r.status_code != 200:
    print(ts() + " - ERROR: Request returned code: " + str(r.status_code))
    sys.exit(3)
  response = r.json()
  #print(response)
  if response['output']['text'] == []:
    response['output']['text'].append('')
  if response['output']['text'][0] != outputs[i-1]:
    print(ts() + " - ERROR: Unexpected test response:")
    print(ts() + " - Received Intent: " + response['intents'][0]['intent'])
    print(ts() + " - Expected Output: " + outputs[i-1])
    print(ts() + " - Received Output: " + response['output']['text'][0])
    sys.exit(4)
  print(ts() + " - Received Intent: " + response['intents'][0]['intent'])
  print(ts() + " - Expected Output: " + outputs[i-1])
  print(ts() + " - Received Output: " + response['output']['text'][0])
  print(ts() + " - Test #" + str(i) +  " finished successfully.")
  return response['context'] 
  
###

init()
for j in range(len(outputs)):
  inputs[j] = inputs[j].replace('\n', '')
  outputs[j] = outputs[j].replace('\n', '')
  outputs[j] = outputs[j].replace('\\n', '\n')
context = {}
for k in inputs:
  context = send_message(k, context)

print(ts() + " - ALL " + str(i) +  " TESTS FINISHED SUCCESSFULLY.")

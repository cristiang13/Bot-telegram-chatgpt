import os
import openai
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def getResponseChatGpt(input):
  
  if 'variables' in input:
    print(input['variables']['model'])
    print(input['variables']['temperature'])
    print(input['variables']['max_tokens'])
    print(input['variables']['top_p'])
    print(input['variables']['frequency_penalty'])
    print(input['variables']['presence_penalty'])

  # try:
  if 'variables' in input:
      response = openai.Completion.create(
      model=input['variables']['model'],
      prompt=input['message'],
      temperature=input['variables']['temperature'],
      max_tokens=input['variables']['max_tokens'],
      top_p=input['variables']['top_p'],
      frequency_penalty=input['variables']['frequency_penalty'],
      presence_penalty=input['variables']['presence_penalty']
    ) 
  else:
    response = openai.Completion.create(
      model="text-davinci-003",
      prompt=input['message'],
      temperature=1,
      max_tokens=2600,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0
    )
  
  return(response['choices'][0]['text'])  
        

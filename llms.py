from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI

def text_davinci():
    return OpenAI(model='text-davinci-003', streaming= True)

def gpt3():
    return ChatOpenAI(model='gpt-3.5-turbo-0125', streaming= True)

def gpt4():
    return ChatOpenAI(model='gpt-4-0125-preview', streaming= True)
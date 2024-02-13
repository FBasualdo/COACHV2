
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.llms import openai
import faiss
from langchain.docstore import InMemoryDocstore
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import pinecone
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import pinecone
from os import getenv
import cohere

load_dotenv()

class Acknowledge_Chain():
    def __init__(self, llm, template):
        self.template = template
        self.set_prompt()
        self.llm = llm
        self.create_chain()
        
    def set_prompt(self):
        self.prompt = PromptTemplate(
            input_variables=["last_message", "bullet"],
            template= self.template
        )

    def create_chain(self):
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt, verbose= True)
    
    def run_chain(self, last_message, bullet):
        response = self.chain.run({'last_message': last_message,
                                   'bullet': bullet,
                                   'output': ''})
        return response

class General_Chain():
    def __init__(self, llm, template):
        self.template = template
        self.set_prompt()
        self.llm = llm
        self.create_chain()
        
    def set_prompt(self):
        self.prompt = PromptTemplate(
            input_variables=["instruction", "message"],
            template= self.template
        )

    def create_chain(self):
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt, verbose= True)
    
    def run_chain(self, instruction, message):
        response = self.chain.run({'instruction': instruction,
                                   'message': message,
                                   'output': ''})
        return response


class General2_Chain():
    def __init__(self, llm, template):
        self.template = template
        self.set_prompt()
        self.llm = llm
        self.create_chain()
    
    def set_prompt(self):
        self.prompt = PromptTemplate(
            input_variables=["instruction", "message"],
            template= self.template
        )

    def create_chain(self):
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt, verbose= True)
    
    def run_chain(self, instruction, message, outcome):
        response = self.chain.run({'instruction': instruction,
                                   'message': message,
                                   'outcome': outcome,
                                   'output': ''})
        return response

class Bullet_maker():
    def __init__(self, llm, template):
        self.template = template
        self.set_prompt()
        self.llm = llm
        self.create_chain()
        
    def set_prompt(self):
        self.prompt = PromptTemplate(
            input_variables=["bullet", "message"],
            template= self.template
        )

    def create_chain(self):
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt, verbose= True)
    
    def run_chain(self, bullet, message):
        response = self.chain.run({'bullet': bullet,
                                   'message': message,
                                   'output': ''})
        return response
    

class YesNo_Bot():
    def __init__(self, llm, template) -> None:
        self.template = template
        self.set_prompt()
        self.llm = llm
        self.create_chain()

    def set_prompt(self):
        self.prompt = PromptTemplate(
            input_variables=["question", "conversation"],
            template= self.template
        )

    def create_chain(self):
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt, verbose= True)
    
    def run_chain(self, question, conversation, answer):
        response = self.chain.run({'question' : question,
                                   'conversation' : conversation,
                                   'answer': answer,
                                   'output': ''})
        return response


class QuestionMaker():
    def __init__(self, llm, template) -> None:
        self.template = template
        self.set_prompt()
        self.llm = llm
        self.create_chain()

    def set_prompt(self):
        self.prompt = PromptTemplate(
            input_variables=["conversation"],
            template= self.template
        )

    def create_chain(self):
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt, verbose= True)
    
    def run_chain(self, conversation):
        response = self.chain.run({#    'chat_history': message_history.messages,
                                   'conversation' : conversation,
                                   'output': ''})
        return response
    

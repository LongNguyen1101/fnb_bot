from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv(override=True)

class BookingChain():
    def __init__(self):
        self.model_name = os.getenv('MODEL_NAME')
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            api_key=self.api_key
        )
    
    def check_phone_chain(self) -> LLMChain:
        with open("bot/chain/prompts/check_phone_number_prompt.txt", encoding="utf-8") as f:
            prompt_text = f.read()
        
        prompt = PromptTemplate.from_template(prompt_text)
        chain = prompt | self.llm
        return chain
    
    def extract_booking_info(self) -> LLMChain:
        with open("bot/chain/prompts/extract_booking_info_prompt.txt", encoding="utf-8") as f:
            prompt_text = f.read()
        
        prompt = PromptTemplate.from_template(prompt_text)
        chain = prompt | self.llm
        return chain
    
    def ask_correct_booking_info(self) -> LLMChain:
        with open("bot/chain/prompts/ask_correct_bookinh_info_prompt.txt", encoding="utf-8") as f:
            prompt_text = f.read()
        
        prompt = PromptTemplate.from_template(prompt_text)
        chain = prompt | self.llm
        return chain
    
    def check_booking_relatedness(self) -> LLMChain:
        with open("bot/chain/prompts/check_booking_relatedness_prompt.txt", encoding="utf-8") as f:
            prompt_text = f.read()
        
        prompt = PromptTemplate.from_template(prompt_text)
        chain = prompt | self.llm
        return chain
    
    def classify_continue_booking(self) -> LLMChain:
        with open("bot/chain/prompts/classify_continue_booking_prompt.txt", encoding="utf-8") as f:
            prompt_text = f.read()
        
        prompt = PromptTemplate.from_template(prompt_text)
        chain = prompt | self.llm
        return chain
    
    def confirm_reservation_intent_classification(self) -> LLMChain:
        with open("bot/chain/prompts/confirm_reservation_intent_classification_prompt.txt", encoding="utf-8") as f:
            prompt_text = f.read()
        
        prompt = PromptTemplate.from_template(prompt_text)
        chain = prompt | self.llm
        return chain
    
    def ask_modify_reservation(self) -> LLMChain:
        with open("bot/chain/prompts/ask_modify_reservation_prompt.txt", encoding="utf-8") as f:
            prompt_text = f.read()
        
        prompt = PromptTemplate.from_template(prompt_text)
        chain = prompt | self.llm
        return chain
    
    def extract_modify_info(self) -> LLMChain:
        with open("bot/chain/prompts/extract_modify_info_prompt.txt", encoding="utf-8") as f:
            prompt_text = f.read()
        
        prompt = PromptTemplate.from_template(prompt_text)
        chain = prompt | self.llm
        return chain
    
    def extract_modify_again_info(self) -> LLMChain:
        with open("bot/chain/prompts/extract_modify_again_info_prompt.txt", encoding="utf-8") as f:
            prompt_text = f.read()
        
        prompt = PromptTemplate.from_template(prompt_text)
        chain = prompt | self.llm
        return chain
    
    def ask_cancel_reservation(self) -> LLMChain:
        with open("bot/chain/prompts/ask_cancel_reservation_prompt.txt", encoding="utf-8") as f:
            prompt_text = f.read()
        
        prompt = PromptTemplate.from_template(prompt_text)
        chain = prompt | self.llm
        return chain
    
    def extract_cancel_info(self) -> LLMChain:
        with open("bot/chain/prompts/extract_cancel_info_prompt.txt", encoding="utf-8") as f:
            prompt_text = f.read()
        
        prompt = PromptTemplate.from_template(prompt_text)
        chain = prompt | self.llm
        return chain
    
    def extract_salutaion(self) -> LLMChain:
        with open("bot/chain/prompts/extract_salutaion_prompt.txt", encoding="utf-8") as f:
            prompt_text = f.read()
        
        prompt = PromptTemplate.from_template(prompt_text)
        chain = prompt | self.llm
        return chain
    
    def check_first_intent(self) -> LLMChain:
        with open("bot/chain/prompts/check_first_intent_prompt.txt", encoding="utf-8") as f:
            prompt_text = f.read()
        
        prompt = PromptTemplate.from_template(prompt_text)
        chain = prompt | self.llm
        return chain
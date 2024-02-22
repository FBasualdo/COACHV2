from chains import General_Chain, General2_Chain, Bullet_maker, YesNo_Bot, QuestionMaker, Acknowledge_Chain
from dotenv import load_dotenv
from question_like import question_list_first_phase, more_info_questions, question_list_second_phase, question_list_third_phase, words_count, question_parser
from templates import get_bullet_template_second, get_general2_template, get_general_template, get_bullet_template, def_bot_template,get_aknowledge_template, question_maker_bot_template
from llms import gpt3, gpt4
import json
from time import sleep

load_dotenv()
general_2_bot = General2_Chain(llm= gpt4(), template= get_general2_template())
general_bot = General_Chain(llm= gpt4(), template= get_general_template())
bullet_bot = Bullet_maker(llm= gpt4(), template= get_bullet_template())
bullet_bot_2 = Bullet_maker(llm= gpt4(), template= get_bullet_template_second())
ready_bot = YesNo_Bot(llm= gpt3(), template= def_bot_template())
question_maker = QuestionMaker(llm= gpt4(), template= question_maker_bot_template())


def conversation_parser(conversations: list):
    parsed_result = """"""
    for conversation in conversations:
        parsed_result += f"""AI: {conversation['Ai']}\nPATIENT: {conversation['patient']}\n"""
        
    return parsed_result

def save_conversation_state(conversation_state):
    with open('conversation_state.json', 'w') as file:
        json.dump(conversation_state, file)


def get_response_second_phase(status:int, conversation:list, last_ai_question:str, user_input:str, interaction_counter:int, flow_counter:int):
    keys = list(question_list_second_phase.keys())
    # print(keys)
    match flow_counter:
        case -1:
            # print("ACACACA EN -1")
            ai_question = keys[0]
            flow_counter = 0
            
        case _:
            conversation.append({'Ai': last_ai_question, 'patient': user_input})
            is_ready = ready_bot.run_chain(question= last_ai_question, conversation= conversation_parser(conversation), answer= user_input)
            print(is_ready)
            if is_ready.lower() == 'yes':
                conversation = []
                interaction_counter = 0
                if flow_counter + 1 <= len(keys) - 1:
                    flow_counter += 1

                    print("THIS IS USER INPUT", user_input)
                    bullet_count = words_count(user_input)
                    print("THIS IS BULLET COUNT", bullet_count)
                    bullet_list = bullet_bot.run_chain(bullet= bullet_count, message= user_input)
                    print("THIS IS BULLET LIST 1", bullet_list)
                    bullet_list = bullet_bot_2.run_chain(bullet= bullet_list, message= user_input)
                    print("THIS IS BULLET LIST 2", bullet_list)
                    ai_question = general_bot.run_chain(instruction= question_list_second_phase[keys[flow_counter]], message= user_input)
                else:
                    status = 3
                    flow_counter = -1
                    bullet_count = words_count(user_input)
                    bullet_list = bullet_bot.run_chain(bullet= bullet_count, message= user_input)
                    bullet_list = bullet_bot_2.run_chain(bullet= bullet_list, message= user_input)
                    ai_question = f"""{bullet_list}"""

                    return  save_conversation_state({
                            'status': status,
                            'conversation': conversation,
                            'last_ai_question': ai_question,
                            'user_input': user_input,
                            'interaction_counter': interaction_counter,
                            'flow_counter': flow_counter
    })
            else:
                interaction_counter += 1
                ai_question = question_maker.run_chain(conversation= conversation_parser(conversation))
        
            if flow_counter == 1 and is_ready.lower() == 'yes':
                aknowledge_bot = Acknowledge_Chain(llm= gpt3(), template= get_aknowledge_template())
                acknowledge = aknowledge_bot.run_chain(last_message= user_input, bullet= bullet_list)
                ai_question = f"""{acknowledge} \n {bullet_list} \n {ai_question}"""
            elif is_ready.lower() == 'yes':
                ai_question = f"""{bullet_list} \n {ai_question}"""
            else:
                ai_question = f"""{ai_question}"""

    save_conversation_state({
        'status': status,
        'conversation': conversation,
        'last_ai_question': ai_question,
        'user_input': user_input,
        'interaction_counter': interaction_counter,
        'flow_counter': flow_counter
    })


def get_response_third_phase(outcome: str, status:int, conversation:list, last_ai_question:str, user_input:str, interaction_counter:int, flow_counter:int):
    keys = list(question_list_third_phase.keys())
    if status == 3:
        match flow_counter:
            case -1:
                ai_question = keys[0]
                flow_counter = 0
            case 0:
                outcome = general_bot.run_chain(instruction= question_list_third_phase[keys[flow_counter]], message= user_input)
                flow_counter += 1
                ai_question = keys[flow_counter].format(outcome= outcome)
            case 1:
                if user_input.lower() == 'y':
                    flow_counter += 1
                    ai_question = general_bot.run_chain(instruction= question_list_third_phase[keys[flow_counter + 1]], message= outcome)
                    question = f"""{keys[flow_counter]}
{ai_question}"""
                    ai_question = question
                    flow_counter += 1
                    
                else:
                    flow_counter = -1
                    ai_question= keys[flow_counter -1]
            case _:      
                conversation.append({'Ai': last_ai_question, 'patient': user_input})
                is_ready = ready_bot.run_chain(question= last_ai_question, conversation= conversation_parser(conversation), answer= user_input)
                print(is_ready)
                if is_ready.lower() == 'yes' or interaction_counter == 2:
                    conversation = []
                    interaction_counter = 0

                    bullet_count = words_count(user_input)
                    bullet_list = bullet_bot.run_chain(bullet= bullet_count, message= user_input)
                    bullet_list = bullet_bot_2.run_chain(bullet= bullet_list, message= user_input)
                    formatted_question = question_list_third_phase[keys[flow_counter]].replace("{outcome}", outcome)
                    print("THIS IS FORMATTED QUESTION", formatted_question)
                    ai_question = general_bot.run_chain(instruction= formatted_question, message= user_input)
                    flow_counter += 1
                    print("THIS IS FLOW COUNTER", flow_counter)
                else:
                    interaction_counter += 1
                    ai_question = question_maker.run_chain(conversation= conversation_parser(conversation))
            
                if flow_counter == 4 and is_ready.lower() == 'yes':
                    aknowledge_bot = Acknowledge_Chain(llm= gpt3(), template= get_aknowledge_template())
                    acknowledge = aknowledge_bot.run_chain(last_message= user_input, bullet= bullet_list)
                    ai_question = f"""{acknowledge} \n {bullet_list} \n {ai_question}"""
                elif is_ready.lower() == 'yes':
                    ai_question = f"""{bullet_list} \n {ai_question}"""
                else:
                    ai_question = f"""{ai_question}"""
            
        save_conversation_state({
            'status': status,
            'conversation': conversation,
            'last_ai_question': ai_question,
            'user_input': user_input,
            'interaction_counter': interaction_counter,
            'flow_counter': flow_counter,
            'outcome': outcome
        })
    
def run():
    print("Welcome to the conversation")
    while True:
        try:
            with open('conversation_state.json', 'r') as file:
                conversation_state = json.load(file)
        except FileNotFoundError:
            conversation_state = {
                'status': 1,
                'conversation': [],
                'last_ai_question': '',
                'user_input': '',
                'interaction_counter': 0,
                'flow_counter': -1,
                'outcome': ''
            }
        status = conversation_state["status"]
        flow_counter = conversation_state["flow_counter"]
        interaction_counter = conversation_state["interaction_counter"]
        last_ai_question = conversation_state["last_ai_question"]
        conversation = conversation_state["conversation"]
        user_input = conversation_state["user_input"]
        outcome = conversation_state.get("outcome", "")
 
        if status == 1:
            for question in question_list_first_phase:
                print(question)
                sleep(4)
            answer = input("You: ")
            if answer == "yes".lower():
                status = 2
                flow_counter = -1
            elif answer == "no".lower():
                exit()
            elif answer == "info".lower():
                for info in more_info_questions:
                    print(info)
                    sleep(4)
                answer = input("You: ")
                if answer == "yes".lower():
                    status = 2
                    flow_counter = -1
                elif answer == "no".lower():
                    exit()
                            
        if status == 2:
            if flow_counter == -1:
                # print("IN -1")
                get_response_second_phase(status= status, conversation= conversation, last_ai_question= last_ai_question, user_input= user_input, interaction_counter= interaction_counter, flow_counter= flow_counter)
            else:
                print(last_ai_question)
                user_input = input("You: ")
                get_response_second_phase(status= status, conversation= conversation, last_ai_question= last_ai_question, user_input= user_input, interaction_counter= interaction_counter, flow_counter= flow_counter)
        elif status == 3:
            if flow_counter == -1:
                get_response_third_phase(outcome= outcome, status= status, conversation= conversation, last_ai_question= last_ai_question, user_input= user_input, interaction_counter= interaction_counter, flow_counter= flow_counter)
            else:
                print(last_ai_question)
                user_input = input("You: ")
                get_response_third_phase(outcome= outcome, status= status, conversation= conversation, last_ai_question= last_ai_question, user_input= user_input, interaction_counter= interaction_counter, flow_counter= flow_counter)
run()
import requests
from openai import OpenAI
import torch

def get_response(instruction,inputs):
    return get_gpt_response(instruction,inputs)



def get_gpt_response(instruction, input): 
    print("get_gpt_response")
    url = ""  
    headers = {  
        "api-key": "",  
        "Content-Type": "application/json"  
    }  
    data = {  
        "messages": [  
            {  
                "role": "system",  
                "content": instruction
            },  
            {  
                "role": "user",  
                "content": input
            }  
        ],  
        "stream": False  
    }  

    response = requests.post(url, headers=headers, json=data)  

    print(f"Status Code: {response.status_code}")  

    try:  
        response_json = response.json()  
        print(response_json)
    except requests.JSONDecodeError:  
        print("Failed to decode JSON.")  
        print("Response content:", response.text)  
        return None  


    response = response_json['choices'][0]['message']['content']  
    return response
  

def get_llm_response(instruction, input, pipeline):
    print("LLM")
    messages = [
        {"role": "system", "content": instruction},
        {"role": "user", "content": input},
    ]

    prompt = pipeline.tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    print("prompt:",prompt)

    terminators = [
        pipeline.tokenizer.eos_token_id,
        pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]

    outputs = pipeline(
        prompt,
        max_new_tokens=2560,
        eos_token_id=terminators,
        do_sample=True,
        temperature=0.1,
        top_p=0.9,
    )
    res=outputs[0]["generated_text"][len(prompt):]
    return res


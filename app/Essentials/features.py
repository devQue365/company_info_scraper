import os
from openai import OpenAI
from ast import literal_eval
with open("app/temp.txt", 'r') as fh:
    raw_htm = fh.read()

token = "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" # os.environ["GITHUB_TOKEN"]
endpoint = "https://models.github.ai/inference"
model_name = "openai/gpt-4o-mini"

client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

review_model_instructions = '''
"You are a helpful assistant that enhances customer reviews. "
    "When given a review, correct grammar, fix casing issues (e.g., 'SEnior' → 'Senior'), "
    "and rewrite it with improved clarity and tone. Also identify the sentiment."
    "if the review does not make sense or is garbage, dispose it and don't show that"
    "Don't include any additional text/information like ```json or any other label, Only produce the output as a list of dictonaries"
    You will be provided json input and you have to perform these operation on that data and return the enhanced and polished version along with additional fields highlighting the sentiment of review.
'''

location_model_instructions = '''
You are also a precise data cleaner and location validator. Your job is to accept JSON input containing a company's office locations, check and correct the locations, and return only the cleaned JSON.

Instructions:
- Input is a JSON object which would include compan's office locatiiiiions for a particular region like US.
- Validate each location: keep only real-world, well-known city or regional locations.
- Discard invalid, misspelled, fictional, or empty entries.
- Add missing locations if important ones are clearly missing, using reliable geographic knowledge.
- DO NOT invent or guess loosely — only add accurate, major cities tied to real companies when strongly implied.
- Output only valid entries in the same format. Do not add any explanation or extra information.

Return ONLY the JSON object in the same format as of input with enhanced cleaning and additions if required and no extra information like — no extra text, no markdown, no code block.
"If no cleaning required then return None !"
'''
extract_insights = [{
    'type': 'function',
    'function': {
        'name': 'gd_review',
        'description': 'transform raw reviews into polished, engaging, and emotionally resonant summaries—while preserving the core message and authenticity of the original and generate the sentiment of the review."Prserve the order"',
        'parameters': {
            'type': 'object',
            'properties': {
                # 'ceo': {
                #     'type': 'string',
                #     'description': 'Name of the CEO of the company.'
                # },
                # 'ceo_approval': {
                #     'type': 'string',
                #     'description': 'CEO approval rating.'
                # },

                'reviews': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'reviewer_name': {
                                'type': 'string',
                                'description': 'Name of the reviewer.'
                            },
                            'reviewer_job_role': {
                                'type': 'string',
                                'description': 'Job role of the reviewer.'
                            },
                            'reviewer_work_location': {
                                'type': 'string',
                                'description': 'The office branch where the reviewer works.'
                            },
                            'reviewer_status': {
                                'type': 'string',
                                'description': 'The current working status of the reviewer.'
                            },
                            'review_date': {
                                'type': 'string',
                                'description': 'Date of the review.'
                            },
                            'review_title': {
                                'type': 'string',
                                'description': 'Title of the review.'
                            },
                            'pros': {
                                'type': 'string',
                                'description': 'Pros mentioned in the review.'
                            },
                            'cons': {
                                'type': 'string',
                                'description': 'Cons mentioned in the review.'
                            },
                            'rating': {
                                'type': 'number',
                                'description': 'Rating given by the reviewer.'
                            }
                        },
                        'required': ['reviewer_job_role', 'reviewer_work_location', 'reviewer_status', 'review_date', 'review_title', 'pros', 'cons', 'rating'],
                        "additionalProperties": False
                    },
                },
            },
            'required': ['reviews'],
            "additionalProperties": False
        },
    }
}]

message_history = [
        {
            "role": "system",
            "content": review_model_instructions,
        },
        {
            "role": "system",
            "content": location_model_instructions,
        },
]

def assistant_call(input_data):
    try:
        global message_history
        # add the input data to message history
        message_history.append(
            {
                "role": "user",
                "content": f"Clean {input_data} if needed else return None"
            }
        )
        response = client.chat.completions.create(
            messages=message_history,
            # instructions = role_model,
            store = True,
            temperature=0.2,
            # top_p=1.0,
            # max_tokens=1000,
            # tools=extract_insights,
            # tool_choice = "auto",
            model=model_name
        )
        output = literal_eval(response.choices[0].message.content)
        return output
    except Exception as e:
        print(f"\033[31m\033[1mError : {str(e)}\033[0m")
        return None

# output_dict = literal_eval(output)
# print(json_response)
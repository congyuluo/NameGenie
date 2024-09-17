from openai import OpenAI
from threading import Thread
from intelij_helpers import print_red
import common

client = OpenAI(api_key=common.API_KEY)


def query_gpt(prompt, model="gpt-4o", max_tokens=4096, stop_after=12, sys_content="This is a new conversation."):
    # Create a thread to handle the API call
    def api_call(response_list):
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": sys_content},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens
        )
        response_list.append(response.choices[0].message.content)

    # Store the response in a list to access it from the thread
    response_list = []
    thread = Thread(target=api_call, args=(response_list,))
    thread.start()

    # Wait for the thread to complete or timeout
    thread.join(timeout=stop_after)
    if thread.is_alive():
        # Optionally handle the case where the thread is still running (e.g., try to cancel the thread)
        print_red("Query timed out.", pause=False)
        # kill the thread
        return None  # or appropriate error handling
    else:
        return response_list[0] if response_list else None


def get_single_query(segment: str, standards: str, prior_error_message: str) -> str:
    standards_prompt = f"Refactor the code segment according to the following standards. " \
                       "Do not add or remove any code, only modify variable, function, and class names. " \
                       "Keep original indentation" \
                       "Only response needed is source code without any additions. The response will be pieced into " \
                       f"larger program, do not contain any non-java response. " \
                       f"segment. {prior_error_message}\n"
    # Assemble prompt
    for standard in standards:
        standards_prompt += f"- {standard}\n"
    standards_prompt += "Do not generate additional constructors " \
                        f"for class definitions. DO NOT add unnecessary words to single word names just to follow " \
                        f"camelcase. Do not change all upper case names into camel case unless you are certain that the variable is not a constant." \
                        f"Change overly short names to meaningful names. Do not change non-english names. ONLY MAKE CHANGES YOU ARE SURE TO BE CORRECT. If the code already" \
                        f" follows this coding convention, say 'the provided code already follows convention'. \n"
    query_response = query_gpt(segment, sys_content=standards_prompt)
    if query_response is None:
        return None
    if query_response.startswith("```java\n"):
        query_response = query_response[8:]
    if query_response.endswith("\n```"):
        query_response = query_response[:-4]
    return query_response

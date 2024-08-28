from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()


def call_openAI(name: str, age: int, gender: str, weight: int, height: int, goal: str, training_frequency: int,
                fitness_level: str) -> str:
    api_key = os.getenv('API_KEY')

    if not api_key:
        raise ValueError("API_KEY is missing. Please check your .env file.")

    client = OpenAI(api_key=api_key)

    prompt = (
        f"Create a personalized exercise program for a {gender} named {name}, "
        f"who is {age} years old, weighs {weight} kg, and is {height} cm tall. "
        f"The goal is to {goal}. "
        f"Fitness level: {fitness_level}. "
        f"Training frequency: {training_frequency} times per week. "
        f"Ensure that the program includes exactly {training_frequency} training sessions per week, "
        f"distributed evenly throughout the week. "
        f"Please provide a detailed plan with structured steps."
    )

    try:
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.7,
        )

        response = completion.choices[0].message.content.strip()
        print("Successfully called OpenAI API for exercise program.")  # הודעה על הצלחה
        return response

    except Exception as e:
        print(f"Error in OpenAI API call: {e}")
        return "An error occurred while generating the program."


def accpected_result(program: str, time: str, weight: int, height: int, name: str, gender: str) -> str:
    api_key = os.getenv('API_KEY')
    if not api_key:
        raise ValueError("API_KEY is missing. Please check your .env file.")
    client = OpenAI(api_key=api_key)
    prompt=(f"give me the expected result for this program {program} if the user will follow this program for {time}"
            f"the user wieght is {weight} and hes height is {height} and hes gender is {gender}"
            f"and hes name is {name}"
            f" you have all the information about the user in the program, you can see hes name,age,gender,"
            f"wegiht,height,goal and training frequency to predice the accpected result for him and give him some motivation to keep follow the plan."
            f"please talk more and give a lot of motivation!"
            f"give me the result only in kg")
    try:
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.9,
        )

        response2 = completion.choices[0].message.content.strip()
        print("Successfully called OpenAI API for expected result.")  # הודעה על הצלחה
        return response2

    except Exception as e:
        print(f"Error in OpenAI API call: {e}")
        return "An error occurred while generating the expected result."


def ask_openai(prompt: str) -> str:
    api_key = os.getenv('API_KEY')

    if not api_key:
        raise ValueError("API_KEY is missing. Please check your .env file.")

    client = OpenAI(api_key=api_key)

    try:
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.7,
        )

        response = completion.choices[0].message.content.strip()
        print("Successfully called OpenAI API for a custom prompt.")  # הודעה על הצלחה
        return response

    except Exception as e:
        print(f"Error in OpenAI API call: {e}")
        return "An error occurred while processing your request."


def call_openAI_for_fact() -> str:
    api_key = os.getenv('API_KEY')

    if not api_key:
        raise ValueError("API_KEY is missing. Please check your .env file.")

    client = OpenAI(api_key=api_key)

    prompt = "Give me a random fitness or well-being fact."

    try:
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.7,
        )

        response = completion.choices[0].message.content.strip()
        print("Successfully called OpenAI API for a random fitness fact.")  # הודעה על הצלחה
        return response

    except Exception as e:
        print(f"Error in OpenAI API call: {e}")
        return "An error occurred while generating the fitness fact."


def get_muscles_sugg_from_openai(muscle: str) -> str:
    api_key = os.getenv('API_KEY')

    if not api_key:
        raise ValueError("API_KEY is missing. Please check your .env file.")

    client = OpenAI(api_key=api_key)

    prompt = f"Give me some tips on how to develop the {muscle} muscles effectively."

    try:
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7,
        )

        # Get the response from OpenAI
        response = completion.choices[0].message.content.strip()

        # Split the response by the numbered points to add line breaks or list items
        formatted_response = response.replace('1.', '<br>1.').replace('2.', '<br>2.').replace('3.', '<br>3.') \
            .replace('4.', '<br>4.').replace('5.', '<br>5.').replace('6.', '<br>6.')

        print(f"Successfully called OpenAI API for muscle suggestion: {formatted_response}")
        return formatted_response

    except Exception as e:
        print(f"Error in OpenAI API call: {e}")
        return "An error occurred while generating the suggestion."
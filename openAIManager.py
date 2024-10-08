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
        print("Successfully called OpenAI API for exercise program.")
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
        print("Successfully called OpenAI API for expected result.")
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
        print("Successfully called OpenAI API for a custom prompt.")
        return response

    except Exception as e:
        print(f"Error in OpenAI API call: {e}")
        return "An error occurred while processing your request."



def ai_suggestions(user_name: str, age: int, gender: str, weight: float, height: float, fitness_goal: str,
                   avg_training_frequency: float, avg_weight_change: float, training_frequency: int,
                   fitness_level: str, program: str) -> str:
    """
    Generate AI suggestions for the user based on detailed user data and progress.

    Parameters:
    - user_name (str): The name of the user.
    - age (int): The user's age.
    - gender (str): The user's gender.
    - weight (float): The user's current weight.
    - height (float): The user's height.
    - fitness_goal (str): The user's fitness goal.
    - avg_workout_frequency (float): The user's average workout frequency per week.
    - avg_weight_change (float): The average weight change per week.
    - training_frequency (int): The number of times the user trains per week.
    - fitness_level (str): The user's fitness level (e.g., beginner, intermediate, advanced).

    Returns:
    - str: AI-generated suggestions for improvement and motivation.
    """
    api_key = os.getenv('API_KEY')

    if not api_key:
        raise ValueError("API_KEY is missing. Please check your .env file.")

    client = OpenAI(api_key=api_key)

    prompt = (
        f"Provide personalized feedback for {user_name}, a {age}-year-old {gender} who is {height} cm tall and weighs {weight} kg. "
        f"The user's fitness goal is {fitness_goal}. They have been working out an average of {avg_training_frequency:.1f} times per week, "
        f"with an average weight change of {avg_weight_change:.2f} kg per week. "
        f"The user trains {training_frequency} times per week and their fitness level is {fitness_level}. "
        f"Please give suggestions on how to improve progress and maintain motivation by this program: {program}, considering the user's goal and progress so far."
    )

    try:
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.5,
        )

        response = completion.choices[0].message.content.strip()
        return response

    except Exception as e:
        print(f"Error in OpenAI API call: {e}")
        return "An error occurred while generating AI suggestions."



def call_openAI_for_fact() -> str:
    api_key = os.getenv('API_KEY')

    if not api_key:
        raise ValueError("API_KEY is missing. Please check your .env file.")

    client = OpenAI(api_key=api_key)

    prompt = (
        f"Bring me a random fitness or well-being fact."
        f"Bring me random fact about count calories"
        f"Bring me random fact about "
        f"Bring me a random fact about what you should do before going to training"
        f"Bring me the most important fact to know about fitness"
    )

    try:
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7,
        )

        response = completion.choices[0].message.content.strip()
        print("Successfully called OpenAI API for a random fitness fact.")
        return response

    except Exception as e:
        print(f"Error in OpenAI API call: {e}")
        return "An error occurred while generating the fitness fact."


def get_ai_suggestions(class_type: str, class_level: str) -> str:
    prompt = (
        f"Provide coaching improvement suggestions for a class of type '{class_type}' "
        f"at the '{class_level}' level. The suggestions should be practical and "
        f"help the coach enhance their training sessions."
    )

    try:
        completion = ask_openai(prompt)
        formatted_completion = format_ai_response(completion)
        return formatted_completion
    except Exception as e:
        print(f"Error fetching suggestions from OpenAI: {e}")
        return "An error occurred while generating suggestions."


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

        response = completion.choices[0].message.content.strip()

        formatted_response = response.replace('1.', '<br>1.').replace('2.', '<br>2.').replace('3.', '<br>3.') \
            .replace('4.', '<br>4.').replace('5.', '<br>5.').replace('6.', '<br>6.')

        print(f"Successfully called OpenAI API for muscle suggestion: {formatted_response}")
        return formatted_response

    except Exception as e:
        print(f"Error in OpenAI API call: {e}")
        return "An error occurred while generating the suggestion."

def get_ai_diet_suggestions(height: float, weight: float, age: int, fitness_goal: str, diet_type: str) -> str:
    prompt = (
        f"Provide diet suggestions for someone who is {height} cm tall, weighs {weight} kg, is {age} years old, "
        f"and has the fitness goal of '{fitness_goal}'. The diet type is '{diet_type}'."
    )

    try:
        completion = ask_openai(prompt)
        formatted_completion = format_ai_response(completion)
        return formatted_completion
    except Exception as e:
        print(f"Error fetching diet suggestions from OpenAI: {e}")
        return "An error occurred while generating suggestions."

def format_ai_response(response: str) -> str:
    sections = response.split('\n')

    formatted_response = "<ul>"
    for section in sections:
        formatted_response += f"<li>{section.strip()}</li>"
    formatted_response += "</ul>"

    return formatted_response
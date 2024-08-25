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
        return response

    except Exception as e:
        print(f"Error in OpenAI API call: {e}")
        return "An error occurred while generating the program."


def accpected_result(program:str,time:str ,weight:int,high:int,name:str,gender:str):
    api_key = os.getenv('API_KEY')
    if not api_key:
        raise ValueError("API_KEY is missing. Please check your .env file.")
    client = OpenAI(api_key=api_key)
    prompt=(f"give me the expected result for this program {program} if the user will follow this program for {time}"
            f"the user wieght is {weight} and hes height is {high} and hes gender is {gender}"
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
        return response2

    except Exception as e:
        print(f"Error in OpenAI API call: {e}")
        return "An error occurred while generating the program."
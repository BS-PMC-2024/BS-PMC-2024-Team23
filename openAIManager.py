from openai import OpenAI
import os
from dotenv import load_dotenv


load_dotenv()

def call_openAI(name: str, age: int, gender: str, weight: int, height: int, goal: str, training_frequency: int, fitness_level: str) -> str:
    api_key = os.getenv('API_KEY')
    client = OpenAI(api_key=api_key)

    prompt = (
        f"Create a personalized exercise program for a {gender} named {name}, "
        f"who is {age} years old, weighs {weight} kg, and is {height} cm tall. "
        f"The goal is to {goal}. "
        f"Fitness level: {fitness_level}. "
        f"Training frequency: {training_frequency} times per week. "
        f"Please provide a detailed plan with structured steps."
    )

    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
        temperature=0.7,
    )

    response = completion.choices[0].message.content.strip()
    return response


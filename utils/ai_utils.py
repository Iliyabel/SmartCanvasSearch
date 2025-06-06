from google import genai
from google.genai import types
import os


def get_gemini_response(prompt: str, api_key: str, model_name: str = "gemini-2.0-flash-lite") -> str:
    """
    Sends a prompt to the Gemini API and returns the model's response.

    Args:
        prompt (str): The prompt to send to the Gemini model.
        api_key (str): The Gemini API key.
        model_name (str, optional): The name of the Gemini model to use. 
                                     Defaults to "gemini-1.5-flash-latest".

    Returns:
        str: The text response from the Gemini model, or an error message.
    """
    if not api_key:
        return "Error: Gemini API key is missing."

    try:
        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(
            model=model_name,
            config=types.GenerateContentConfig(
                system_instruction="You are a helpful AI assistant that wants to provide where the source is for a question.",),
            contents=prompt
        )
        
        
        return response.text

    except Exception as e:
        return f"Error communicating with Gemini API: {str(e)}"
    
    
def get_dummy_ai_response() -> str:
    """
    Returns a dummy AI response for testing purposes.
        
    Returns:
        str: A dummy response simulating an AI's answer.
    """
    return "Real numbers in computers are represented as the sum of an integer part and a fractional part [Source: 2.ComputerArithmetic.pptx (Slide 12)]. However, irrational numbers cannot be precisely represented because of the limited number of bits available [Source: 2.ComputerArithmetic.pptx (Slide 12)]. Two main approaches exist: fixed-point representation, where bits are divided for the integer and fractional parts, and floating-point representation, which divides bits for the sign, exponent, and mantissa, similar to scientific notation [Source: 2.ComputerArithmetic.pptx (Slide 13)]. Floating-point representation is now standard [Source: 2.ComputerArithmetic.pptx (Slide 13)]. Limited precision means overflow and underflow are unavoidable [Source: 2.ComputerArithmetic.pptx (Slide 12)]. The documents also mention converting decimal numbers to binary as part of representing real numbers [Source: 2.ComputerArithmetic.pptx (Slide 18)]."    
    
    
def format_ai_response(response: str) -> str:
    """
    Converts a plain-text AI response into a simple HTML
    format to improve readability, adding line breaks and
    highlighting source references.
    """
    # Split by sentences – naive approach:
    sentences = response.split('. ')

    # Build HTML with <p> tags:
    html_lines = []
    for s in sentences:
        # (Optional) Bold the "[Source: …]" part
        # e.g., convert "[Source: 2.ComputerArithmetic…]" to "<b>[Source: 2.ComputerArithmetic…]</b>"
        formatted_s = s.replace("[Source:", "<b>[Source:").replace("]", "]</b>")
        
        # Ensure we end each paragraph with a period if present
        if not formatted_s.endswith('.'):
            formatted_s += '.'
        
        html_lines.append(f"<p>{formatted_s.strip()}</p>")

    return "".join(html_lines)
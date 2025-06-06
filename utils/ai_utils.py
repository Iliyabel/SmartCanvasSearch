from google import genai
from google.genai import types
import re
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
                system_instruction="""You are a helpful AI assistant that wants to provide where 
                    the source is for a question. Summarize the answer for each different source 
                    but not for each differnt page or slide. State the quotes after the summary.
                    Do not use '*' charcter for bold text. Use '*' to state a bullet point. Use '--' 
                    to show that the sentence has a Source in it. 
                    State '(Summary)' for the summary after the source but before the quotes.here is an example:
                    'The files that mention SysTick interrupts are:

                    -- Final_Project.docx [Source: Final_Project.docx (Paragraph 176)]
                    (Summary)   This final project handles only SysTick interrupts. The SysTick timer is started with _timer_start which is invoked when main() calls alarm(). The SysTick timer can count down up to 1 second. If main() calls alarm(2) or alarm(3), SysTick interrupts will occur at least twice or three times. Upon receiving a SysTick interrupt, the control jumps to SysTick_Handler in startup_TM4C129.s.
                    *   "This final project only handles SysTick interrupts."
                    *   "The SysTick timer gets started with _timer_start that was invoked when main( ) calls alarm( )."
                    *   "Note that SysTick timer can count down up to 1 second."
                    *   "Therefore, if main( ) calls alarm( 2 ) or alarm( 3 ), you’ll get a SysTick interrupts at least twice or three times."
                    *   "Upon receiving a SysTick interrupt, the control jumps to SysTick_Handler in startup_TM4C129.s."

                    -- Final_Project.docx [Source: Final_Project.docx (Paragraph 267)]
                    (Summary)   This document mentions SysTick Interrupt.
                    *   "SysTick Interrupt"

                    -- Final_Project.docx [Source: Final_Project.docx (Paragraph 268)]
                    (Summary)   A SysTick interrupt is caught at SysTick_Handler in startup_TM4C129.s.
                    *   "A SysTick interrupt is caught at SysTick_Handler in startup_TM4C129.s."

                    -- Homework7_key.docx [Source: Homework7_key.docx (Paragraph 74)]
                    (Summary)   The C program defines sig_handler() that is invoked upon receiving a SysTick interrupt. The main() function initializes alarmed to 1, schedules sig_hanlder() to be invoked upon a SysTick interrupt, and starts SysTick to count down for 10 seconds.
                    *   "The following C program defines sig_handler( ) (lines 2-4) that is invoked upon receiving a SysTick interrupt and that changes alarmed from 1 to 2. The main( ) function (lines 6-16) initializes alarmed to 1 (line 8), schedules sig_hanlder( ) to be invoked upon a SysTick interrupt (line 9), and starts SysTick to count down for 10 seconds (line 10)."'
                            """),
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
    return """The files that mention SysTick interrupts are:

    -- Final_Project.docx [Source: Final_Project.docx (Paragraph 176)]
    (Summary)   This final project only handles SysTick interrupts. The SysTick timer is started with _timer_start which is invoked when main() calls alarm(). The SysTick timer can count down up to 1 second. If main() calls alarm(2) or alarm(3), SysTick interrupts will occur at least twice or three times. Upon receiving a SysTick interrupt, the control jumps to SysTick_Handler in startup_TM4C129.s.
    *   "Interrupts: This final project only handles SysTick interrupts."
    *   "The SysTick timer gets started with _timer_start that was invoked when main( ) calls alarm( )."
    *   "Note that SysTick timer can count down up to 1 second."
    *   "Therefore, if main( ) calls alarm( 2 ) or alarm( 3 ), you’ll get a SysTick interrupts at least twice or three times."
    *   "Upon receiving a SysTick interrupt, the control jumps to SysTick_Handler in startup_TM4C129.s."

    -- Final_Project.docx [Source: Final_Project.docx (Paragraph 267)]
    (Summary)   This document mentions SysTick Interrupt.
    *   "SysTick Interrupt"

    -- Final_Project.docx [Source: Final_Project.docx (Paragraph 268)]
    (Summary)   A SysTick interrupt is caught at SysTick_Handler in startup_TM4C129.s.
    *   "A SysTick interrupt is caught at SysTick_Handler in startup_TM4C129.s."

    -- Homework7_key.docx [Source: Homework7_key.docx (Paragraph 74)]
    (Summary)   The C program defines sig_handler() that is invoked upon receiving a SysTick interrupt. The main() function initializes alarmed to 1, schedules sig_hanlder() to be invoked upon a SysTick interrupt, and starts SysTick to count down for 10 seconds.
    *   "The following C program defines sig_handler( ) (lines 2-4) that is invoked upon receiving a SysTick interrupt and that changes alarmed from 1 to 2. The main( ) function (lines 6-16) initializes alarmed to 1 (line 8), schedules sig_hanlder( ) to be invoked upon a SysTick interrupt (line 9), and starts SysTick to count down for 10 seconds (line 10). The main( ) function falls into a while( ) loop (lines 11-14), jumps sig_handler( ) upon receiving a SysTick interrupt, and gets out of the while( ) loop as alarmed eventually becomes 2."""    
    
    
def format_ai_response(response: str) -> str:
    """
    Converts a plain-text AI response into a more styled HTML
    format to improve readability.
    - Colors [Source: ...] references.
    - Colors '--' source lines.
    - Colors '(Summary)' section.
    - Colors '*' bullet points.
    - Italicizes quoted text.
    - Indents bullet points that introduce quotes.
    - Adds a gap before source lines that follow quote bullet lists.
    """
    
    # Color [Source: ...] spans 
    processed_text = response.replace("[Source:", "<span style='color: #145c2c;'>[Source:")
    processed_text = processed_text.replace("]", "]</span>")

    # Regex finds text between quotes and wraps the inner content with <i> tags.
    def italicize_quote_content(match):
        # match.group(1) is the content *inside* the quotes
        return f'"<i>{match.group(1)}</i>"'
    
    processed_text = re.sub(r'"([^"]*)"', italicize_quote_content, processed_text)

    lines = processed_text.splitlines()
    html_paragraphs = [] 

    for i, line_text in enumerate(lines):
        stripped_line = line_text.strip()
        if not stripped_line:
            continue

        if stripped_line.startswith("-- "):
            # Remove the "-- " prefix
            content = stripped_line[3:]
            style = "margin-top: 1.5em;" if html_paragraphs else ""
            html_p = (
                f"<p style='{style}'>"
                f"<span style='color: #007bff'>--</span>&nbsp;" # Blue for source lines
                f"{content}</p>"
            )
            html_paragraphs.append(html_p)
            
        elif stripped_line.startswith("* "):
            # Remove the "* " prefix
            content = stripped_line[2:]
            html_p = (
                f"<p style='margin-left: 25px;'>" # Indent quote lines
                f"<span style='color: #D9534F;'>*</span>&nbsp;" # Red asterisk for quotes
                f"{content}</p>"
            )
            html_paragraphs.append(html_p)
            
        # Check for summary section start
        elif stripped_line.startswith("(Summary) "):
            # Remove the "(Summary) " prefix
            content = stripped_line[10:]
            html_p = (
                f"<p style='margin-left: 25px;'>"
                f"<span style='color: #3C815C;'>(Summary)</span>&nbsp;" # Green for summary
                f"{content}</p>"
            )
            html_paragraphs.append(html_p)
                
        else:
            # Normal line (e.g., introductory sentence) or a line that breaks a summary
            html_paragraphs.append(f"<p>{stripped_line}</p>")
            
    return "".join(html_paragraphs) 
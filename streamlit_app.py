import streamlit as st
import pandas as pd
import openai
from decouple import config

# Set up your OpenAI API key
openai.api_key = config('OPENAI_API_KEY')

# Function to send a message to the OpenAI chatbot model and return its response
def send_message(message_log):
    # Use OpenAI's ChatCompletion API to get the chatbot's response
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-1106",  # The name of the OpenAI chatbot model to use
        messages=message_log,  # The conversation history up to this point, as a list of dictionaries
        max_tokens=100,  # The maximum number of tokens (words or subwords) in the generated response
        stop=None,  # The stopping sequence for the generated response, if any (not used here)
        temperature=0.7,  # The "creativity" of the generated response (higher temperature = more creative)
    )

    # Find the first response from the chatbot that has text in it (some responses may not have text)
    for choice in response.choices:
        if "text" in choice:
            return choice.text

    # If no response with text is found, return the first response's content (which may be empty)
    return response.choices[0].message.content

# Streamlit app
def main():
    message_log = [{"role": "system", "content": "You are a helpful assistant."}]
    st.title("Problem-Solution Analysis App")

    # Upload a CSV file
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        # Add columns for 'isFiltered' and 'analysis' to the DataFrame
        df['isFiltered'] = ""
        df['analysis'] = ""

        # Display problem-solution pairs as cards in a flexible grid
        for idx, row in df.iterrows():
            truncated_problem = row["problem"][:100] + "..."
            truncated_solution = row["solution"][:100] + "..."
            
            card = st.expander(f"Problem: {truncated_problem}", expanded=False)
            with card:
                st.write("Full Problem:")
                st.write(row["problem"])
                st.write("Full Solution:")
                st.write(row["solution"])

                # Send the message to OpenAI for analysis
                analysis = send_message(
                    [
                        {
                            "role": "system",
                            "content": "You are a professional idea evaluator and filterer. You will receive a problem followed by a solution. An idea filter is designed to weed out ideas that are sloppy, off-topic (i.e., not sustainability related), unsuitable, or vague (such as the over-generic content that prioritizes form over substance, offering generalities instead of specific details). This filtration system helps concentrate human evaluators' time and resources on concepts that are meticulously crafted, well-articulated, and hold tangible relevance. Mention 1. whether the idea should filtered out (Filter or Keep), and 2. concise bullet points supporting your argument.",
                        },
                        {
                            "role": "assistant",
                            "content": "Problem: " + row["problem"] + "\n Solution: " + row["solution"],
                        },
                    ]
                )

                # Determine if the idea should be filtered
                if "keep" in analysis.lower():
                    row['isFiltered'] = "Keep"
                else:
                    row['isFiltered'] = "Filter"

                row['analysis'] = analysis

                # Display the result and icons
                st.write("Analysis Result:")
                st.write(row['analysis'])

                if row['isFiltered'] == "Keep":
                    st.image("green-checkmark.png", caption="Analysis Result: Positive", width=200)
                else:
                    st.image("red-x.png", caption="Analysis Result: Negative", width=200)

        # Allow filtering based on whether an idea is filtered or not
        filtered_ideas = df[df['isFiltered'] == "Filter"]
        st.subheader("Filtered Ideas")
        st.dataframe(filtered_ideas)

if __name__ == "__main__":
    main()

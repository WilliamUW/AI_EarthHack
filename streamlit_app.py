import asyncio
import streamlit as st
import pandas as pd
import openai
from decouple import config

# Set up your OpenAI API key
openai.api_key = config("OPENAI_API_KEY")


# Function to send a message to the OpenAI chatbot model and return its response
async def send_message(message_log, maxToken):
    print(message_log)

    # Use OpenAI's ChatCompletion API to get the chatbot's response
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-1106",  # The name of the OpenAI chatbot model to use
        messages=message_log,  # The conversation history up to this point, as a list of dictionaries
        max_tokens=maxToken,  # The maximum number of tokens (words or subwords) in the generated response
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
    st.title("Welcome to SWIFT! 🔰")
    st.subheader("(Sustainable Workflow for Idea Filtering and Testing)")

    # Upload a CSV file
    uploaded_file = st.sidebar.file_uploader(
        "Upload a CSV file with the columns: 1. ID, 2. Problem, 3. Solution. [Example](https://github.com/WilliamUW/AI_EarthHack/blob/main/20%20AI%20EarthHack%20Dataset%20copy.csv)",
        type=["csv"],
    )

    filter_prompt = ""

    filter_level = st.sidebar.selectbox(
        "Select Filtering Level:",
        ["Loose Filter", "Normal Filter", "Strict Filter"],
        index=1,
    )

    if filter_level == "Loose Filter":
        st.sidebar.write("You selected a loose filter where most ideas will pass.")
        filter_prompt = "Be a loose filter where most ideas will pass."
    elif filter_level == "Normal Filter":
        st.sidebar.write("You selected a normal filter.")
    elif filter_level == "Strict Filter":
        st.sidebar.write("You selected a strict filter.")
        filter_prompt = "Be an extremely strict filter where very little ideas will pass and you are super critical of all aspects of an idea such the business model and whether an existing solution already exists."

    formatting = st.sidebar.text_input("Analysis Delivery Format", "Concise bullet points")

    criterias = st.sidebar.text_input(
        "Evaluation Criterias",
        "Environmental impact, economic viability, scalability",
    )

    # Add a number input for setting a threshold
    maxToken = st.sidebar.number_input(
        "Preferred Length of Analysis",
        value=300,
        step=1,
        max_value=1000,
    )

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, encoding="ISO-8859-1")

        # filtered_ideas = None
        # keep_ideas = None
        # all_ideas = None

        # Check if the DataFrame contains the columns "problem" and "solution"
        if "problem" in df.columns and "solution" in df.columns:
            st.sidebar.success(
                "Valid CSV! The CSV file contains the columns 'problem' and 'solution'."
            )
        else:
            st.sidebar.error(
                "Invalid CSV: The CSV file does not contain the required columns 'problem' and 'solution'."
            )
            df = None

        # Add a number input for setting a threshold
        threshold = st.sidebar.number_input(
            "Number of ideas to process",
            value=10,
            step=1,
            max_value=df[df.columns[0]].count(),
        )

        if st.button(
            f"Proceed with the uploaded CSV file? It will require {min(threshold, df[df.columns[0]].count())} API calls. Estimated time: {min(threshold, df[df.columns[0]].count()) * 3} seconds."
        ):
            st.success("Processing right now!")
            gif_url = "https://i.giphy.com/o0vwzuFwCGAFO.webp"  # Replace with your GIF URL
            st.image(gif_url)
            # Add columns for 'isFiltered' and 'analysis' to the DataFrame
            df["isFiltered"] = ""
            df["analysis"] = ""

            # Display problem-solution pairs as cards in a flexible grid
            for idx, row in df.iterrows():
                if idx >= threshold:
                    break
                if type(row["problem"]) is float or row["problem"] == "":
                    continue
                truncated_problem = row["problem"][:80] + "..."
                truncated_solution = row["solution"][:100] + "..."

                # Send the message to OpenAI for analysis
                analysis = asyncio.run(
                    send_message(
                        [
                            {
                                "role": "system",
                                "content": f"You are an expert in sustainability and are very selective about which circular economy ideas will work, given most fail due to there being pre-existing solutions, economic inviability, inability to scale, and technological and business risks. You will receive a problem followed by a solution. Only approve ideas that are meticulously and professionally crafted, well-articulated, and hold tangible relevance. Filtering strictness: {filter_prompt}. In separate lines, mention 3 points. Point 1 - Filter Out Yes or No. Remove if the idea if any of the following applies: sloppy (short length e.g. less than 3 sentences), off-topic (i.e., not sustainability related), unsuitable, or vague (such as the over-generic content that prioritizes form over substance, offering generalities instead of specific details) and if it doesn't clearly specify how it addresses all the evaluation criterias listed below. Return either (Yes - remove idea.) if it falls under one of those categories or (No - keep idea.) if it does not. Point 2 - SWIFT Score: a SWIFT score out of 100 as to whether to filter out the idea (100 - keep, 0 - filter out). This should align with point 1. Point 3 - Analysis Explanation: {formatting} supporting whether to keep or remove the idea from 1. Evaluate on the following criterias: {criterias}. Finally, write a one sentence conclusion that explains why the idea is filtered out and the filter score using the criterias listed. Output format: In separate lines, mention the 3 points: 1. Filter Out: Yes or No. 2. SWIFT Score: Out of 100. 3. Analysis Explanation: 4. Conclusion:",
                            },
                            {
                                "role": "assistant",
                                "content": "Problem: "
                                + row["problem"]
                                + "\n Solution: "
                                + row["solution"],
                            },
                        ],
                        maxToken,
                    )
                )

                df.at[idx, "analysis"] = analysis

                # Determine if the idea should be filtered
                if "yes" in analysis.lower():
                    df.at[idx, "isFiltered"] = "Filter"
                else:
                    df.at[idx, "isFiltered"] = "Keep"

                icon = "❌"

                if df.at[idx, "isFiltered"] == "Keep":
                    icon = "✅"

                card = st.expander(
                    f"#{idx + 1} - {icon} - Problem: {truncated_problem}",
                    expanded=False,
                )
                with card:
                    st.write("Full Problem:")
                    st.write(row["problem"])
                    st.write("Full Solution:")
                    st.write(row["solution"])

                    # Display the result and icons
                    st.write("Analysis Result:")
                    if df.at[idx, "isFiltered"] == "Keep":
                        st.image(
                            "green-checkmark.png",
                            caption="Analysis Result: Keep Idea",
                            width=200,
                        )
                    else:
                        st.image(
                            "red-x.png",
                            caption="Analysis Result: Filter Out Idea",
                            width=200,
                        )
                    st.write(analysis)

            # Allow filtering based on whether an idea is filtered or not
            filtered_ideas = df[df["isFiltered"] == "Filter"]
            st.subheader("Removed Ideas")
            st.dataframe(filtered_ideas)

            # Allow filtering based on whether an idea is filtered or not
            keep_ideas = df[df["isFiltered"] == "Keep"]
            st.subheader("Remaining Ideas")
            st.dataframe(keep_ideas)

            all_ideas = df[df["id"] != None]
            st.subheader("All Ideas")
            st.dataframe(all_ideas)

            gif_url = "https://i.giphy.com/3LMuVfcoGXOV2OO51k.webp"  # Replace with your GIF URL
            st.image(gif_url)   

        # # Export dataframes to CSV files
        # if st.button("Export Removed Ideas as CSV"):
        #     with st.spinner("Exporting Removed Ideas..."):
        #         filtered_ideas.to_csv("removed_ideas.csv", index=False)
        #     st.success("Removed Ideas exported successfully!")

        # if st.button("Export Remaining Ideas as CSV"):
        #     with st.spinner("Exporting Remaining Ideas..."):
        #         keep_ideas.to_csv("remaining_ideas.csv", index=False)
        #     st.success("Remaining Ideas exported successfully!")

        # if st.button("Export All Ideas as CSV"):
        #     with st.spinner("Exporting All Ideas..."):
        #         all_ideas.to_csv("all_ideas.csv", index=False)
        #     st.success("All Ideas exported successfully!")


if __name__ == "__main__":
    main()

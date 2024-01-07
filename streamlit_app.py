import asyncio
import streamlit as st
import pandas as pd
import openai
from decouple import config

# Set up your OpenAI API key
openai.api_key = config("OPENAI_API_KEY")


# Function to send a message to the OpenAI chatbot model and return its response
async def send_message(message_log):
    print(message_log)

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
    st.title("Welcome to SWIFT! ")
    st.subheader("(Sustainable Workflow for Idea Filtering and Testing)")

    # Upload a CSV file
    uploaded_file = st.file_uploader(
        "Upload a CSV file with the columns: 1. ID, 2. Problem, 3. Solution.",
        type=["csv"],
    )

    filter_prompt = ""

    filter_level = st.selectbox(
        "Select Filtering Level:",
        ["Loose Filter", "Normal Filter", "Strict Filter"],
        index=1,
    )

    if filter_level == "Loose Filter":
        st.write("You selected a loose filter where most ideas will pass.")
        filter_prompt = "Be a loose filter where most ideas will pass."
    elif filter_level == "Normal Filter":
        st.write("You selected a normal filter.")
    elif filter_level == "Strict Filter":
        st.write("You selected a strict filter.")
        filter_prompt = "Be an extremely strict filter where very little ideas will pass and you are super critical of all aspects of an idea such the business model and whether an existing solution already exists."

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, encoding="ISO-8859-1")

        # filtered_ideas = None
        # keep_ideas = None
        # all_ideas = None

        # Check if the DataFrame contains the columns "problem" and "solution"
        if "problem" in df.columns and "solution" in df.columns:
            st.success(
                "Valid CSV! The CSV file contains the columns 'problem' and 'solution'."
            )
        else:
            st.error(
                "Invalid CSV: The CSV file does not contain the required columns 'problem' and 'solution'."
            )
            df = None

        # Add a number input for setting a threshold
        threshold = st.number_input(
            "Set the maximum number of ideas you want to process",
            value=10,
            step=1,
            max_value=df[df.columns[0]].count(),
        )

        if st.button(
            f"Proceed with the uploaded CSV file? It will require {min(threshold, df[df.columns[0]].count())} API calls. Estimated time: {min(threshold, df[df.columns[0]].count()) * 3} seconds."
        ):
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
                                "content": f"You are a sustainability expert and professional idea evaluator and filterer. You will receive a problem followed by a solution. This filtration system helps concentrate human evaluators' time and resources on concepts that are meticulously crafted, well-articulated, and hold tangible relevance. {filter_prompt} In separate lines, mention 1. whether the idea falls under one of the categories: sloppy, off-topic (i.e., not sustainability related), unsuitable, or vague (such as the over-generic content that prioritizes form over substance, offering generalities instead of specific details). Return either (Yes - remove idea) if it falls under one of those categories or (No - keep idea) if it does not. 2. a viability score out of 100. 3. concise bullet points supporting whether to keep or remove the idea from 1.",
                            },
                            {
                                "role": "assistant",
                                "content": "Problem: "
                                + row["problem"]
                                + "\n Solution: "
                                + row["solution"],
                            },
                        ]
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

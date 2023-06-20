import streamlit as st
import pandas as pd
from datetime import datetime
import openai
import os
import re

# # set the OpenAI API key, from the environment variable
# openai.api_key = os.environ["OPENAI_API_KEY"]

# set the OpenAI API key, from streamlit secrets.toml file
openai.api_key = st.secrets["OPENAI_API_KEY"]

# function to split text into paragraphs
def split_paragraphs(text):
    paragraphs = re.split(r'\n+', text)  # Splitting on double line breaks
    return paragraphs

# set the context
context = "You are THE expert authority on punctuation rules and conventions for the English language. You will be provided an exceprt of text that may or may not contain punctuation errors; the text will be contained within curly braces. If punctuation errors exist in the text, please correct these punctuation errors; ensure that the corrected text contains zero newline characters; and, return only the corrected text:"

followup_context = "Define a numbered list containing all changes that were made between the text in the first set of curly braces and the text in the second set of curly braces; ensure that any differenceses between the 2 texts are accounted for your list of changes, including any changes to punctuation or capitalization, and be sure to list any changes to capitalization; and, only return the list and nothing else:"

# set the page title
st.set_page_config(page_title='Proofreader App', page_icon='🏴‍☠️', layout='wide')

# show the page title
st.title('Proofreader App')

# create a placeholder for the form
input_area = st.empty()

# create a form
with input_area.form("text_submit"):
    content = st.text_area(
        label="Enter text here:",
        placeholder="The writer who neglects punctuation, or mispunctuates, is liable to be misunderstood for the want of merely a comma...",
        height=300
    )
    submit = st.form_submit_button("Submit")

# create a placeholder for the success message
success_message = st.empty()

# create a placeholder for the progress bar
progress_bar_placeholder = st.empty()

# if the user has submitted the form and the content is not empty
if submit and content != '':

    # split the content into paragraphs
    paragraphs = split_paragraphs(content.strip())

    # clear the placeholder
    input_area.empty()

    # show the success message
    success_message.success('Submit successful!')

    # initialize the followup_prompt variable
    followup_prompts = []
    original_texts = []
    corrected_texts = []
    corrections_lists = []

    # initialize the fixed_content variable
    fixed_content = ''
    csv_file = '' # This needs to be a dataframe, to append to after each iteration of below loop

    # create a progress bar
    with progress_bar_placeholder:
        st.write('Processing...')
        progress_bar = st.progress(0)

    # loop through the paragraphs in batches of 20
    for i in range(0, len(paragraphs), 20):

        # update the progress bar
        progress_bar.progress((i + min(20, len(paragraphs))) / len(paragraphs) / 2)

        # get the next 20 paragraphs
        these_paragraphs = paragraphs[i:i + 20]

        # append these paragraphs to the original texts list
        for this_paragraph in these_paragraphs:
            original_texts.append(this_paragraph)

        # concatenate the context and each paragraph
        prompts = [context + '\n{' + p + '}' for p in these_paragraphs]

        # send the batch of prompts to the OpenAI API
        response = openai.Completion.create(
            model="text-davinci-003", # rate limit: 60rpm/60ktpm
            prompt=prompts,
            temperature=0,
            max_tokens=1024,
        )

        for j in range(len(response.choices)):

            # append the followup prompts to the followup prompts variable
            followup_prompts.append(prompts[j] + '\n{' + response.choices[j].text + '}\n' + followup_context)

            # append the corrected texts to the corrected texts variable
            corrected_texts.append(response.choices[j].text)

            # append the corrected texts to the fixed content variable
            fixed_content += '\n' + response.choices[j].text

        # send the batch of prompts to the OpenAI API
        followup_response = openai.Completion.create(
            model="text-davinci-003", # rate limit: 60rpm/60ktpm
            prompt=followup_prompts,
            temperature=0,
            max_tokens=1024,
        )

        for k in range(len(followup_response.choices)):

            # append the corrections list to the corrections lists variable
            corrections_lists.append(followup_response.choices[k].text.strip().replace('\n', '|'))

            # cretae a CSV file - append a new row to csv_flie variable
            print(followup_prompts[k] + '\n' + followup_response.choices[k].text + '\n\n-----------\n\n')

    # remove extra newlines
    fixed_content = re.sub('\n+', '\n\n', fixed_content.strip())

    # create a dataframe from the original texts, corrected texts, and corrections lists
    print(len(original_texts))
    print(len(corrected_texts))
    print(len(corrections_lists))
    df = pd.DataFrame({
        'original': original_texts,
        'corrected': corrected_texts,
        'corrections': corrections_lists
    })
    print(df)
    print(corrections_lists)

    # create a download button, to download the CSV file, from the dataframe
    st.download_button(
        "Download corrections.csv",
        df.to_csv(index=False).encode('utf-8'),
        "corrections-" + datetime.now().strftime("%Y%m%dT%H:%M:%S") + ".csv",
        "text/csv",
        key='download-csv', 
    )

    # clear the progress bar
    progress_bar_placeholder.empty()

    # clear the success placeholder
    success_message.empty()

    # show the fixed content
    st.text_area('Corrected text:', fixed_content, height=300)
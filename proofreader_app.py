import streamlit as st
import openai
import os
import re

# set the OpenAI API key
openai.api_key = os.environ["OPENAI_API_KEY"]

# function to split text into paragraphs
def split_paragraphs(text):
    paragraphs = re.split(r'\n+', text)  # Splitting on double line breaks
    return paragraphs

# set the context
context = "You are THE expert authority on punctuation rules and conventions for the English language. You will be provided an exceprt of text that may or may not contain punctuation errors; the text will be contained within curly braces. If punctuation errors exist in the text, please correct these punctuation errors; the corrected text will have zero newline characters; and, return only the corrected text:"

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

    # initialize the fixed_content variable
    fixed_content = ''

    # create a progress bar
    with progress_bar_placeholder:
        st.write('Processing...')
        progress_bar = st.progress(0)

    # loop through the paragraphs in batches of 20
    for i in range(0, len(paragraphs), 20):

        # update the progress bar
        progress_bar.progress((i + min(20, len(paragraphs))) / len(paragraphs) / 2)

        # concatenate the context and each paragraph
        prompts = [context + '\n{' + p + '}' for p in paragraphs[i:i+20]]

        # send the batch of prompts to the OpenAI API
        response = openai.Completion.create(
            model="text-davinci-003", # rate limit: 60rpm/60ktpm
            prompt=prompts,
            temperature=0,
            max_tokens=1024,
        )

        # loop through the choices and remove the curly braces and add a newline
        for choice in response.choices:
            fixed_content += '\n' + choice.text

    # remove extra newlines
    fixed_content = re.sub('\n+', '\n\n', fixed_content.strip())

    # clear the progress bar
    progress_bar_placeholder.empty()

    # clear the success placeholder
    success_message.empty()

    # show the fixed content
    st.text_area('Corrected text:', fixed_content, height=300)
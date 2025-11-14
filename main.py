# Copyright (c) 2025 victor256sd
# All rights reserved.

import streamlit as st
import streamlit_authenticator as stauth
import openai
from openai import OpenAI
import os
import time
import yaml
from yaml.loader import SafeLoader
from pathlib import Path
from cryptography.fernet import Fernet
import re

# Disable the button called via on_click attribute.
def disable_button():
    st.session_state.disabled = True        

# Definitive CSS selectors for Streamlit 1.45.1+
st.markdown("""
<style>
    div[data-testid="stToolbar"] {
        display: none !important;
    }
    div[data-testid="stDecoration"] {
        display: none !important;
    }
    div[data-testid="stStatusWidget"] {
        visibility: hidden !important;
    }
</style>
""", unsafe_allow_html=True)

# Load config file with user credentials.
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

# Initiate authentication.
authenticator = stauth.Authenticate(
    config['credentials'],
)

# Call user login form.
result_auth = authenticator.login("main")
    
# If login successful, continue to aitam page.
if st.session_state.get('authentication_status'):
    authenticator.logout('Logout', 'main')
    st.write(f'Welcome *{st.session_state.get('name')}* !')

    # # Initialize chat history.
    # if "ai_response" not in st.session_state:
    #     st.session_state.ai_response = []
    
    # Model list, Vector store ID, assistant IDs (one for initial upload eval, 
    # the second for follow-up user questions).
    MODEL_LIST = ["gpt-4o-mini"] #, "gpt-4.1-nano", "gpt-4.1", "o4-mini"] "gpt-5-nano"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
    VECTOR_STORE_ID = st.secrets["VECTOR_STORE_ID"]
    INSTRUCTION_ENCRYPTED = b'gAAAAABpFqVGD4HMi1aqsE1_8vcjuJRmkBRu0d3dL7GsNoH6fFFJKKODEY69GYbdJ0T4tBNivLIqOio7JVBYVgST0fher9PjWfcx6J5KmFVx6PCAYILyAyxD5DYOBAGo_J0lZHynI2ofhK5QwHWA3JkZTIK1RHiR2sfVDjj-rJbxnljnXGAgl5Wx7xM6rOnH8oBItYp5n7wn1j65Zg8Q8_cP7NyWvJJaFSoUTcZAivHl4gaj2umdm1WXpK3R73B3uPqcNwls6ahJYiSlo9keVtn7rK0kcWHlPYM-vbgov8tCT0HxnB-yy7CzKm4vLToFxG24TLqs59N8rkJTSdDa0G7T7CUPs4UYAm9iizCrIjw_WdBLZsiY20Tfh5TeprTROXdL_BSi1JTlD5HNrmxIVAnzy5ouepR3c2LM-d5B8F_PMti7XKQ8xp025mi81x-SMWEqw-AZZdj1ATWo3PTFTUrUl_c_AT2J-Zg6eZjV3qe6FmJDi-SGJuKgVhrL6vSxfmz7B11Sx4Uaa22c-kqTS2q4KmVeHi5WpQLkfL13JJwPTAsflFUFoXrSbbRORnSYfRKwxWGnbPPV9HUyQ1oNdRbAZAUMhFDcVZPOgEr-Z-9p0mgD1QEi0XPwfjzOJP92ogdDcxhKXnPAGSyY3QmiLcCEMDgqf6OnHiJpgiYa1t9sKee-BpXGWCWB-3Px_YaZodF9XHGx7tKhWL4XGLCb_EYY2ALZ6vJdME4Ndne3kJ2wO69_NHunY-PiN-JyThhyuxtQpFpNObZ6RYGjrW55hTLjYTpX1FathrXBu1etKpJJmLB-DWZ6fO54iV-BN58bSqzR7piHgZSUGHWCVDZfDIC7aZ1NPQ8nkc_ZOqID103yOAD1N0_S4i5gsnsD521tBggbhN07O4Gu0h6uVJVe8FDfxOO3fNqMmUOaEPBjyFW87vxQOy6ua7Uf-qt6XXXuT8nyFod6sNXsnEFsrIllHBMwvSnQH36xVEqlRfX3zLLkM31y5iBmOgN9D47o3y963Zs2wXGHizs6AsSE6yOMFPIY2MvviCV5SSiI6rKp0SGlxbMc3DiJBb-L8bcyNmAEwHvVJD5YNCVG5MESog0VvQwPyOZDMmUX2d6DVjAxPoY8IJIhD0hxcqkAr4iEo1sZCHc125bqSNO2wxdKU-hT34zfedAPLtgQ-3MatuGhnV-EZ7k5pXBCxT1NpheHmytNq3QSVEXUlISCyNbXXT8AGcQ6dFzksBa8R-HyuKq22jmdlNstE2h3PS4dAiJq3oMB45BOJmNagkfWL4d_OlHlLqXGppXT3R9Z8Lg0EzOGhTO2pdM7SP0UAqbQpHrpkCZDolVkeFgHggpoNSSSRf6ZnbIS6-NtRqr6jAvsucUSwfDyBYOM98RbVEp40oETrXzeh7e29yYM5QTG5mrhcgSpC1dKg8u3zJFbEc9oHIVXYeuH3y1I7zhucXEKfNgDqTFNSqOr2HCBH1ku-UyaUpxqq2U9RheHSDCENyZxaJM6fRbxT3xSrXXa8iJvu_Ur_mRDrl92PgoXRM18hCJz4m4I5DJWyMKx40pBGvmKxEMDL90hYYUH7UoD7cELvvOZibDo-rQ1Vu_UWEBer2ReEinL8sb1-JOlHvkVaUFiTRmpAFVQP6YvEDZ6kmqb6dgIKZO-qwbq-dkLf_UGDnH_eotmX_GNg2GjFdYtgFiivqWpm9r1NRmnQV-5ovMWiEAmGSt5FI81oBak219sHNJvQ8ID0vvrrXt-Mz3ZgqseTYPQVCpvM60Wy9OvB5CJxKsHyvwp3yYxXCmJXQBzU4NSm4RqKzSVnvPlufvUQMjGUA7fyeDllDRIU0o5fYKB50gAQm1qA_iTFkzcAfW1DJrOyqqF4yanyBeLPoBkVmaQDW6zxYTNog0dyohAW8KpxGyA20RE4neU1N2dyaZH-rNfr235PT58CNMokugb-X3avrZeQVn3z0Rlg46I4A8y2WXy_rRgkYUT_NtmD9mjJShfENEF_Kz3Wq6Q6GBeErR5gA0ohu8vQ8qYnoCfNcXo_PW_VgCFgYuCWpDSv2-pXKIYMHGAQjw3EgqGRHOgJMg1hmj4NdjciBU6ed_kfUe83y_WMVnrRTQskxOD7hoFazffI0LRGOc9_zJYsg5Sidl9Hm-28R9syoFKxd4Kuhz7lgxF6QxVjd5TofZiou1igqThYqDCNcnrOkvyU4G-FEp2h4fO0dEQYiDwlLUrYjzCJITM2q_pbzdCm1CiFTh-go-3_-p0GKnDWW0Cb0y-KJ3zMuRPcLX27jHJJa_5yhtXD1If6bZhnzCbaUpOwW6qzJm6eU6q5Q7FeM_aLOoOyl-zFI0rEsMzxdD_mOmaJPTjV5TQTV8JF96B3OhvGG_Dv0IHB8t4lKhG_5g92hL26y4XUCxaGVTfCmq82-99lxLkN9VBpXrhLxpVWg8ePV4ChQo4eN12x72MNpAMacyd3fwtmh4Vqp8oBPt92WmWe26hvNVumeJ5hyRZF-bPLYi6-iikFpgr9z93blj3kHtiTr-Z2Ooa-g4bTDsK303PBm7xmcQAQHTHPCrJe0EmkRWONX8QIQ-2_rrAH1Zh3DQqUZnU2wSZA1m-OTMe7smkodysyu4yoCg-BShw-saw92pZnB7IYZzZDFcj10Ux_CHvuvrAaGKBcGSKFtGDbgOqC22_gLVNqkjaL6AjuvrfzE6nEAzdTXuIs8b1FyA1noeo-gtEKXM8Qmuit46uzzNwUBu69irWSMPIfPQl6kLj9PfOx_RwWsS7f-_fUDfD1_K-ni9cTNQI73GakPBhDPcByD5eK76eNdYTkPP9-fRl7h7RDgd0qyyfLpK7V06QjiDGoefNFhNczQtiwtxxfhRITR8R4UZDW-4aKOutId7PUjazNUhN8Pz4Ehm2VtWjPgSwSHQ71Vt52ztxIbll5Hjbcj1DbLj16QmnljXkprJ1lMakXJev5vrqvfLAGvuJuYoNqVFHjBoU9ZS49uMKXbcaeW_nnJRZ4kc8YjznBn5W9e3LSGbclo8-zTHFK5cj6fz7cC1HD4Ofq3xGZGODKOfxNIPuez2xWFSZenoO0-7kU8ynrwLTyn72GmU_Hjkk_AuetdDPSB65oxb7d0-5bxopUkaGC07HXyOIihNFBGfVl1ie6RqwVyUHSX74yMFvvUJsLiiUy1A6sVOwe8Xm9j6wrAFcA0_9oTxvGPgQ1Ili65cqfdq0iZXY1LJmd87T6nvL7alioBGKUVdFjkCzhJQFfDvN2FVGqH6Aht8TXuYs20aucm8H293LKqGEEpFjybyW9NPX4cnetAK2iv1sgPxRpxxc5Du2cI_CBhVsWoQER9VFY_MS3wGhJ83YT4JpfRPVIPLZFbgXwXeyU957EelO9GFEyy3UgNR3KmPZl4BXwJ3fX24g9jIGYdYPDkJPut2cjAsRFxPiW7mVIywPk8txLyaAeSbwUv1PGQAa7OVUq40lFFMdwrvKYpKWeRJj_MewLMYEdv-mZS9tbiNZ9XqKaElgfSJCcETiNDpUCw3faYo3JXAZsVfnJyW2_4Z4Vs_B-7IXwtT2W07Ywh91M1iCUPmCLiNW5JfqsYjk5FnYI__s3dXNZMihi9_wRma_5FtzTwOF-qAWSWKc0imNZJVXBr04hE53NH5P6LnSxAI8pM5wp7fnhQWN-Y1d77gKsJRXU93ZkimGDMZtahSAsKSlnY9Xk7iMJTfVXEBAwZtH3R3dMelsMfbJSfbj9YnlYlWCwcyLfjUEzzhZJnjDreLMR_Nr7YSshMj_Db9PpEZ5xLQ8VyrTmq8IVONvOOwOXz3rlWgrHYZlCeywXz9Jlj5Kzw_LFLMAJlJ6KPIO4F-Kz7g6VvpLSXLAcB6g9674Yr1NZjWp65mk5zLWxwBiRYk5vl2roZc4yaDxeGwTAWougi90fC5k7SCdAZ1HigefE7AYdI78TYqV4d0WE1R0fY6-MQtIqm_H7INGM3BIXPXN2WVhTlVDJJwOYDAgYhJ0SgXh1NSzj8eOZW86NMnK8JPfxrtn1VRp7EWjGCi2mb35sDiyGyc2yhFg2Wr6IF5-DU94CNSmyd-nyj5G9Los46lnpIM7OdSGTLhC2svogWSdJlXWVgtYxXNaB_9rEj5ErOI37tE9J0j7k738medBtkBoiLmY9lfPyjH34ry_2Z68eqRhzd5tV0R9w65QTNEYudCqiZWH76YUzg4OZMKQH8ltzau6BsY4q38oh8a5bzaj0ibNKk4YaEnBSj4ERHqv_5suanHev58UYy-YbFTf2VP2C9T0VMA-qxNwo1XghsowJihIgpd8VckX4a0NANDC_ufXgcoWirDRffqGoigO_rtVt6hvQ0SFc6jTIxQN_mwjvcTRmoBiChFC-B1bY2nNxhurOvSWRvvqRQYJTRPXhhmqKsuZFJqQ50BKgCcH5H6ucIewbN0dtHb1HqqvIVGclFc495ZIRMaOUT5oDdVlW7hTk_2CqFwRDMwKps-E6P_eRq8ahJ6SluG138sq_XTfKgyoOfdDLBL2ekhTDBUF1BH3gyx1Vv3IAkSL1s50QzRgZSNSVWANGsmXLxH4pigG-X9-viZFL-I49TwBpKAv8B9QcVRnotQknerKAj_9gc3IO6STxJ-pM2ZHvL8VIeuYrGXO1V-2Y5uXkhluV0-opM3NmKXUVzyi-BF8Sw_tezUp4KRrkLi2f8s34zs56kNTHGgL-ZWK7O0GDYLmVNcul3fCsdN-kCDdzXn8hdH3JfBb7g9tsh9dlMIlj63TYLGjopS-b6FKrfNjXAj84uQHcFSAIn79Z-oMiz2pLmn8enAjlPKWgxvnuxwJsYENlSrirODcmavYOImOkplAofzivivBSNweWRWf3dXx9DfYxaY5LSZtKsQRVsmBYXN0Me84NIHMOyt0CdLFV2coI1zbdDzer-qH8YHcFOweufmIpiZLyuvncAwjWQSjzjX42ZAirSqhaFbg4NuITpDYgjKX8tKHNNxklbCDhOf5AlEnOo80E_ImK9JhR_D5aEuL96xRH5lKLwE7EKlRftQOq_hAU1j8GW837jHPJey0CEd8NYfalvZ6scin9YERsVGIWJHDmy8CNBRJ2MpQqq3CruDXy5OJ4GlcKyF42GukknGfizRf8sbvuR-d4MwLn3QLq5Za0T7v8bESVlaWm6y00bzocN6wNEWSXsl50ABVq5IlMbnf-YsG4cwxYggBD4apeCS1GIpWQud1fDYUW9zTB42om8dugilZIxB92FzrWSyFZxLBvotIhWpznN1ZnKMXWD1BgBViYV7WzGyNSYIptSAECewzG2I5kfFhzZNvNqaQa8eRoSC_Z4K8Kd34WJ9mdsNf1LnjZDerBBpBt7Elw-NIIZb9617xu7iYgJ6w80Tsc7KiDElFV51IsGBp3EvWwnJOxW6MHRyEogrVgZRL2CVkisvDXMP1zGhxpD2fL_tVNKd1f-3P'

    key = st.secrets['INSTRUCTION_KEY'].encode()
    f = Fernet(key)
    INSTRUCTION = f.decrypt(INSTRUCTION_ENCRYPTED).decode()

    # Set page layout and title.
    st.set_page_config(page_title="Bridge AI", page_icon=":bridge_at_night:", layout="wide")
    st.header(":bridge_at_night: Bridge AI")
    
    # Field for OpenAI API key.
    openai_api_key = os.environ.get("OPENAI_API_KEY", None)

    # Retrieve user-selected openai model.
    model: str = st.selectbox("Model", options=MODEL_LIST)
        
    # If there's no openai api key, stop.
    if not openai_api_key:
        st.error("Please enter your OpenAI API key!")
        st.stop()
    
    # Create new form to search aitam library vector store.    
    with st.form(key="qa_form", clear_on_submit=False, height=300):
        query = st.text_area("**Ask for mental health guidance:**", height="stretch")
        submit = st.form_submit_button("Send")
        
    # If submit button is clicked, query the aitam library.            
    if submit:
        # If form is submitted without a query, stop.
        if not query:
            st.error("Enter a question for mental health guidance!")
            st.stop()            
        # Setup output columns to display results.
        # answer_col, sources_col = st.columns(2)
        # Create new client for this submission.
        client2 = OpenAI(api_key=openai_api_key)
        # Query the aitam library vector store and include internet
        # serach results.
        with st.spinner('Searching...'):
            response2 = client2.responses.create(
                instructions = INSTRUCTION,
                input = query,
                model = model,
                temperature = 0.6,
                # text={
                #     "verbosity": "low"
                # },
                tools = [{
                            "type": "file_search",
                            "vector_store_ids": [VECTOR_STORE_ID],
                }],
                include=["output[*].file_search_call.search_results"]
            )
        # Write response to the answer column.    
        # with answer_col:
        try:
            cleaned_response = re.sub(r'【.*?†.*?】', '', response2.output_text) #output[1].content[0].text)
        except:
            cleaned_response = re.sub(r'【.*?†.*?】', '', response2.output[1].content[0].text)
        st.write("*The guidance and responses provided by this application are AI-generated and informed by general psychological principles and mental health best practices. They are intended solely for informational and supportive purposes and do not constitute professional psychological diagnosis, therapeutic advice, or crisis intervention. All responses should be considered suggestions, not instructions, and must be integrated into your own professional standard of practice. Practitioners are expected to base their decisions and actions on their own clinical judgment, experience, and training. Users should consult licensed mental health professionals, medical providers, or emergency services for any concerns requiring clinical evaluation, treatment, or urgent care. This tool is designed to assist, not replace, qualified mental health expertise or professional judgment.*")
        st.markdown("#### Response")
        st.markdown(cleaned_response)

        st.markdown("#### Sources")
        # Extract annotations from the response, and print source files.
        try:
            annotations = response2.output[1].content[0].annotations
            retrieved_files = set([response2.filename for response2 in annotations])
            file_list_str = ", ".join(retrieved_files)
            st.markdown(f"**File(s):** {file_list_str}")
        except (AttributeError, IndexError):
            st.markdown("**File(s): n/a**")

        # st.session_state.ai_response = cleaned_response
        # Write files used to generate the answer.
        # with sources_col:
        #     st.markdown("#### Sources")
        #     # Extract annotations from the response, and print source files.
        #     annotations = response2.output[1].content[0].annotations
        #     retrieved_files = set([response2.filename for response2 in annotations])
        #     file_list_str = ", ".join(retrieved_files)
        #     st.markdown(f"**File(s):** {file_list_str}")

            # st.markdown("#### Token Usage")
            # input_tokens = response2.usage.input_tokens
            # output_tokens = response2.usage.output_tokens
            # total_tokens = input_tokens + output_tokens
            # input_tokens_str = f"{input_tokens:,}"
            # output_tokens_str = f"{output_tokens:,}"
            # total_tokens_str = f"{total_tokens:,}"

            # st.markdown(
            #     f"""
            #     <p style="margin-bottom:0;">Input Tokens: {input_tokens_str}</p>
            #     <p style="margin-bottom:0;">Output Tokens: {output_tokens_str}</p>
            #     """,
            #     unsafe_allow_html=True
            # )
            # st.markdown(f"Total Tokens: {total_tokens_str}")

            # if model == "gpt-4.1-nano":
            #     input_token_cost = .1/1000000
            #     output_token_cost = .4/1000000
            # elif model == "gpt-4o-mini":
            #     input_token_cost = .15/1000000
            #     output_token_cost = .6/1000000
            # elif model == "gpt-4.1":
            #     input_token_cost = 2.00/1000000
            #     output_token_cost = 8.00/1000000
            # elif model == "o4-mini":
            #     input_token_cost = 1.10/1000000
            #     output_token_cost = 4.40/1000000

            # cost = input_tokens*input_token_cost + output_tokens*output_token_cost
            # formatted_cost = "${:,.4f}".format(cost)
            
            # st.markdown(f"**Total Cost:** {formatted_cost}")

    # elif not submit:
    #         st.markdown("#### Response")
    #         st.markdown(st.session_state.ai_response)

elif st.session_state.get('authentication_status') is False:
    st.error('Username/password is incorrect')

elif st.session_state.get('authentication_status') is None:
    st.warning('Please enter your username and password')

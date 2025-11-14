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
    INSTRUCTION_ENCRYPTED = b'gAAAAABpFqOKzurOJfOcgNoDIcwZKTQnrvTMB5Ff7PJkjrD1FPZBrPGSRc53H6I-CuzwZl5wc8es1riYycA8xgthWA06NCIlx1wFRFUdhokqNbOtoadE6NuNhA17n1USgEAwFiRUz5TG5QF1UZzvAXtZiIRbhschQY0o6J2bIs1W68E-9O0E08D3KxJUgd3GUOI2mSP9Tgzjyc2pVafucfkO11JKW8TyfadDPImpVK2B9Tz6Dsb-V6hsgw7-gUz_D-VoJHjgNo6J5HGtNEQcNwkBktOpeEFTKJvyIPHbNTPdB-1XeYkecHMzhwUho0Lc_T_SCOq-0sZS8n4h0m-DQAmR5sa58NUCdPYQZeAOkByNKuopioZhqqGsBELKtj4E8WEPSn75zp2mIqQGrr2fRFv7n-9Ebq4TR0_mjsizzZ96HbhbySTMMTgFkaMsRs1qACEY8MMpgM48wqt6i7Uc_OYpBBi_RYhpYFlwHk8bDJ15H4n1as7IfKlNvN-5ZoTXzTN6T9IVZA5won2LTYUOjpLkQdcttQjVn9LnTh_vrYjBUm5a4mxAoFalAKKNXf74iUT_Vu32WFHS2hiGlKgK1xPb9opyUhYoYnvtgA75dtqbqCUwGLDhmjL2N5IQUoJq351kvcFo88tVigmJvrqqxoVWQW_bItkVDuETNhCx7ouDvu3kQn1ttcx9y0A-nTsaRO_MCLa8wjaIMsWYRtQjooeUm9ximVoeyJSvDG0-_pfOkbJsRe4ibg9ovYpHw6ChLCM5wPSkpDZrE25BYswEdpkyZc5Z50x1dtbJDbgTaRgiAuLD42VY0V8UmC7byuxdB9bQGFzAj7ZdhFwezWc5aGCyWOxG5UDw1ekhMz55YU3gr1B3GEgMWz3-uC2W8zT2O-7SvJZl9sw4u4O2XngCbpIM-KUwJj-ic1mgGgfxPMKAQ2_RQij1c2xD4SOzoG8AhMWU1dMBPx7BnnjIWwgqWvbQ7EY8SKqfDj2wXRYIZQ0B2ZaX6Ou4iKjgI6Q_KNLQum6BmgVD3huBfsjqSbf3C9klNNL_L_BSmNJOLWEoyAMtN9BCa7FpOk5M1rzil2CELQXxJ7cso_Od3wIl_lNd1qH0AqjiJUHsw1GziEyylwAIqfkJvK6yXL8-80b68lEKC1bgrSQCK3TMdOY8EThyGZN1x8P6fBv9-_F1tXKnLOZb1_YSJtEtiXnYD32awLB-4W0f_mPBP5RNd_qRkOJLiX25oAsncP4pOyTue2lMNmaC6hxK0H2rY4ZUxUXciftyAIiDvj4urh14zXbBZFyFW4ow3kjhcszKwipCsTOH3SVBBszxrHGd_mS8x08rKEfdh4MaiZvKG51rd8oeT8D7tk4cy0gK_Cycs6Nh3wBMyD-Rtt9uu2B_MzoazIV97O-DJS82Cj4xJpmwjDSBb4uL-o-OQcC1mqvzZVRKv-OEEVToQnc9SPqb33P8hoK0Gf7ceHHFiNf4qLuzbou_cApo8iQBk2SqdT62y7UsxHMTIfm4U3jGSXgVqfuovrczdNYXPtzcrnQ3bxfgli_wVNJXT8gz7wJ2NZp4JiQ3Bj2poipju5-FUg1VSDbInAc3cl2QuS_25xK86czT-w54pxlMFqp9K9fDrJq4gMg_n7U8800iWwUOy0PxqgWMzem-29tmmsQ4YzJdDh1QBg7JGegnOiU0muMvffOEA6jTOz4rvgOUMZYweAUdDwskVvuGg8rADC2qdAYEQIfa0y5PhQUz120f6EtfyOpLSTC05R6LTIro7bZNrBxaZxpXUKMtG7OZsNsT3JtQZ3AFuwCJyQak4MTGeWqtwGdrssoC58cvwA29itE7fhFkYACkX0PK41XLJXCu-GABawL0EJAb_P-ib7ANzwtn2Vz8IBTqvyrzSZxX49wxEwBFmLIRcXca-7_XZDFLOFajv1bMz4vhAPThfdhhpiBUPuunVD-HH4j0CJkbC0TnWLpT4AuoDMTgXtW5Rvo_lCrurbSw-RZn67GQTNGgOpDB86XEcDaJ87SwGFCX6zwCZbSFMv-WQOHukufdtOqKbQ4Tp-2l0I5TIPh0DGj4RHmF04Tf59TgpZDmravNJ0CNKMUDrJbh-zx51hUlnIsSOkiiSOfwGfN7FGexQyKrac4g696w_FWiL2yi5e3tTrXnXcYAPgoVeA3_zbiZo4WbnZ1xMKjv5lnW6cYTVigjNBAsA4D-j83SI4LGUEeQLT8pTXHwIvEEXEfHnTptk31xsusCMXMNW0wi8dK0QkmvrkKwGEqaxMVr1CXmpUycP4gh9mLbC1CBMKw6hGVPyrj2i77N_gB9TCs9V4_bQrwpsWp-vwiv-xpFuMNe1gnKewpad0XAy4DnYmv4nGRQFvuLdWucrWlpXJQmm4H12IKY-9OgDoOaKFCr59UBMly3S2G3wJvwqVoiODPE4OfWUri3mdraZrzoeSBCASvZKJoGb12_u1XlbHuREx1T2GxTBvErG4Q1J5m5s29dQp3PNvSg1SAEOkslH5ykkqKqwNQP3-_55ZNbjZyYkZSCxsTDTIMqSjhYxVEjFs8X7CbsG-Uvh-cdLi5zvGPm0bBVwQcdM-LOotxjhZIf1XiO0t68iJ_rXQ7bU4PX4CKtgWLGXpgKg0r31f_J57xsHw5TbN0B7IeZjYRC6BcA1smNemX3rekFssL7IW64ndPDZwGvolOxfIjO4VBQY7KBoEXm9uWOV-aHIF1ooKOBN9zVMe9M65fk1Fcb_x9OuxUGUv0ho_d2rz_MOB8oR00QhxL3Qj-9_rDiZsbCzzfwnHMzB6tmpaNaNrqna3KhHV0FwjQd5WLMaRt8YT_JtDScxAce4NzXxGhtoRkE2KkDiumWJkGYs1N3jd0HybsNyV5OrOQ8kMd3jgoLsNeKU6y1UJjQgSZwSUpQKySSVntL9Aj3ZO0IpjgjYn0Y9AmNhCqLD-hoak7vFrlG0YP8Nir1ijYOSTKNF4sR3v_Ow3G__ghtkOca4Yp6gwxWYsVP33eGpREgLPagRZlQGwK95gia6u7DXZTt6dW7XC0tEFGzl5_Ygks86HcIa8zJolrqQP-7jUmxudOktsbXX0IMJ6P28sF6bWZSbURUI0awCAoWFLkAE6RXNtCjYDzlxQghrptRnYfnnarpJ6Dh4PK2DTUrdEm-rBHMg6G458vH9i_RVLzE5UV8ExIIiCVKKoOhya0rFI9QmdUH5jVRfLBGzmDqYX7tgQkkenp7AgALQJt1g1yxoDmdXVL5xJf6_E5keCELmuiOChD8fAkbP-qqwF4xtj8X_eufOwW_h0CAkHC3zfqA2K_BaglHmI0-2UpuUMdX-VvlfB8F-7uJxkxZLvtIr6lPh1z4N2POd2WbfLc7_A7Ob0dB0B8BPKncSNIkxR8uCccCVOW1FZNAtaeZnZgVA3f0D2diri_ZgpuWujqumKIbqJ0hx-lbvSIpi-RMlUWCNtw3HRAUEjcB56n05j18wojcEy57cWlX-TYqnLFr6HfOjY5nSeJhjFMqBEotW3eb54GKD9THJRTX89xlk_6pxIkyuV1oclCY9ZDR8WTMPT_7cPWDEXCFuzeGI1SXrT7Wm6PWt1pNPFcE-jOtlOzwpqTevcPrWc8tDIknCe8hDSkzTr5mQ7eSkD7F18bSHZQ00OsN7Tzh3pypz7JsZ6gtwc_HfW4yef9Gs2PMp0Prc4O1nnddeGqkaalI6rcC-0YqshDFwNf2jg12Uux_-aqvYUzDTL3sCBESZffU-qm0A_cD928ta_1mQqAqst0hAAUTuCU9V7g9QL5SNhtupGGFljyXggcZzJRxshqDu5omAXrOovPM_PE22XShjjLRZBz3tuEz0Xr8xXobnZm1J7gfxsFmhiHMaBbW_iGg3Kew71sGAmPMyd77WhxS0FXP0naZSJ4H2O8p9JcG2Y4-a1mVg6sfeV3OoKQvflbcvL4N2nwntXy4lWlc8akR_bA2f4NgM5AD-FxSHqzFw_uEDf-QLtWXzRGiJW6wee_BeGGVDy1z_StcJtV21Nysu-CT_kw4Gmx9T1KN6hLjkuA9Rz81XJVAb5HR8d2zQMVaizfttSinwB8HZuqIhDPfZQLsyyRY6iGFrabFa9Yx0Dowqykk61g24or4PqlcG4QNzwl55g2MOwE3wuzv0zTFL7CJpg-VSSK7QKP3LTBtY7dKw_zJ1uhXBOxWh585CPI5jkLKiBJM4Piza2Bnev8PA06vYGNxFshNOPB63srrgq97UCu78GWMb2ssC5qeTtOX3ktzlknqynAaVfIt8zijUbHm8oPfix8WJJH6NpPxC5m1ZWRgkautKteUQSXY7M7SJA64jkX3NIbtJil_2MORwzia-7kExzbCr7aclw3sfIcOvtiTa1CW_vBPNisEe6QmO4mon2PsPuCkG-i9lvfTBUuMT-IYJBc_ZnEECvi2ZVnq4xr2fsa12EDajb629WhrzyRmMV0VNzY6_boDlehXKLaNUO6-hn8UYBLMpnFpe-FtJHQvFDr0oXqo-fMpb_LYSE3YjAieY20SMKsEJNRHPeHGddXfRjqFJMTGUsmnZ9RGOYwRM5d3i_EnroupxQ9rnQ=='

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

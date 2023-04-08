import streamlit as st
import pandas as pd
import numpy as np
import cloudinary
from cloudinary.uploader import upload
from cloudinary.api import resource

st.set_page_config(
    page_title="Discord Moderation Log",
    page_icon="https://cdn-icons-png.flaticon.com/512/5968/5968756.png",
    layout="wide"
)

st.header("Discord Moderation Log")
st.write("This is a simple moderation actions log app for the Streamlit Discord server.")

# DB initialization operations

cloudinary.config(
  cloud_name = st.secrets["cloud_name"],
  api_key = st.secrets["api_key"],
  api_secret = st.secrets["api_secret"],
  secure = True
)

def read_df():
    try:
        df = pd.read_feather(resource("moderation_log.feather", resource_type="raw")["url"])
        return df
    except:
        df = pd.DataFrame(columns=["Discord Username", "Action Taken", "Date", "Action Taken By", "Reason"])
        return df

def save_to_cloudinary(df):
    df = df.reset_index(drop=True)
    df.to_feather("moderation_log.feather")
    object = upload("moderation_log.feather", public_id="moderation_log.feather", resource_type="raw", overwrite=True)

tab1, tab2, tab3 = st.tabs(["Search for a specific user", "Add New Entry", "See/Edit Complete Database"])

# Specific User Section

with tab1:
    username = st.text_input("Enter Discord Username to search for")

    if username:
        df = read_df()
        user_data = df[df["Discord Username"] == username]
        if(len(user_data)==0):
            st.write("Given user is a first time offender, please add new entry")
        else:
            specific_user_data = st.experimental_data_editor(user_data, key="specific data", use_container_width=True)
            if st.button("Save Changes", key="update specifc data"):
                # replace empty strings / complete whitespaces with NaN
                temp_specific_user_data = specific_user_data.replace(r'^\s*$', np.nan, regex=True)
                temp_specific_user_data = temp_specific_user_data.dropna(how='all')  # drop rows with all NaN values
                
                x = list(set(temp_specific_user_data["Discord Username"]))

                if len(temp_specific_user_data) == 0:
                    df = df[df["Discord Username"] != username]
                    save_to_cloudinary(df)
                    st.success("Changes Saved Successfully", icon="✅")
                elif temp_specific_user_data.isnull().values.any():
                    st.error("NULL values not allowed in the Database", icon="🚨")
                elif len(x)>1 or x[0]!=username:
                    st.error("Username Change Not Allowed", icon="🚨")
                else:
                    df = df[df["Discord Username"] != username]
                    df = pd.concat([df, specific_user_data], ignore_index=False)
                    save_to_cloudinary(df)
                    st.success("Changes Saved Successfully", icon="✅")


# New User Section

with tab2:
    with st.form(key="new entry form"):
        c1, c2 = st.columns(2)
        discord_username = c1.text_input("Enter Discord Username")
        action_taken = c2.text_input("Enter Action Taken")
        date = c1.text_input("Enter Date")
        action_taken_by = c2.text_input("Enter Action Taker's Name")
        reason = st.text_area("Enter Reason")

        submitted = st.form_submit_button("Add Entry")

        if submitted:
            if len(discord_username) == 0 or \
                len(action_taken) == 0 or \
                len(date) == 0 or \
                len(action_taken_by) == 0 or \
                len(reason) == 0:
                st.error("Please fill all the fields and re-submit the form", icon="🚨")
            else:
                df = read_df()
                df.loc[len(df)] = [discord_username, action_taken, date, action_taken_by, reason]
                save_to_cloudinary(df)
                st.success("New Entry Added Successfully", icon="✅")


# Complete DB Section

with tab3:
    st.warning("Please be careful while making changes", icon="⚠️")
    df = read_df()
    edited_df = st.experimental_data_editor(df, num_rows="dynamic", key="Full DB", use_container_width=True)

    if st.button("Save Changes", key="save complete db"):
        # replace empty strings / complete whitespaces with NaN
        temp_edited_df = edited_df.replace(r'^\s*$', np.nan, regex=True)
        temp_edited_df = temp_edited_df.dropna(how='all')  # drop rows with all NaN values

        if len(temp_edited_df) == 0:
            st.error("Database cannot be empty", icon="🚨")
        elif temp_edited_df.isnull().values.any():
            st.error("NULL values not allowed in the Database", icon="🚨")
        else:
            save_to_cloudinary(temp_edited_df)
            st.success("Changes Saved Successfully", icon="✅")

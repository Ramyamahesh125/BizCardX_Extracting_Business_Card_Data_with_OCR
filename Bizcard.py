
import easyocr
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
from PIL import Image
import re
import io
import sqlite3

# Converting Image To Text Format:
def image_to_text(path):

    input_image = Image.open(path)

    # Converting image to array format
    image_arr = np.array(input_image)

    reader = easyocr.Reader(['en'])
    text = reader.readtext(image_arr, detail = 0)

    return text, input_image

def extracted_text(texts):
    extracted_dict = {"NAME":[],
                     "DESIGNATION":[],
                     "COMPANY NAME":[],
                     "CONTACT":[],
                     "E-MAIL":[],
                     "WEBSITE":[],
                     "ADDRESS":[],
                     "PINCODE":[]}

    extracted_dict["NAME"].append(texts[0])
    extracted_dict["DESIGNATION"].append(texts[1])

    for i in range(2, len(texts)):

        if texts[i].startswith("+") or (texts[i].replace("-","").isdigit() and '-' in texts[i]):
            extracted_dict["CONTACT"].append(texts[i])

        elif "@" in texts[i] and ".com" in texts[i]:
            extracted_dict["E-MAIL"].append(texts[i])

        elif "WWW" in texts[i] or "www" in texts[i] or "Www" in texts[i] or "wWw" in texts[i] or "wwW" in texts[i]:
            small = texts[i].lower()
            extracted_dict["WEBSITE"].append(texts[i])

        elif "Tamil Nadu" in texts[i] or "TamilNadu" in texts[i] or texts[i].isdigit():
            extracted_dict["PINCODE"].append(texts[i])

        elif re.match(r'^[A-Za-z]' , texts[i]):
            extracted_dict["COMPANY NAME"].append(texts[i])

        else :
            remove= re.sub(r'[,;]', '', texts[i])
            extracted_dict["ADDRESS"].append(remove)

    for key,value in extracted_dict.items():
        if len(value) > 0:
            concadenate = "".join(value)
            extracted_dict[key] = [concadenate]

        else :
            value = "NA"
            extracted_dict[key] = [value]

    return extracted_dict

# Streamlit

st.set_page_config(layout = "wide")
st.title("BIZCARDX : EXTRACTING BUSINESS CARD DATA WITH 'OCR'")

with st.sidebar:
  select = option_menu("Main Menu",["Home", "Upload","Modify", "Delete"],
      icons=['house','upload', 'tools','star'], menu_icon="cast", default_index=1)

if select == "Home":
  col1, col2 = st.columns(2)
  with col1:
    st.subheader("OCR")
    st.write("Optical Character Recognition (OCR) is the process that converts an image of text into a machine-readable text format.")
    st.write("For example, if you scan a form or a receipt, your computer saves the scan as an image file.")
    st.write("You cannot use a text editor, search, or count the words in the image file.")
    st.write(" However, you can use OCR to convert the image into a text document with its content stored as text data")
    st.write("")
    st.write("")
  with col2 :
    st.image(Image.open("/content/Bizcard Image.jpg"))

  st.subheader("Importance Of OCR")
  st.write("Most business workflows involve receiving information from print media. Paper forms, invoices, scanned legal documents")
  st.write("and printed contracts are all part of bussiness processes. These large volume of paperwork take a lot of time and space")
  st.write("to store and manage. Though paperless document management is the way to go, scanning the document into an image creates")
  st.write("challenge. The process requires manual intervention and can be tedious and slow. Moreover, digitizing this document content ")
  st.write("image files with the text hidden within it. Texts in images cannot be processed by word processing software in the same way")
  st.write("as text documents. OCR technique solves the problem by converting text images into text data that can be analysed by other")
  st.write("business software. You can then use the data to conduct analytics, streamline operations, automate processes and improve")
  st.write("productivity")

  st.subheader("Technologies Used Here")
  st.write("OCR, Streamlit GUI, SQL, Data Extraction, Data Modification")

  st.subheader("Project Overview")
  st.write("BizCardX : Extracting Business Card Data with allows user to upload an image of a business card and extract its relavant information")
  st.write("which includes company name, card holder name, designation, mobile number, email address, website URL, area, city, state")
  st.write("and pincode. The extracted information should then be displayed in the application Graphical User Interface(GUI) the" )
  st.write("application should allows the users to save the extracted information into the database.")

elif select == "Upload":
  st.subheader("Here you can upload the image and extract its contents ")
  img = st.file_uploader("Upload The Image To Extract The Data:", type = ["png", "jpg", "jpeg"])

  if img is not None:
    st.image(img, width = 500)

    text_img, input_img = image_to_text(img)

    text_dict = extracted_text(text_img)

    if text_dict:
      st.success("Text is extracted successfully !!!")

    df = pd.DataFrame(text_dict)

    # Converting Image to bytes :

    image_bytes = io.BytesIO()
    input_img.save(image_bytes, format = "PNG")

    image_data = image_bytes.getvalue()

    # Creating Dictionary :

    data = {"Image":[image_data]}

    df_1 = pd.DataFrame(data)

    concat_df = pd.concat([df, df_1], axis = 1)

    st.dataframe(concat_df)

    button_1 = st.button("Save", use_container_width= True)

    if button_1 :
      mydb = sqlite3.connect("Bizcard, db")
      cursor = mydb.cursor()

      # Creating  Table :

      create_query = ''' create table if not exists Bizcard_Data(Name varchar(255),
                                                                Designation varchar(255),
                                                                Company_Name varchar(255),
                                                                Contact varchar(255),
                                                                EMail varchar(255),
                                                                Website varchar(255),
                                                                Address Varchar(255),
                                                                Pincode varchar(255),
                                                                Image text)'''

      cursor.execute(create_query)
      mydb.commit()

      # Insert query :

      insert_query = ''' insert into Bizcard_Data(Name, Designation, Company_Name, Contact, EMail, Website, Address, Pincode, Image)

                                                  values(?,?,?,?,?,?,?,?,?)'''

      values = concat_df.values.tolist()[0]
      cursor.execute(insert_query, values)
      mydb.commit()

      st.success("Saved Successfully !!!")

  button = st.button("Preview", use_container_width = True)

  if button :

    mydb = sqlite3.connect("Bizcard, db")
    cursor = mydb.cursor()

    # select_query

    select_query = ''' select * from Bizcard_Data'''

    cursor.execute(select_query)
    table = cursor.fetchall()
    mydb.commit()

    table_df = pd.DataFrame(table, columns =['Name', 'Designation', 'Company_Name', 'Contact', 'EMail', 'Website', 'Address',
                                            'Pincode','Image'])
    st.dataframe(table_df)

elif select == "Modify":

  st.subheader("Here you can modify the details :")

  mydb = sqlite3.connect("Bizcard, db")
  cursor = mydb.cursor()

  # select_query

  select_query = ''' select * from Bizcard_Data'''

  cursor.execute(select_query)
  table = cursor.fetchall()
  mydb.commit()

  table_df = pd.DataFrame(table, columns =['Name', 'Designation', 'Company_Name', 'Contact', 'EMail', 'Website', 'Address',
                                          'Pincode','Image'])
  col1, col2 = st.columns(2)
  with col1 :

    selected_name = st.selectbox("Select The Name:", table_df["Name"])

  df_3 = table_df[table_df["Name"] == selected_name]

  df_4 = df_3.copy()

  col1, col2 = st.columns(2)
  with col1:
    md_name = st.text_input("Name",df_3["Name"].unique()[0])
    md_des_name = st.text_input("Designation",df_3["Designation"].unique()[0])
    md_com_name = st.text_input("Company_Name",df_3["Company_Name"].unique()[0])
    md_cont = st.text_input("Contact",df_3["Contact"].unique()[0])
    md_mail = st.text_input("EMail",df_3["EMail"].unique()[0])

    df_4["Name"] = md_name
    df_4["Designation"] = md_des_name
    df_4["Company_Name"] = md_com_name
    df_4["Contact"] = md_cont
    df_4["EMail"] = md_mail


  with col2 :
    md_web = st.text_input("Website",df_3["Website"].unique()[0])
    md_add = st.text_input("Address",df_3["Address"].unique()[0])
    md_pin = st.text_input("Pincode",df_3["Pincode"].unique()[0])
    md_img = st.text_input("Image",df_3["Image"].unique()[0])

    df_4["Website"] = md_web
    df_4["Address"] = md_add
    df_4["Pincode"] = md_pin
    df_4["Image"] = md_img



  button_3 = st.button("Modify", use_container_width = True)


  if button_3 :

    mydb = sqlite3.connect("Bizcard, db")
    cursor = mydb.cursor()

    cursor.execute(f"delete from Bizcard_Data where Name ='{selected_name}'")
    mydb.commit()

    # Insert query :

    insert_query = ''' insert into Bizcard_Data(Name, Designation, Company_Name, Contact, EMail, Website, Address, Pincode, Image)

                                                values(?,?,?,?,?,?,?,?,?)'''

    values = df_4.values.tolist()[0]
    cursor.execute(insert_query, values)
    mydb.commit()


    st.subheader("Modified Dataframe:")

  st.dataframe(df_4)

  st.success("Modified Successfully !!!")

elif select == "Delete":

  st.subheader("Here you are able to delete the existed data:")

  mydb = sqlite3.connect("Bizcard, db")
  cursor = mydb.cursor()

  col1, col2 = st.columns(2)
  with col1 :
    # select_query

    select_query = ''' select Name from Bizcard_Data'''

    cursor.execute(select_query)
    table_1 = cursor.fetchall()
    mydb.commit()

    names = []

    for i in table_1 :
      names.append(i[0])

    name_selection = st.selectbox("Select The Name:", names)

    if name_selection:
      st.subheader(f"You have selected {names[0]}'s name!")

  if name_selection :


    remove = st.button("Delete",use_container_width= True )

    if remove:
      cursor.execute(f'''delete from Bizcard_Data
                        where Name = '{name_selection}' ''')

      mydb.commit()

      st.warning(f"Deleted {name_selection}'s Details Successfully !")







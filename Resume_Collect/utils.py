from pdfminer.high_level import extract_text
import spacy
import re
from word2number import w2n

"""Functions to extract text of docs"""
def extract_text_from_pdf(pdf_path):

    return extract_text(pdf_path)


"""Function to fix error related to null bytes"""
def remove_null_bytes(input_str):
    string = str(input_str)
    return string.replace('\x00', '')


"""New function for reading pdf DOESNT WORK"""
from django.core.files.storage import default_storage
from pdfminer.high_level import extract_text

"""def read_pdf(file):
    # Save the uploaded file to disk
    path = default_storage.save(file.name, file)

    # Extract text from the PDF file
    text = extract_text_from_pdf(path)

    return text"""
from pdfminer.high_level import extract_text
from io import BytesIO

def read_pdf(file_object):
    # Create a BytesIO object from the InMemoryUploadedFile
    pdf_data = BytesIO(file_object.read())
    # Use the BytesIO object with extract_text() function
    text = extract_text(pdf_data)
    return text

def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)

def extract_candidate(text):
    candidate = {'phone': None, 'email': None, 'name': None, 'education': None, 'experience': None, 'text_list': None}
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    """PHONE"""
    phone_pattern = re.compile(r'\(?\d{3}\)?[-.\s]*\d{3}[-.\s]*\d{4}')
    match = re.findall(phone_pattern, doc.text)
    if match == []:
        candidate['phone'] = None
    else:
        phone = match[0].replace(" ", "")
        phone = phone.replace("(", "")
        phone = phone.replace(")", "-")
        candidate['phone'] = phone
    """EMAIL"""
    email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    match = re.findall(email_pattern, doc.text)
    if match == []:
        candidate['email'] = None
    else:
        candidate['email'] = match[0]

    name = ""
    school_level = ['HS', 'H.S.', 'GED', 'SECONDARY EDUCATION', 'SCHOOL', 'HIGH SCHOOL']
    associate_level = ['AA', 'A.A.', 'ASSOCIATE OF ARTS', 'A.S.', 'ASSOCIATE OF SCIENCE', 'ASSOCIATE'] 
    bachelor_level = ['BA', 'B.A.', 'BACHELOR OF ARTS', 'BS', 'B.S.', 'BACHELOR OF SCIENCE', 'BACHELOR']
    master_level = ['MA', 'M.A.', 'MASTER OF ARTS', 'MS', 'M.S.', 'M.Sc.', 'MSc', 'MASTER OF SCIENCE', 'MASTER'] 
    doctor_level = ['M.D.', 'MD', 'DOCTOR OF MEDICINE', 'J.D.', 'JD', 'JURIS DOCTOR', 'PH.D.', 'PHD', 'DOCTOR OF PHILOSOPHY', 'ED.D.', 'EDD', 'DOCTOR OF EDUCATION', 'DOCTOR', 'DOCTORATE', 'DR.']
    next_token = 0
    nexxt_token = 0
    nexxxt_token = 0
    nexxxxt_token = 0
    space_list = ['', ' ', '  ', '   ', '    ', '     ', '      ', '       ', '        ', '         ', '          ']
    text_list = []
    combined = []
    for i, token in enumerate(doc):
        """NAME"""
        if candidate['name'] == None:
            if token.pos_ == "PROPN":
                name += token.text + " "
            else:
                if name == '':
                    candidate['name'] = 'None'
                else:
                    candidate['name'] = name[:-1]
        """EDUCATION"""
        next_token += 1
        if candidate['education'] == None:
            if token.text.upper() in doctor_level:
                candidate['education'] = 'Doctor'
            elif token.text.upper() in master_level:
                candidate['education'] = 'Master\'s'
            elif token.text.upper() in bachelor_level:
                candidate['education'] = 'Bachelor\'s'
            elif token.text.upper() in associate_level:
                candidate['education'] = 'Associate\'s'

            elif next_token < len(doc):
                compound_word_2 = ("{} {}".format(token.text.upper(), doc[next_token]).upper())
                if compound_word_2 in doctor_level:
                    candidate['education'] = 'Doctor'
                elif compound_word_2 in master_level:
                    candidate['education'] = 'Master\'s'
                elif compound_word_2 in bachelor_level:
                    candidate['education'] = 'Bachelor\'s'
                elif compound_word_2 in associate_level:
                    candidate['education'] = 'Associate\'s'

            elif (next_token + 1) < len(doc):
                compound_word_3 = ("{} {} {}".format(token.text.upper(), doc[next_token]).upper(), doc[next_token + 1].upper())
                if compound_word_3 in doctor_level:
                    candidate['education'] = 'Doctor'
                elif compound_word_3 in master_level:
                    candidate['education'] = 'Master\'s'
                elif compound_word_3 in bachelor_level:
                    candidate['education'] = 'Bachelor\'s'
                elif compound_word_3 in associate_level:
                    candidate['education'] = 'Associate\'s'

        """EXPERIENCE"""
        nexxxt_token += 1
        if candidate['experience'] == None:
            if nexxxt_token < len(doc):
                if token.like_num and doc[nexxxt_token].text == 'years':
                    if token.is_alpha:
                        word_to_num = w2n.word_to_num(token.text)
                        candidate['experience'] = f'{word_to_num} years'
                    else:
                        candidate['experience'] = f'{token.text} years'
                elif token.like_num and doc[nexxxt_token + 1].text == 'years':
                    if token.is_alpha:
                        word_to_num = w2n.word_to_num(token.text)
                        candidate['experience'] = f'{word_to_num} years'
                    else:
                        candidate['experience'] = f'{token.text} years'

        """TEXT_LIST"""
        if token.dep_ != 'det' and not token.is_punct and "\n" not in token.text and "\uf0b7" not in token.text and token.like_num is not True and token.text != ' ' and token.text not in space_list:
            token_text = token.text.lower()
            text_list.append(token_text)

            if i + 1 < len(doc):
                token_next = doc[i+1]
                if token_next.dep_ != 'det' and not token_next.is_punct and "\n" not in token_next.text and "\uf0b7" not in token_next.text and token_next.like_num is not True and token_next.text != ' ' and token_next.text not in space_list:
                    compound_word_2 = "{} {}".format(token_text, token_next.text.lower())
                    combined.append(compound_word_2)

                if i + 2 < len(doc):
                    third_token = doc[i+2]
                    if third_token.dep_ != 'det' and not third_token.is_punct and "\n" not in third_token.text and "\uf0b7" not in third_token.text and third_token.like_num is not True and third_token.text != ' ' and third_token.text not in space_list:
                        if token_next.dep_ != 'det' and not token_next.is_punct and "\n" not in token_next.text and "\uf0b7" not in token_next.text and token_next.like_num is not True and token_next.text != ' ' and token_next.text not in space_list:
                            compound_word_3 = "{} {} {}".format(token_text, token_next.text.lower(), third_token.text.lower())
                            combined.append(compound_word_3)

    text_list.extend(combined)
    candidate['text_list'] = text_list

    """IF NO HIGHER EDUCATION FOUND"""
    if candidate['education'] == None:
        for token in doc:
            nexxt_token += 1
            if token.text.upper() in school_level:
                candidate['education'] = 'Certificate'
            elif nexxt_token < len(doc):
                compound_word_2 = ("{} {}".format(token.text.upper(), doc[nexxt_token]).upper())
                if compound_word_2 in school_level:
                    candidate['education'] = 'Certificate'
            elif (nexxt_token + 1) < len(doc):
                compound_word_3 = ("{} {} {}".format(token.text.upper(), doc[nexxt_token]).upper(), doc[nexxt_token + 1].upper())
                if compound_word_3 in school_level:
                    candidate['education'] = 'Certificate'
    
    return candidate
"""Coversheet adder for online exams in Year 2 Maths.

Credits:
* https://stackoverflow.com/questions/1180115/add-text-to-existing-pdf-using-python
* Walter Shen wrote the code to personalise coversheets
* Danilo Jr Dela Cruz wrote code to merge coversheets and cmd line interface.
"""

import argparse
import io

from argparse import RawTextHelpFormatter
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import date


MODULES = {
    'MATH50001': 'Analysis II',
    'MATH50003': 'Linear Algebra and Numerical Analysis',
    'MATH50004': 'Multivariable Calculus and Differential Equations',
    'MATH50005': 'Groups and Rings',
    'MATH50006': 'Lebesgue Measure and Integration',
    'MATH50007': 'Network Science',
    'MATH50008': 'Partial Differential Equations in Action',
    'MATH50009': 'Principles of Programming',
    'MATH50010': 'Probability for Statistics',
    'MATH50011': 'Statistical Modelling 1'
}


def personalise_coversheet(cid, module_code, questions_attempted):
    """Personalise coversheet with student information."""
    packet = io.BytesIO()

    can = canvas.Canvas(packet, pagesize=letter)
    can.drawString(100, 701, cid)
    can.drawString(158, 655, MODULES[module_code])
    can.drawString(158, 609, module_code)
    can.drawString(105, 563, str(date.today()))

    for q in questions_attempted:
        can.drawString(145, 485-(q)*13.7, "✓")

    can.save()
    packet.seek(0)
    cs_details = PdfFileReader(packet)

    return cs_details


def add_coversheet(input_dir, output_dir, cid, module_code, questions_attempted):
    """Add question to coversheet and create output file."""

    cs_details = personalise_coversheet(cid, module_code, questions_attempted)

    # Files need to be open for the entirety of the merge
    with open("template.pdf", "rb") as template, \
         open(input_dir, "rb") as question, \
         open(output_dir, "wb") as outputStream:
        template_pdf = PdfFileReader(template)
        question_pdf = PdfFileReader(question)

        page = template_pdf.getPage(0)
        page.mergePage(cs_details.getPage(0))

        coversheet = PdfFileWriter()
        coversheet.addPage(page)    
        coversheet.appendPagesFromReader(question_pdf)
        coversheet.write(outputStream)


def by_question(cid, module_code, number_of_questions):
    """Create a coversheet for each question.

    This is typically the format required for longer exams such as Summer.
    
    Parameters
    ----------
    cid : str
        College Identification Number (e.g., 01701234)
    module_code: str
        Module Code (e.g., MATH50001)
    number_of_questions: int
        Number of questions being submitted.

    It is assumed that the questions are in separate files and are found in
    Input/[module_code] Q[q_number]. Each file will be processed and placed in
    Output/[cid]_[module_code]_Q[q_number].
    """
    assert module_code in MODULES, f'{module_code} is invalid'

    for q in range(1, number_of_questions+1):
        try:
            input_dir = f'Input/{module_code} Q{q}.pdf'
            output_dir = f'Output/{cid}_{module_code}_Q{q}.pdf'
            add_coversheet(input_dir, output_dir, cid, module_code, [q])
            print(f'Question {q} has been processed successfully.')
        except Exception as e:
            print(f'Error in creating output for question {q}.')
            print(e)


def full_submission(cid, module_code, number_of_questions):
    """Create one coversheet for all questions.

    This is typically the format required for midterms.

    It is assumed that the questions are all in one file found in 
    Input/[module_code].pdf One coversheet will be added to the file and output 
    will be placed in Output/[cid]_[module_code]_full_submission.pdf.
    
    Parameters
    ----------
    cid : str
        College Identification Number (e.g., 01701234)
    module_code: str
        Module Code (e.g., MATH50001)
    number_of_questions: int
        Number of questions being submitted.
    """
    assert module_code in MODULES, f'{module_code} is invalid'

    input_dir = f'Input/{module_code}.pdf'
    output_dir = f'Output/{cid}_{module_code}_full_submission.pdf'
    add_coversheet(input_dir, output_dir, cid, module_code, 
                                        range(1, number_of_questions + 1))

    print('Success! Output file has been placed in Ouput.')


if __name__ == "__main__":
    description = """example usage: python3 covadd.py full 01701234 MATH50001 6.

Ensure that you are in the same folder as covadd.py and that there are
folders called Input and Output and a template file for the coversheet. 

Current directory should have
Input Output covadd.py template.pdf
    """
    parser = argparse.ArgumentParser(description = description,
                                        formatter_class= RawTextHelpFormatter)

    parser.add_argument("mode",     type=str, help="(full/by_q) Output format.")
    parser.add_argument("cid",      type=str, help="College Identifier.")
    parser.add_argument("mod_code", type=str, help="Module Code. E.g., MATH50001")
    parser.add_argument("q_no",     type=int, help="Number of questions being submitted.")
    args = parser.parse_args()

    if args.mode == "full":
        full_submission(args.cid, args.mod_code, args.q_no)
    elif args.mode == "by_q":
        by_question(args.cid, args.mod_code, args.q_no)
    else:
        print(f'{args.mode} is invalid. Use one of (full/by_q).')

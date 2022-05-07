"""Coversheet adder for online exams in Year 3 Maths.

Credits:
* https://stackoverflow.com/questions/1180115/add-text-to-existing-pdf-using-python
* Walter Shen wrote the code to personalise coversheets
* Danilo Jr Dela Cruz wrote code to merge coversheets 
"""

import argparse
import io
import os
import shutil

from argparse import RawTextHelpFormatter
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import date


MODULES = {
    "MATH60012": "Mathematical Finance: An Introduction to Option Pricing",
    "MATH60026": "Methods for Data Science",
    "MATH60031": "Markov Processes",
    "MATH60043": "Statistical Theory",
    "MATH60045": "Applied Probability",
    "MATH60046": "Time Series Analysis",
    "MATH60047": "Stochastic Simulation",
    "MATH60048": "Survival Models",
}

FILE_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
DEFAULT_TEMPLATE_DIR = f"{FILE_DIRECTORY}/template.pdf"

class CoverSheetAdder:

    def __init__(self, cid, module_code, number_of_questions, input_dir, output_dir, template_dir=DEFAULT_TEMPLATE_DIR):
        self.cid = cid
        self.module_code = module_code
        self.number_of_questions = number_of_questions
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.template_dir = template_dir

        assert self.module_code in MODULES, f"{self.module_code} is not recognised."


    def personalise_coversheet(self, questions_attempted):
        """Personalise coversheet with student information."""
        packet = io.BytesIO()

        can = canvas.Canvas(packet, pagesize=letter)
        can.drawString(100, 701, self.cid)
        can.drawString(158, 655, MODULES[self.module_code])
        can.drawString(158, 609, self.module_code)
        can.drawString(105, 563, str(date.today()))

        for q in questions_attempted:
            can.drawString(145, 485-(q)*13.7, "✓")

        can.save()
        packet.seek(0)
        cs_details = PdfFileReader(packet)

        return cs_details


    def add_coversheet(self, input_dir, output_dir, questions_attempted):
        """Add question to coversheet and create output file."""

        cs_details = self.personalise_coversheet(questions_attempted)

        # Files need to be open for the entirety of the merge
        with open(self.template_dir, "rb") as template, \
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


    def by_question(self):
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

        for q in range(1, self.number_of_questions+1):
            try:
                input_dir = f"{self.input_dir}/{q}.pdf"
                output_dir = f"{self.output_dir}/{self.cid}_{self.module_code}_Q{q}.pdf"
                self.add_coversheet(input_dir, output_dir, [q])
                print(f"Question {q} has been processed successfully.")
            except Exception as e:
                print(f"Error in creating output for question {q}.")
                print(e)


    def full_submission(self):
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

        input_dir = f"{self.input_dir}/{self.module_code}.pdf"
        output_dir = f"{self.output_dir}/{self.cid}_{self.module_code}_full_submission.pdf"
        self.add_coversheet(input_dir, output_dir, range(1, self.number_of_questions + 1))

        print("Success! Output file has been placed in Ouput.")

    def clear_directory(self, dir_):
        for file in os.listdir(dir_):
            path = os.path.join(dir_, file)
            try:
                shutil.rmtree(path)
            except OSError:
                os.remove(path)

    def clear_input_directory(self):
        self.clear_directory(self.input_dir)

    def clear_output_directory(self):
        self.clear_directory(self.output_dir)


# Import FPDF class
from fpdf import FPDF

# Create instance of FPDF class
# Letter size paper, use inches as unit of measure
pdf = FPDF(format='letter', unit='in')

# Add new page. Without this you cannot create the document.
pdf.add_page()

# Remember to always put one of these at least once.
pdf.set_font('Times', '', 10.0)

# Effective page width, or just epw
epw = pdf.w - 2 * pdf.l_margin

# Set column width to 1/4 of effective page width to distribute content
# evenly across table and page
col_width = epw / 3

# Since we do not need to draw lines anymore, there is no need to separate
# headers from data matrix.


def print_pdf(data):

    th = pdf.font_size

    pdf.set_font('Times', 'B', 14.0)
    pdf.cell(epw, 0.0, 'Computer Generated Attendance Report', align='C')

    # Here we add more padding by passing 2*th as height
    pdf.set_font('Times', 'B', 12.0)
    pdf.ln(0.5)
    pdf.cell(col_width, 1.5 * th, "Name", border=1)
    pdf.cell(col_width, 1.5 * th, "ID", border=1)
    pdf.cell(col_width, 1.5 * th, "Availability", border=1)

    pdf.set_font('Times', '', 10.0)
    pdf.ln(1.5 * th)
    for row in data:
        for datum in row:
            pdf.cell(col_width, 1.5 * th, str(datum), border=1)

        pdf.ln(1.5 * th)

    pdf.output('attendance.pdf', 'F')


def print_attendance_sheet(available_people, database):
    peopleList = []
    for key in available_people:
        peopleList.append([database[key], key, ""])
        # print(key)

    print_pdf(peopleList)

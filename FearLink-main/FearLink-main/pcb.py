from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

# Create a PDF file
pdf_file = "FearLink_PCB_Layout.pdf"
c = canvas.Canvas(pdf_file, pagesize=A4)

# Set up the page
c.setTitle("FearLink Smartwatch PCB Layout")
c.setFont("Helvetica", 12)

# Draw the PCB outline
c.rect(2*cm, 2*cm, 16*cm, 10*cm)  # PCB boundary

# Draw components
def draw_component(x, y, label):
    c.rect(x, y, 1*cm, 0.5*cm)  # Component outline
    c.drawString(x + 0.2*cm, y + 0.2*cm, label)  # Component label

# Draw connections
def draw_connection(x1, y1, x2, y2):
    c.line(x1, y1, x2, y2)

# Add components
draw_component(3*cm, 8*cm, "MCU")  # MCU
draw_component(6*cm, 8*cm, "Display")  # 1.6-inch Display
draw_component(9*cm, 8*cm, "SIM7600")  # SIM7600 Module
draw_component(12*cm, 8*cm, "GPS")  # GPS Module
draw_component(3*cm, 5*cm, "PPG")  # PPG Sensor
draw_component(6*cm, 5*cm, "GSR")  # GSR Sensor
draw_component(9*cm, 5*cm, "Accel")  # Accelerometer
draw_component(12*cm, 5*cm, "Battery")  # Battery & Power

# Add connections
draw_connection(3.5*cm, 8*cm, 6.5*cm, 8*cm)  # MCU → Display
draw_connection(6.5*cm, 8*cm, 9.5*cm, 8*cm)  # Display → SIM7600
draw_connection(9.5*cm, 8*cm, 12.5*cm, 8*cm)  # SIM7600 → GPS
draw_connection(3.5*cm, 8*cm, 3.5*cm, 5*cm)  # MCU → PPG
draw_connection(6.5*cm, 8*cm, 6.5*cm, 5*cm)  # MCU → GSR
draw_connection(9.5*cm, 8*cm, 9.5*cm, 5*cm)  # MCU → Accel
draw_connection(12.5*cm, 8*cm, 12.5*cm, 5*cm)  # MCU → Battery

# Add labels
c.drawString(2.5*cm, 1.5*cm, "FearLink Smartwatch PCB Layout")
c.drawString(2.5*cm, 1.2*cm, "Components: MCU, Display, SIM7600, GPS, PPG, GSR, Accelerometer, Battery")

# Save the PDF
c.save()

print(f"PCB layout saved as {pdf_file}")
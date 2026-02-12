from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, PageBreak

# File name
pdf_filename = "Investor_Pitch.pdf"

# Styles for formatting
styles = getSampleStyleSheet()
title_style = styles["Title"]
heading_style = styles["Heading2"]
body_style = styles["BodyText"]

# Create a document
doc = SimpleDocTemplate(pdf_filename, pagesize=landscape(letter))

# Content list
content = []

# Add Title Slide
title = Paragraph("<b>Smartwatch for Fear Detection</b>", title_style)
subtitle = Paragraph("<i>AI-Powered Safety & Wellness Tracker</i>", body_style)
content.extend([title, Spacer(1, 0.5 * inch), subtitle, PageBreak()])

# Problem Statement
content.append(Paragraph("<b>🚨 Problem Statement</b>", heading_style))
content.append(Paragraph("Millions of individuals, including children and women, face safety risks daily. "
                         "Traditional smartwatches only track health metrics but fail to detect emotional distress.", body_style))
content.append(PageBreak())

# Our Solution
content.append(Paragraph("<b>💡 Our Innovative Solution</b>", heading_style))
content.append(Paragraph("A cutting-edge smartwatch equipped with AI and biometric sensors that detects fear, "
                         "sends emergency alerts, and provides real-time safety insights.", body_style))
content.append(PageBreak())

# Unique Selling Points (USPs)
content.append(Paragraph("<b>🌟 Unique Selling Points</b>", heading_style))
content.append(Paragraph(
    "<ul>"
    "<li>🚀 AI-powered real-time fear detection</li>"
    "<li>📡 eSIM 4G LTE & WiFi for standalone connectivity</li>"
    "<li>📊 Cloud analytics & emergency notifications</li>"
    "<li>🔄 Machine learning for personalized alerts</li>"
    "<li>🎙 AI Voice Assistant for safety commands</li>"
    "</ul>",
    body_style))
content.append(PageBreak())

# Market Opportunity
content.append(Paragraph("<b>📈 Market Opportunity</b>", heading_style))
content.append(Paragraph("With over 500 million smartwatch users worldwide, integrating AI for safety can revolutionize the industry. "
                         "Targeting schools, government safety initiatives, and personal safety markets.", body_style))
content.append(PageBreak())

# Revenue Model
content.append(Paragraph("<b>💰 Revenue Model</b>", heading_style))
content.append(Paragraph("Direct sales, B2B partnerships with schools and governments, and subscription-based safety features for premium services.", body_style))
content.append(PageBreak())

# Cost & Pricing
content.append(Paragraph("<b>🛠 Cost & Pricing</b>", heading_style))
content.append(Paragraph("Prototype Cost: ₹7L - ₹15L | Unit Manufacturing Cost: ₹12,000 | Selling Price: ₹18,999", body_style))
content.append(PageBreak())

# Investment Ask
content.append(Paragraph("<b>🚀 Investment Ask</b>", heading_style))
content.append(Paragraph("Seeking ₹1 Cr for prototype development, initial manufacturing, and marketing.", body_style))
content.append(PageBreak())

# Next Steps
content.append(Paragraph("<b>🛠 Next Steps</b>", heading_style))
content.append(Paragraph("<ul>"
                         "<li>🎯 Complete prototype within 6 months</li>"
                         "<li>📢 Launch pilot programs with schools & governments</li>"
                         "<li>🚀 Scale production & global partnerships</li>"
                         "</ul>",
                         body_style))
content.append(PageBreak())

# Generate PDF
doc.build(content)

print(f"✅ PDF successfully created: {pdf_filename}")

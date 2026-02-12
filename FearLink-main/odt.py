from odf.opendocument import OpenDocumentText
from odf.style import Style, TextProperties, ParagraphProperties
from odf.text import H, P, Span

# Create a new ODT document
doc = OpenDocumentText()

# Define styles
# Heading style (Bold, 18pt, Dark Blue)
heading_style = Style(name="Heading1", family="paragraph")
heading_style.addElement(TextProperties(attributes={'fontweight': 'bold', 'fontsize': '18pt', 'color': '#00008B'}))
doc.styles.addElement(heading_style)

# Subheading style (Bold, 16pt, various colors)
subheading_style = Style(name="Subheading", family="paragraph")
subheading_style.addElement(TextProperties(attributes={'fontweight': 'bold', 'fontsize': '16pt'}))
doc.styles.addElement(subheading_style)

# Body text style
body_style = Style(name="Body", family="paragraph")
body_style.addElement(TextProperties(attributes={'fontsize': '12pt'}))
doc.styles.addElement(body_style)

# Bold text style
bold_style = Style(name="Bold", family="text")
bold_style.addElement(TextProperties(attributes={'fontweight': 'bold'}))
doc.styles.addElement(bold_style)

# Function to add bold text within a paragraph
def add_bold_text(paragraph, text):
    bold_span = Span(stylename=bold_style, text=text)
    paragraph.addElement(bold_span)

# Add content to the document
# Title
title = H(outlinelevel=1, stylename=heading_style, text="[Fear Detection Smartwatch – Business Proposal]")
doc.text.addElement(title)
subtitle = P(stylename=body_style, text="A Next-Gen Safety & Security Innovation")
doc.text.addElement(subtitle)
date = P(stylename=body_style, text="Date: March 16, 2025")
doc.text.addElement(date)
doc.text.addElement(P(text="[Insert Logo or Smartwatch Icon Here]"))

# Executive Summary
doc.text.addElement(H(outlinelevel=2, stylename=subheading_style, text="[Executive Summary]"))
p = P(stylename=body_style)
p.addText("We’re revolutionizing safety with the ")
add_bold_text(p, "world’s first AI-powered fear detection smartwatch")
p.addText(".")
doc.text.addElement(p)
for point in [
    "Target Audience: Students, women, elderly.",
    "Key Features: Real-time fear tracking, instant alerts, phone-free operation.",
    "Market Edge: No direct competitors in fear detection.",
    "Potential: Massive demand from schools, parents, and governments."
]:
    doc.text.addElement(P(stylename=body_style, text=point))
doc.text.addElement(P(text="[Graphic Placeholder: Smartwatch with glowing alert symbol on right | 50% page width]"))

# Section 1: The Problem
doc.text.addElement(H(outlinelevel=2, stylename=subheading_style, text="[1. The Problem – Why?]"))
doc.text.addElement(P(stylename=body_style, text="The Safety Crisis"))
p = P(stylename=body_style)
p.addText("Every day, millions face danger but lack instant help.")
doc.text.addElement(p)
for point in [
    "Current smartwatches track health, not fear or distress.",
    "Schools and governments need innovative safety solutions."
]:
    p = P(stylename=body_style)
    add_bold_text(p, point.split(" ")[0])  # Bold first word for emphasis
    p.addText(" " + " ".join(point.split(" ")[1:]))
    doc.text.addElement(p)
doc.text.addElement(P(text="[Graphic Placeholder: Silhouette of a person in distress | Bottom left, 30% page width]"))
doc.text.addElement(P(text="[Stat Callout: “Millions at Risk Daily” in a red circle | Top right]"))

# Section 2: The Solution
doc.text.addElement(H(outlinelevel=2, stylename=subheading_style, text="[2. The Solution – How?]"))
doc.text.addElement(P(stylename=body_style, text="Our Innovation"))
p = P(stylename=body_style)
p.addText("An ")
add_bold_text(p, "AI-powered smartwatch")
p.addText(" that:")
doc.text.addElement(p)
for point in [
    "Tracks fear via heart rate, sweating, motion, voice, and expressions.",
    "Sends instant alerts to guardians or authorities.",
    "Operates independently with eSIM + 4G LTE + WiFi.",
    "Improves accuracy with cloud-based AI."
]:
    doc.text.addElement(P(stylename=body_style, text=point))
doc.text.addElement(P(text="[Graphic Placeholder: Flowchart – Smartwatch → Sensors → Cloud → Alerts | Center, 60% page width]"))

# Section 3: Business Model
doc.text.addElement(H(outlinelevel=2, stylename=subheading_style, text="[3. Business Model – How We Profit]"))
doc.text.addElement(P(stylename=body_style, text="Revenue Streams"))
for point in [
    "Direct Sales: ₹18,999/unit (₹7,000 profit).",
    "Subscriptions: ₹1,500/year for AI insights.",
    "Partnerships: Bulk orders from schools/governments.",
    "Licensing: AI tech to other brands."
]:
    doc.text.addElement(P(stylename=body_style, text=point))
doc.text.addElement(P(text="[Graphic Placeholder: Pie chart showing revenue split | Right, 40% page width]"))

# Section 4: Market Potential
doc.text.addElement(H(outlinelevel=2, stylename=subheading_style, text="[4. Market Potential – Why Now?]"))
doc.text.addElement(P(stylename=body_style, text="Huge Demand"))
for point in [
    "India: 250M+ students, 500M+ women.",
    "Global: US, UK, UAE, Europe.",
    "Industry: ₹10,000 Cr women’s safety tech (30% CAGR).",
    "0.1% Market Capture = ₹9,500 Cr revenue."
]:
    doc.text.addElement(P(stylename=body_style, text=point))
doc.text.addElement(P(text="[Graphic Placeholder: Map with highlighted regions | Bottom, 50% page width]"))
doc.text.addElement(P(text="[Stat Callout: “85% of parents worry about safety” in a blue bubble | Top right]"))

# Section 5: Prototype Development
doc.text.addElement(H(outlinelevel=2, stylename=subheading_style, text="[5. Prototype Development – When?]"))
doc.text.addElement(P(stylename=body_style, text="Timeline & Cost"))
doc.text.addElement(P(stylename=body_style, text="Cost: ₹7L – ₹15L"))
for point in [
    "Phase 1 (Months 1-2): R&D, AI modeling.",
    "Phase 2 (Months 3-4): Hardware integration.",
    "Phase 3 (Months 5-6): Testing.",
    "Phase 4 (Months 7-8): Production."
]:
    doc.text.addElement(P(stylename=body_style, text=point))
doc.text.addElement(P(text="[Graphic Placeholder: Horizontal timeline with milestones | Center, 70% page width]"))

# Section 6: Funding Strategy
doc.text.addElement(H(outlinelevel=2, stylename=subheading_style, text="[6. Funding Strategy]"))
doc.text.addElement(P(stylename=body_style, text="How We Raise Capital"))
for point in [
    "Step 1: ₹10L MSME loan (prototype).",
    "Step 2: Government/school bulk orders.",
    "Step 3: ₹5Cr – ₹10Cr from investors (post-MVP)."
]:
    doc.text.addElement(P(stylename=body_style, text=point))
doc.text.addElement(P(text="[Graphic Placeholder: Flowchart – Loan → Orders → Investors | Right, 40% page width]"))

# Section 7: Go-To-Market Strategy
doc.text.addElement(H(outlinelevel=2, stylename=subheading_style, text="[7. Go-To-Market Strategy]"))
doc.text.addElement(P(stylename=body_style, text="How We Sell"))
for point in [
    "Institutional: Schools, safety orgs.",
    "B2C: Amazon, Flipkart, website.",
    "Marketing: Ads, influencers, media buzz."
]:
    doc.text.addElement(P(stylename=body_style, text=point))
doc.text.addElement(P(text="[Graphic Placeholder: Collage of a school, shopping cart, megaphone | Bottom, 60% page width]"))

# Section 8: Financial Forecast
doc.text.addElement(H(outlinelevel=2, stylename=subheading_style, text="[8. Financial Forecast]"))
doc.text.addElement(P(stylename=body_style, text="Revenue & ROI"))
for point in [
    "Year 1: 10,000 units = ₹189 Cr.",
    "Year 2: 25,000 units = ₹475 Cr.",
    "Break-even: 18 months (5,000 units).",
    "Year 2 Profit: ₹50 Cr+."
]:
    doc.text.addElement(P(stylename=body_style, text=point))
doc.text.addElement(P(text="[Graphic Placeholder: Line graph of revenue growth | Center, 50% page width]"))

# Section 9: Team & Costs
doc.text.addElement(H(outlinelevel=2, stylename=subheading_style, text="[9. Team & Costs]"))
doc.text.addElement(P(stylename=body_style, text="Lean & Efficient"))
for point in [
    "Team: AI, hardware, marketing.",
    "Monthly Cost: ₹3L.",
    "Example: AI Engineers (2) @ ₹50,000 each."
]:
    doc.text.addElement(P(stylename=body_style, text=point))
doc.text.addElement(P(text="[Graphic Placeholder: Simple org chart with roles | Right, 40% page width]"))

# Section 10: Why Invest?
doc.text.addElement(H(outlinelevel=2, stylename=subheading_style, text="[10. Why Invest?]"))
doc.text.addElement(P(stylename=body_style, text="The Opportunity"))
for point in [
    "World’s first fear detection smartwatch.",
    "No competition, massive need.",
    "High profit: ₹7,000/unit.",
    "Globally scalable.",
    "A safety revolution!"
]:
    doc.text.addElement(P(stylename=body_style, text=point))
doc.text.addElement(P(text="[Graphic Placeholder: Smartwatch with glowing halo | Center, 50% page width]"))

# Call to Action
doc.text.addElement(H(outlinelevel=2, stylename=subheading_style, text="[Call to Action]"))
doc.text.addElement(P(stylename=body_style, text="“Let’s build the future of safety together!”"))
doc.text.addElement(P(stylename=body_style, text="Contact: [Your email/phone]"))
doc.text.addElement(P(stylename=body_style, text="Next Steps: Fund the prototype → Dominate the market."))
doc.text.addElement(P(text="[Graphic Placeholder: Rocket or handshake icon | Bottom right, 30% page width]"))

# Save the document
doc.save("Fear_Detection_Smartwatch_Proposal.odt")
print("ODT file 'Fear_Detection_Smartwatch_Proposal.odt' has been created!")
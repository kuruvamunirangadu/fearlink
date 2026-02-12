from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.xmlchemy import OxmlElement

# Create a new presentation
prs = Presentation()

# Helper function to add a slide with a title and content
def add_slide_with_title(layout, title_text, content_lines, title_color=RGBColor(0, 0, 139)):
    slide = prs.slides.add_slide(layout)
    title = slide.shapes.title
    title.text = title_text
    title.text_frame.paragraphs[0].font.size = Pt(18)
    title.text_frame.paragraphs[0].font.bold = True
    title.text_frame.paragraphs[0].font.color.rgb = title_color
    
    body_shape = slide.shapes.placeholders[1]  # Assuming layout has a content placeholder
    tf = body_shape.text_frame
    tf.clear()  # Remove default text
    
    for line in content_lines:
        p = tf.add_paragraph()
        p.text = line
        p.font.size = Pt(12)
        p.font.color.rgb = RGBColor(0, 0, 0)
        if "<b>" in line:  # Handle bold text
            p.text = line.replace("<b>", "").replace("</b>", "")
            p.font.bold = True
    return slide

# Slide 1: Title Slide
title_slide_layout = prs.slide_layouts[0]  # Title Slide layout
slide = prs.slides.add_slide(title_slide_layout)
title = slide.shapes.title
title.text = "Fear Detection Smartwatch – Business Proposal"
title.text_frame.paragraphs[0].font.size = Pt(24)
title.text_frame.paragraphs[0].font.bold = True
title.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 0, 139)  # Dark Blue
subtitle = slide.placeholders[1]
subtitle.text = "A Next-Gen Safety & Security Innovation\nDate: March 16, 2025\n[Insert Logo or Smartwatch Icon Here]"
subtitle.text_frame.paragraphs[0].font.size = Pt(14)

# Slide 2: Executive Summary
content_layout = prs.slide_layouts[1]  # Title and Content layout
add_slide_with_title(content_layout, "Executive Summary", [
    "We’re revolutionizing safety with the <b>world’s first AI-powered fear detection smartwatch</b>.",
    "Target Audience: Students, women, elderly.",
    "Key Features: Real-time fear tracking, instant alerts, phone-free operation.",
    "Market Edge: No direct competitors in fear detection.",
    "Potential: Massive demand from schools, parents, and governments.",
    "[Graphic: Smartwatch with glowing alert symbol - Add image 'smartwatch.png']"
], RGBColor(0, 0, 139))

# Slide 3: The Problem
add_slide_with_title(content_layout, "1. The Problem – Why?", [
    "The Safety Crisis",
    "Every day, millions face danger but lack instant help.",
    "Current smartwatches track health, not <b>fear or distress</b>.",
    "Schools and governments need innovative safety solutions.",
    "[Graphic: Silhouette of a person in distress - Add image 'silhouette.png']",
    "[Stat Callout: “Millions at Risk Daily” in a red circle]"
], RGBColor(255, 0, 0))  # Red

# Slide 4: The Solution
add_slide_with_title(content_layout, "2. The Solution – How?", [
    "Our Innovation",
    "An <b>AI-powered smartwatch</b> that:",
    "Tracks fear via heart rate, sweating, motion, voice, and expressions.",
    "Sends <b>instant alerts</b> to guardians or authorities.",
    "Operates independently with <b>eSIM + 4G LTE + WiFi</b>.",
    "Improves accuracy with <b>cloud-based AI</b>.",
    "[Graphic: Flowchart – Smartwatch → Sensors → Cloud → Alerts]"
], RGBColor(0, 128, 0))  # Green

# Slide 5: Business Model
add_slide_with_title(content_layout, "3. Business Model – How We Profit", [
    "Revenue Streams",
    "Direct Sales: ₹18,999/unit (₹7,000 profit).",
    "Subscriptions: ₹1,500/year for AI insights.",
    "Partnerships: Bulk orders from schools/governments.",
    "Licensing: AI tech to other brands.",
    "[Graphic: Pie chart showing revenue split]"
], RGBColor(255, 215, 0))  # Gold

# Slide 6: Market Potential
add_slide_with_title(content_layout, "4. Market Potential – Why Now?", [
    "Huge Demand",
    "India: 250M+ students, 500M+ women.",
    "Global: US, UK, UAE, Europe.",
    "Industry: ₹10,000 Cr women’s safety tech (30% CAGR).",
    "0.1% Market Capture = ₹9,500 Cr revenue.",
    "[Graphic: Map with highlighted regions - Add image 'map.png']",
    "[Stat Callout: “85% of parents worry about safety” in a blue bubble]"
], RGBColor(0, 0, 139))  # Blue

# Slide 7: Prototype Development
slide = add_slide_with_title(content_layout, "5. Prototype Development – When?", [
    "Timeline & Cost",
    "Cost: ₹7L – ₹15L",
    "Phase 1 (Months 1-2): R&D, AI modeling.",
    "Phase 2 (Months 3-4): Hardware integration.",
    "Phase 3 (Months 5-6): Testing.",
    "Phase 4 (Months 7-8): Production.",
    "[Graphic: Horizontal timeline with milestones]"
], RGBColor(128, 0, 128))  # Purple
# Add a simple timeline shape
left, top, width, height = Inches(1), Inches(4), Inches(5), Inches(0.2)
timeline = slide.shapes.add_shape(1, left, top, width, height)  # Rectangle
timeline.fill.solid()
timeline.fill.fore_color.rgb = RGBColor(128, 0, 128)

# Slide 8: Funding Strategy
add_slide_with_title(content_layout, "6. Funding Strategy", [
    "How We Raise Capital",
    "Step 1: ₹10L MSME loan (prototype).",
    "Step 2: Government/school bulk orders.",
    "Step 3: ₹5Cr – ₹10Cr from investors (post-MVP).",
    "[Graphic: Flowchart – Loan → Orders → Investors]"
], RGBColor(0, 128, 128))  # Teal

# Slide 9: Go-To-Market Strategy
add_slide_with_title(content_layout, "7. Go-To-Market Strategy", [
    "How We Sell",
    "Institutional: Schools, safety orgs.",
    "B2C: Amazon, Flipkart, website.",
    "Marketing: Ads, influencers, media buzz.",
    "[Graphic: Collage of a school, shopping cart, megaphone]"
], RGBColor(255, 165, 0))  # Orange

# Slide 10: Financial Forecast
add_slide_with_title(content_layout, "8. Financial Forecast", [
    "Revenue & ROI",
    "Year 1: 10,000 units = ₹189 Cr.",
    "Year 2: 25,000 units = ₹475 Cr.",
    "Break-even: 18 months (5,000 units).",
    "Year 2 Profit: ₹50 Cr+.",
    "[Graphic: Line graph of revenue growth]"
], RGBColor(255, 215, 0))  # Gold

# Slide 11: Team & Costs
add_slide_with_title(content_layout, "9. Team & Costs", [
    "Lean & Efficient",
    "Team: AI, hardware, marketing.",
    "Monthly Cost: ₹3L.",
    "Example: AI Engineers (2) @ ₹50,000 each.",
    "[Graphic: Simple org chart with roles]"
], RGBColor(128, 128, 128))  # Grey

# Slide 12: Why Invest?
add_slide_with_title(content_layout, "10. Why Invest?", [
    "The Opportunity",
    "World’s first fear detection smartwatch.",
    "No competition, massive need.",
    "High profit: ₹7,000/unit.",
    "Globally scalable.",
    "<b>A safety revolution!</b>",
    "[Graphic: Smartwatch with glowing halo - Add image 'smartwatch.png']"
], RGBColor(0, 0, 139))  # Dark Blue

# Slide 13: Call to Action
add_slide_with_title(content_layout, "Call to Action", [
    "“Let’s build the future of safety together!”",
    "Contact: [Your email/phone]",
    "Next Steps: Fund the prototype → Dominate the market.",
    "[Graphic: Rocket or handshake icon - Add image 'rocket.png']"
], RGBColor(0, 0, 0))  # Black

# Save the presentation
prs.save("Fear_Detection_Smartwatch_Proposal.pptx")
print("PPTX file 'Fear_Detection_Smartwatch_Proposal.pptx' has been created!")
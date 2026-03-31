import io
import re
from docx import Document
import PyPDF2
def check_sections(text: str, required_sections: list) -> dict:
    """
    Check if required CV sections are present in the parsed text.
    Returns dict with sections found/missing lists.
    """
    text_lower = text.lower()
    found = []
    missing = []
    for section in required_sections:
        # Use simple case-insensitive search with word boundary for accuracy
        if re.search(r"\b" + re.escape(section.lower()) + r"\b", text_lower):
            found.append(section)
        else:
            missing.append(section)
    return {"found_sections": found, "missing_sections": missing}
def parse_resume(file_content: bytes, filename: str) -> dict:
    """
    Parses the resume content based on file extension.
    Supports .pdf, .docx, and plain text files.
    Checks for required CV sections.
    Returns extracted info and summary.
    """
    text = ""
    lower_fname = filename.lower()
    try:
        if lower_fname.endswith(".docx"):
            doc = Document(io.BytesIO(file_content))
            text = "\n".join([para.text for para in doc.paragraphs])
        elif lower_fname.endswith(".pdf"):
            reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        elif lower_fname.endswith(".txt"):
            text = file_content.decode("utf-8")
        else:
            return {
                "filename": filename,
                "message": "Unsupported file type. Please upload a .pdf, .docx, or .txt file."
            }
        word_count = len(text.split())
        preview = text[:500]
        # Customize list based on CV expectations
        required_sections = [
            "Contact Information",
            "Summary",
            "Work Experience",
            "Education",
            "Skills",
            "Certifications",
            "Projects"
        ]

        sections_check = check_sections(text, required_sections)

        # Create user-friendly analysis summary
        analysis_summary = []
        analysis_summary.append(f"📄 Resume Analysis for: {filename}")
        analysis_summary.append(f"📊 Total words: {word_count}")
        analysis_summary.append("")

        if sections_check["found_sections"]:
            analysis_summary.append("✅ SECTIONS FOUND:")
            for section in sections_check["found_sections"]:
                analysis_summary.append(f"   • {section}")
            analysis_summary.append("")

        if sections_check["missing_sections"]:
            analysis_summary.append("❌ MISSING SECTIONS (Consider Adding):")
            for section in sections_check["missing_sections"]:
                analysis_summary.append(f"   • {section}")
            analysis_summary.append("")

        # Add recommendations and specific corrections
        analysis_summary.append("💡 RECOMMENDATIONS & CORRECTIONS:")
        suggestions = []

        if len(sections_check["missing_sections"]) == 0:
            suggestions.append("✅ Excellent! Your resume contains all key sections.")
        elif len(sections_check["missing_sections"]) <= 2:
            suggestions.append("📝 Good foundation! Consider adding the missing sections above.")
        else:
            suggestions.append("📋 Consider adding more key sections to strengthen your resume.")

        if word_count < 200:
            suggestions.append("📏 Your resume might benefit from more detailed descriptions.")
            suggestions.append("   → Try expanding each role with 2-3 bullet points of achievements")
            suggestions.append("   → Add quantifiable results (e.g., 'Increased sales by 25%')")
        elif word_count > 800:
            suggestions.append("✂️ Consider condensing content for better readability.")
            suggestions.append("   → Aim for 1-2 pages maximum")
            suggestions.append("   → Remove older or less relevant experiences")
        else:
            suggestions.append("📏 Word count looks good for a professional resume.")

        # Add specific content suggestions based on missing sections
        if "Contact Information" in sections_check["missing_sections"]:
            suggestions.append("📞 Missing Contact Info - Add: Phone, Email, LinkedIn, Location")

        if "Summary" in sections_check["missing_sections"]:
            suggestions.append("📝 Add Professional Summary - 2-3 sentences highlighting your key strengths")

        if "Work Experience" in sections_check["missing_sections"]:
            suggestions.append("💼 Missing Work Experience - Include job titles, companies, dates, and achievements")

        if "Skills" in sections_check["missing_sections"]:
            suggestions.append("🛠️ Add Skills Section - List technical and soft skills relevant to your target role")

        if "Education" in sections_check["missing_sections"]:
            suggestions.append("🎓 Include Education - Add degrees, institutions, and graduation years")

        # Format improvement suggestions
        text_lower = text.lower()
        if not re.search(r'\b(achieved|increased|improved|managed|led|developed|created)\b', text_lower):
            suggestions.append("💪 Use stronger action verbs (achieved, increased, improved, managed, led)")

        if not re.search(r'\d+%|\$\d+|\d+,\d+|\d+ years?', text):
            suggestions.append("📊 Add quantifiable achievements with numbers, percentages, or dollar amounts")

        if len(text.split('\n')) < 5:
            suggestions.append("📋 Consider better formatting with clear sections and bullet points")

        for suggestion in suggestions:
            analysis_summary.append(f"   • {suggestion}")

        analysis_summary.append("")
        analysis_summary.append("🎯 NEXT STEPS:")
        if sections_check["missing_sections"]:
            analysis_summary.append(f"   1. Add the {len(sections_check['missing_sections'])} missing section(s) listed above")
        analysis_summary.append("   2. Review each section for completeness and relevance")
        analysis_summary.append("   3. Proofread for grammar and spelling errors")
        analysis_summary.append("   4. Ensure consistent formatting throughout")

        user_friendly_output = "\n".join(analysis_summary)

        return {
            "filename": filename,
            "word_count": word_count,
            "preview": preview,
            "sections_found": sections_check["found_sections"],
            "sections_missing": sections_check["missing_sections"],
            "analysis": user_friendly_output,
            "suggestions_count": len(suggestions),
            "has_corrections": len(sections_check["missing_sections"]) > 0 or word_count < 200 or word_count > 800,
            "message": "Resume analysis completed successfully!"
        }

    except Exception as e:
        return {
            "filename": filename,
            "message": f"Error parsing resume: {str(e)}"
        }

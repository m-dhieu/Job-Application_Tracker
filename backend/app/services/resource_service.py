def fetch_resources(skill: str):
    """
    Returns static resources for demonstration.
    Replace with real API calls if needed.
    """
    resources = {
        "python": [
            {"title": "Python Basics - Khan Academy", "url": "https://www.khanacademy.org/computing/computer-programming"},
            {"title": "Learn Python - FreeCodeCamp", "url": "https://www.freecodecamp.org/learn/scientific-computing-with-python/"},
        ],
        "data science": [
            {"title": "Intro to Data Science - Khan Academy", "url": "https://www.khanacademy.org/math/statistics-probability"},
            {"title": "Data Science Tutorials - YouTube", "url": "https://www.youtube.com/playlist?list=PLZyvi_9gamL-EE3zQJbU5NsvLa_EFy3nS"},
        ]
    }
    return resources.get(skill.lower(), [{"title": "No resources found for this skill", "url": ""}])

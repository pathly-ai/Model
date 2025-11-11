import pandas as pd
import random


CAREER_TEMPLATES = {
    'Software Developer': {
        'edu': ['B.Tech'], 'stream': ['Computer Science'], 'cgpa': (8.0, 9.8),
        'tech_skills': ['Python', 'Java', 'SQL', 'Git', 'JavaScript'], 'soft_skills': ['Problem-Solving', 'Teamwork'],
        'personality': ['Introvert', 'Ambivert'], 'salary': ['8-12 LPA', '12+ LPA'], 'certifications': ['Coursera - Python for Everybody', 'No Certification'],
        'work_env': ['I like a mix of both', 'I prefer working alone'], 'learning': ['Kinesthetic', 'Visual'], 'relocating': ['Yes', 'Maybe'], 'higher_studies': ['No'],
        'ambiguous_swap': 'Data Scientist'
    },
    'Data Scientist': {
        'edu': ['M.Tech', 'B.Tech'], 'stream': ['Computer Science', 'Data Science'], 'cgpa': (8.5, 9.9),
        'tech_skills': ['Python', 'R', 'SQL', 'TensorFlow', 'Scikit-learn'], 'soft_skills': ['Critical Thinking', 'Problem-Solving'],
        'personality': ['Ambivert', 'Introvert'], 'salary': ['12+ LPA', '8-12 LPA'], 'certifications': ['Google Data Analytics', 'IBM Data Science'],
        'work_env': ['I prefer working alone'], 'learning': ['Read/Write', 'Visual'], 'relocating': ['Yes'], 'higher_studies': ['Yes', 'No'],
        'ambiguous_swap': 'AI Specialist'
    },
    'AI Specialist': {
        'edu': ['M.Tech'], 'stream': ['AI & ML', 'Computer Science'], 'cgpa': (8.8, 10.0),
        'tech_skills': ['Python', 'PyTorch', 'TensorFlow', 'NLP', 'Computer Vision'], 'soft_skills': ['Research', 'Critical Thinking'],
        'personality': ['Introvert'], 'salary': ['12+ LPA'], 'certifications': ['Deep Learning Specialization', 'TensorFlow Developer'],
        'work_env': ['I prefer working alone'], 'learning': ['Read/Write'], 'relocating': ['Yes'], 'higher_studies': ['Yes'],
        'ambiguous_swap': 'Data Scientist'
    },
    'Financial Analyst': {
        'edu': ['B.Com', 'MBA'], 'stream': ['Finance', 'Commerce'], 'cgpa': (7.5, 9.2),
        'tech_skills': ['MS Excel', 'Financial Modeling', 'SQL', 'Tableau'], 'soft_skills': ['Analytical Skills', 'Attention to Detail'],
        'personality': ['Ambivert', 'Extrovert'], 'salary': ['4-8 LPA', '8-12 LPA'], 'certifications': ['CFA', 'No Certification'],
        'work_env': ['I prefer working alone'], 'learning': ['Read/Write', 'Visual'], 'relocating': ['No', 'Maybe'], 'higher_studies': ['Yes', 'No'],
        'ambiguous_swap': 'Business Analyst'
    },
    'Marketing Manager': {
        'edu': ['BBA', 'MBA'], 'stream': ['Marketing', 'Business Administration'], 'cgpa': (7.0, 9.0),
        'tech_skills': ['Digital Marketing', 'SEO', 'Google Analytics', 'Social Media Management'], 'soft_skills': ['Creativity', 'Leadership', 'Communication'],
        'personality': ['Extrovert'], 'salary': ['8-12 LPA', '12+ LPA'], 'certifications': ['Google Digital Marketing', 'HubSpot Content Marketing'],
        'work_env': ['I prefer working in a team'], 'learning': ['Auditory', 'Visual'], 'relocating': ['Yes', 'Maybe'], 'higher_studies': ['No'],
        'ambiguous_swap': 'Social Media Manager'
    },
    'Graphic Designer': {
        'edu': ['B.Des', 'B.A.'], 'stream': ['Fine Arts', 'Graphic Design'], 'cgpa': (6.5, 8.9),
        'tech_skills': ['Adobe Photoshop', 'Adobe Illustrator', 'Figma'], 'soft_skills': ['Creativity', 'Attention to Detail'],
        'personality': ['Introvert', 'Ambivert'], 'salary': ['4-8 LPA', 'Less than 4 LPA'], 'certifications': ['Adobe Certified Expert (ACE)', 'No Certification'],
        'work_env': ['I prefer working alone', 'I like a mix of both'], 'learning': ['Visual', 'Kinesthetic'], 'relocating': ['No'], 'higher_studies': ['No', 'Yes'],
        'ambiguous_swap': 'UI/UX Designer'
    },
    'Mechanical Engineer': {
        'edu': ['B.Tech', 'Diploma'], 'stream': ['Mechanical Engineering'], 'cgpa': (7.0, 9.0),
        'tech_skills': ['AutoCAD', 'SolidWorks', 'MATLAB'], 'soft_skills': ['Problem-Solving', 'Teamwork'],
        'personality': ['Ambivert'], 'salary': ['4-8 LPA', '8-12 LPA'], 'certifications': ['Certified SOLIDWORKS Professional', 'No Certification'],
        'work_env': ['I prefer working in a team'], 'learning': ['Kinesthetic'], 'relocating': ['Yes', 'Maybe'], 'higher_studies': ['Yes'],
        'ambiguous_swap': 'Civil Engineer'
    },
     'UI/UX Designer': {
        'edu': ['B.Des', 'B.Tech'], 'stream': ['Graphic Design', 'Human-Computer Interaction'], 'cgpa': (7.5, 9.3),
        'tech_skills': ['Figma', 'Sketch', 'Adobe XD', 'User Research'], 'soft_skills': ['Empathy', 'Problem-Solving', 'Creativity'],
        'personality': ['Ambivert'], 'salary': ['8-12 LPA', '12+ LPA'], 'certifications': ['Nielsen Norman Group UX Certification', 'No Certification'],
        'work_env': ['I like a mix of both'], 'learning': ['Visual', 'Kinesthetic'], 'relocating': ['Yes', 'No'], 'higher_studies': ['No'],
        'ambiguous_swap': 'Graphic Designer'
    }
}


def generate_realistic_data(num_rows=5000, noise_level=0.18):
    """Generates a rich dataset with controlled ambiguity to target 80-95% accuracy."""
    data_list = []
    career_paths = list(CAREER_TEMPLATES.keys())

    for i in range(num_rows):
        career = random.choice(career_paths)
        template = CAREER_TEMPLATES[career]
        
        # This is the key part: for 18% of the data, we swap the label to a similar but different career.
        if random.random() < noise_level:
            final_career_label = template['ambiguous_swap']
        else:
            final_career_label = career

        student_data = {
            'Current Education Level': random.choice(template['edu']),
            'Stream / Specialization': random.choice(template['stream']),
            'Latest Grade / CGPA': round(random.uniform(template['cgpa'][0], template['cgpa'][1]), 2),
            'Technical / Hard Skills': ', '.join(random.sample(template['tech_skills'], k=random.randint(2, len(template['tech_skills'])))),
            'Soft Skills': ', '.join(random.sample(template['soft_skills'], k=min(2, len(template['soft_skills'])))),
            'Personality Type': random.choice(template['personality']),
            'Salary Expectation (Annual, in INR)': random.choice(template['salary']),
            'Certifications Obtained': random.choice(template['certifications']),
            'Preferred Work Environment': random.choice(template['work_env']),
            'Learning Style': random.choice(template['learning']),
            'Open to Relocating': random.choice(template['relocating']),
            'Willingness to Pursue Higher Studies': random.choice(template['higher_studies']),
            'Recommended Career Path': final_career_label
        }
        data_list.append(student_data)
        
    return pd.DataFrame(data_list)


if __name__ == "__main__":
    final_df = generate_realistic_data(5000)
    
    file_name = 'final_project_dataset.csv'
    final_df.to_csv(file_name, index=False, encoding='utf-8')
    
    print(f"Successfully generated {len(final_df)} rows of data.")
    print(f"The data has {len(final_df.columns)} columns.")
    print(f"Saved to '{file_name}'")
    
    print("\nHere's a preview of your new data:")
    print(final_df.head())
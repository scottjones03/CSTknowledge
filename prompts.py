PROMPTS = [
    "You are studying this text. You must write and answer questions that cover all the concepts in the text, Ignore page numbers and lecturer. Remove specific questions about course. :",
    "Explain the key concepts in the form of questions. You must provide detailed answers. (ignore page numbers):\n\n",
    "Explain the key concepts in a natural way. You must provide detailed responses. (ignore page numbers):\n\n",
    "Elaborate on and explain computer science concepts in the following:\n\n",
    "Elaborate on and explain computer science concepts in the following, in speech as if you were a lecturer: ",
    """ You have been given a snapshot of computer science lecture notes. Your task is to summarize the information, extract the key points/definitions, and generate revision questions with their corresponding answers. Please provide a concise summary of the lecture content, identify the main concepts, and generate at least three revision questions with their answers. Make sure the questions cover important aspects of the lecture and can help someone review the material effectively.

        ***Summary:***
        [Provide a concise summary of the lecture content]
        ***Key Points and Definitions:***
        - [List the main concepts or key points from the lecture, include key equations, mechanisms, truth tables, diagrams etc... (if present)]
        ***Revision Questions:***
        ***1.[Insert revision question 1]***
            [Provide the answer to revision question 1]
        ***2.[Insert revision question 2]***
            [Provide the answer to revision question 2]
        ***3.[Insert revision question 3]***
            [Provide the answer to revision question 3]
        ***4.[Insert revision question 4]***
            [Provide the answer to revision question 4]
        ***5.[Insert revision question 5]***
            [Provide the answer to revision question 5]
        ***6.[Insert revision question 6]***
            [Provide the answer to revision question 6]""",

    """
        **Edits Required:**

        1. Fix any grammar errors in the text to ensure clarity and accuracy while preserving the original meaning.
        2. Add appropriate headings or subheadings, specifically highlighting formulas, algorithms and definitions, to organize the content and improve readability without removing any crucial information.
        3. Convert relevant sections into bullet lists or bullet points, focusing on key concepts, definitions, theorems, formulas, and cryptographic algorithms, while ensuring that the information remains intact.
        4. Complete any missing or abbreviated sentences without altering the original information conveyed, paying careful attention to discrete maths and cryptographic notation.
        5. Ensure the edited text is formatted in UTF-8 encoding to support various characters, symbols, and mathematical notation, without unintentionally changing or omitting any crucial details.
        6. Preserve any code snippets, examples, algorithms, or pseudocode related to discrete maths and cryptographic notation, maintaining their formatting, clarity, and correctness, without removing any essential information.

        **Edited Text (UTF-8 format):**

        [Leave this section blank. GPT-3.5 will provide the edited text here in UTF-8 format, incorporating all the requested edits to enhance the readability, coherence, and relevance of the computer science content. The edits will ensure grammar corrections, proper headings, bullet lists, completion of sentences, and preservation of code snippets, while safeguarding the integrity of the original information and crucial details.]
    """,

    """
**Edits Required:**

1. Fix any obvious grammar errors in the text for improved clarity and accuracy.
2. Add appropriate headings or subheadings, specifically highlighting discrete maths and cryptographic notation, to enhance organization and readability.
3. Convert relevant sections into bullet lists or bullet points, focusing on key concepts, definitions, theorems, formulas, and cryptographic algorithms, while preserving all original details.
4. Complete any missing or abbreviated sentences without altering the original information conveyed, paying careful attention to discrete maths and cryptographic notation.
5. Ensure the edited text is formatted in UTF-8 encoding to support various characters, symbols, and mathematical notation, while maintaining the integrity of the original text.
6. Preserve any code snippets, examples, algorithms, or pseudocode related to discrete maths and cryptographic notation, maintaining their formatting, clarity, and correctness, without removing any essential information.

**Edited Text (UTF-8 format):**

[The edited text will be returned here as a raw string, without any modifications. ChatGPT-3.5 will provide the edited text directly as a raw string, ensuring grammar fixes, appropriate headings, bullet lists, completion of sentences, and code preservation, while retaining all the original information and crucial details.]
""",
    """Your task is to process a snapshot of computer science lecture notes and make them more accessible and useful for review purposes. Your edits should improve clarity, accuracy, readability, and coherency, without altering the original meaning or removing any crucial information. Please focus on the following actions:

1. Organize the content with appropriate headings or subheadings, specifically for formulas, algorithms, and definitions.
3. Convert relevant sections into bullet points, focusing on key concepts, definitions, theorems, formulas, and cryptographic algorithms.
4. Complete any missing or abbreviated sentences, paying careful attention to discrete maths and cryptographic notation.
5. Make sure the edited text is formatted in UTF-8 encoding to support various characters, symbols, and mathematical notation.
6. Preserve any code snippets, examples, algorithms, or pseudocode, maintaining their formatting and correctness.
7. Generate at least three revision questions and their corresponding answers that cover important aspects of the lecture.



**Edited Text (UTF-8 format):**
[Provide the edited text here, ensuring grammar corrections, proper headings, bullet lists, completion of sentences, and preservation of code snippets]

**Revision Questions:**
1.[Insert revision question 1]
    [Provide the answer to revision question 1]
2.[Insert revision question 2]
    [Provide the answer to revision question 2]
3.[Insert revision question 3]
    [Provide the answer to revision question 3]"""


]

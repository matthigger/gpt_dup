# Chat GPT Math Problem Duplicator

Duplicates and refreshes a given math problem via chatGPT, updating numbers and solutions as needed. Results will vary, but this tool has been successful for many simple math problems from CS1800 given a well formated latex template.

For example, [2s_comp_overflow00.tex](/example/2s_comp_overflow00.tex) can be used via:

    python -m gpt_dup 2s_comp_overflow00.tex

to generate [2s_comp_overflow00.tex](/example/2s_comp_overflow01.tex)

# Install

    pip install git+https://github.com/matthigger/gpt_dup

# Account Setup

You'll need to sign up for openai's API service (min sign up is $5 in May 2024, to create the problem above cost < $0.01). Once you've got an account, [make an API key](https://platform.openai.com/api-keys) and store it in [key.py](/gpt_dup/key.py).  (Alternatively, if no key is found, the software will ask with each run).
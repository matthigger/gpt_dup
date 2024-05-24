import argparse
import pathlib
import re
from datetime import datetime

from openai import OpenAI

from gpt_dup.key import api_key

client = OpenAI(api_key=api_key)

from tenacity import retry, stop_after_attempt, wait_random_exponential


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def completion_with_backoff(**kwargs):
    return client.chat.completions.create(**kwargs)


def duplicate_and_save_cli():
    description = """ 
    Duplicates and refreshes a given math problem via chatGPT, updating 
    numbers and solutions as needed.  Results will vary, but this tool has been
    successful for many simple math problems from CS1800 given a well 
    formated latex template. 
    """
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('-f', '--file', type=str, help='Input File',
                        required=True, dest='file')
    parser.add_argument('-o', '--out', type=str, dest='file_out',
                        help='Output File (will add index to input by default)')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='run in quiet mode', dest='quiet')
    args = parser.parse_args()

    duplicate_and_save(file=args.file, file_out=args.file_out,
                       verbose=not args.quiet)


def duplicate_and_save(file, file_out=None, verbose=True):
    # choose a file out, write a placeholder file with timestamp
    if file_out is None:
        file_out = get_file_out_add_one(file=file)

    if verbose:
        print(f'new problem requested: {file_out}')

    new_prob = duplicate(file=file)

    with open(file_out, 'w') as f:
        f.write(new_prob)

    if verbose:
        print(new_prob)
        print(f'written to: {file_out}')

    return file_out


def duplicate(file=None, s=None, model='gpt-4o'):
    assert (file is None) != (s is None), 'file xor s required'

    if s is None:
        s = open(file).read()

    prompt = '''Provide a file in a similar format, rewriting the math problem 
    with new numbers and updating the solutions as needed to ensure 
    correctness?  Your response should include only the latex, do not include 
    anything in your response which is not latex.
    '''
    messages = [{'role': 'user',
                 'content': prompt + s}]
    completion = completion_with_backoff(model=model, messages=messages)
    return completion.choices[0].message.content


def get_file_out_add_one(file, z_fill_width=2, touch=True):
    file = pathlib.Path(file)

    # get old idx (if present)
    match = re.search('\d+$', file.stem)
    if match is None:
        new_idx = 0
        stem_old = file.stem
    else:
        grp = match.group()
        new_idx = int(grp) + 1
        stem_old = file.stem[:-len(grp)]

    for _ in range(1000):
        file_out = file.with_stem(stem_old + str(new_idx).zfill(z_fill_width))
        if not file_out.exists():
            if touch:
                with open(file_out, 'w') as f:
                    s_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f'requested at: {s_time} (this will be overwritten)',
                          file=f)
            return file_out
        new_idx += 1

    raise RuntimeError(f'no unique file out created: {file}')


if __name__ == '__main__':
    duplicate_and_save_cli()

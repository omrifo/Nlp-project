import json
import os
import re
from sys import argv
import matplotlib.pyplot as plt
from collections import Counter
import math

def zipf_law(all_tokens, image_path):

    tokens = re.findall(r'\b\w+\b', all_tokens)
    
    token_counts = Counter(tokens)
    
    sorted_token_counts = token_counts.most_common()
    
    tokens, frequencies = zip(*sorted_token_counts)
    print("The Highest Frequency:")
    for i in range(10):
        print(sorted_token_counts[i])
    print("The Lowest Frequency:") 
    for i in range(1, 11):
        print(sorted_token_counts[-i])   
    ranks = range(1, len(tokens) + 1)
    log2_ranks = [math.log2(rank) for rank in ranks]
    log2_frequencies = [math.log2(frequency) for frequency in frequencies]

    plt.figure(figsize=(10, 6))
    plt.plot(log2_ranks, log2_frequencies, marker='o', linestyle='-', color='b')

    plt.title("Zipf's Law")
    plt.xlabel("Log2 Rank")
    plt.ylabel("Log2 Frequency")
    plt.grid(True)
    plt.savefig(image_path, dpi=300)



def extract_key_from_all_lines(jsonl_file):
    extracted_values = []
    with open(jsonl_file, 'r', encoding="utf8") as file:
        for line in file:
            record = json.loads(line)
            if "sentence_text: " in record.keys():
                 extracted_values.append(record["sentence_text: "])

    return extracted_values


if __name__ == "__main__":
   
    
    jsonl_file_path = argv[1]
    directory=argv[2]
    full_path=os.path.join(directory,"plot.png")

    all_tokens_corpus_str=""
    all_tokens_corpus=extract_key_from_all_lines(jsonl_file_path)
    for token in all_tokens_corpus  :
        all_tokens_corpus_str+=str(token)
        all_tokens_corpus_str+=" "
 
    zipf_law(all_tokens_corpus_str, full_path)

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from collections import defaultdict
import pandas as pd
from itertools import combinations


#read transaction data from CSV file
def read_transactions_from_csv(file_path, percent):
    """
    Load transaction data from a CSV file.
    """
    transactions = defaultdict(set)
    df = pd.read_csv(file_path)
    num_records = int(len(df) * (percent / 100))
    df = df.head(num_records)
    for index, row in df.iterrows():
        transaction_no = row['TransactionNo']
        item = row['Items']
        transactions[transaction_no].add(item)
    return transactions


#generate candidate itemsets of a given size
def generate_candidate_itemsets(itemsets, size):
    candidate_itemsets = set()
    for itemset1 in itemsets:
        for itemset2 in itemsets:
            union_set = itemset1.union(itemset2)
            if len(union_set) == size:
                candidate_itemsets.add(union_set)
    return candidate_itemsets


#prune infrequent itemsets
def prune_itemsets(candidate_itemsets, transactions, min_support):
    pruned_itemsets = {}
    total_transactions = len(transactions)
    for itemset in candidate_itemsets:
        support_count = 0
        for transaction in transactions.values():
            if all(item in transaction for item in itemset):
                support_count += 1
        support = support_count / total_transactions
        if support >= min_support:
            pruned_itemsets[itemset] = support
    return pruned_itemsets


#generate frequent itemsets apriori
def apriori(transactions, min_support):

    item_counts = {}
    for transaction in transactions.values():
        for item in transaction:
            item_counts[item] = item_counts.get(item, 0) + 1

    frequent_itemsets = {frozenset([item]): support for item, support in item_counts.items() if
                         support / len(transactions) >= min_support}


    size = 2
    all_frequent_itemsets = {}
    while frequent_itemsets:
        all_frequent_itemsets.update(frequent_itemsets)
        candidate_itemsets = generate_candidate_itemsets(frequent_itemsets.keys(), size)
        pruned_itemsets = prune_itemsets(candidate_itemsets, transactions, min_support)
        frequent_itemsets = pruned_itemsets
        size += 1

    return all_frequent_itemsets


#generate association rules from frequent itemsets
def generate_association_rules(frequent_itemsets, min_confidence):
    association_rules = []
    for itemset in frequent_itemsets:
        if len(itemset) > 1:
            for i in range(1, len(itemset)):
                for subset in combinations(itemset, i):
                    antecedent = frozenset(subset)
                    consequent = itemset.difference(antecedent)
                    confidence = frequent_itemsets[itemset] / frequent_itemsets[antecedent]
                    if confidence >= min_confidence:
                        association_rules.append((antecedent, consequent, confidence))
    return association_rules



def run_apriori(file_path, min_support, min_confidence, percent):
    transactions = read_transactions_from_csv(file_path, percent)
    frequent_itemsets = apriori(transactions, min_support)
    association_rules = generate_association_rules(frequent_itemsets, min_confidence)
    return frequent_itemsets, association_rules

#GUI

def on_button_click():
    min_support = float(support_entry.get())
    min_confidence = float(confidence_entry.get())
    file_path = file_entry.get()
    percent = float(percent_entry.get())
    if not file_path:
        messagebox.showerror("Error", "Please select a file.")
        return

    frequent_itemsets, association_rules = run_apriori(file_path, min_support, min_confidence, percent)


    frequent_itemsets_text.delete('1.0', tk.END)
    association_rules_text.delete('1.0', tk.END)

    for itemset, support in frequent_itemsets.items():
        frequent_itemsets_text.insert(tk.END, f"{list(itemset)} - Support: {support}\n")

    for antecedent, consequent, confidence in association_rules:
        association_rules_text.insert(tk.END, f"{list(antecedent)} => {list(consequent)} - Confidence: {confidence}\n")



def browse_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        file_entry.delete(0, tk.END)
        file_entry.insert(0, file_path)


#main window
root = tk.Tk()
root.title("Apriori Algorithm")

# Create input fields and labels
file_label = ttk.Label(root, text="Select File:")
file_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
file_entry = ttk.Entry(root)
file_entry.grid(row=0, column=1, padx=5, pady=5)
browse_button = ttk.Button(root, text="Browse", command=browse_file)
browse_button.grid(row=0, column=2, padx=5, pady=5)

percent_label = ttk.Label(root, text="Percentage of Records to Read:")
percent_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
percent_entry = ttk.Entry(root)
percent_entry.grid(row=1, column=1, padx=5, pady=5)

support_label = ttk.Label(root, text="Minimum Support:")
support_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
support_entry = ttk.Entry(root)
support_entry.grid(row=2, column=1, padx=5, pady=5)

confidence_label = ttk.Label(root, text="Minimum Confidence:")
confidence_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
confidence_entry = ttk.Entry(root)
confidence_entry.grid(row=3, column=1, padx=5, pady=5)

button = ttk.Button(root, text="Run Apriori", command=on_button_click)
button.grid(row=4, column=0, columnspan=3, padx=5, pady=5)

# display frequent itemsets and association rules
frequent_itemsets_text = tk.Text(root, height=10, width=50)
frequent_itemsets_text.grid(row=5, column=0, columnspan=3, padx=5, pady=5)

association_rules_text = tk.Text(root, height=10, width=50)
association_rules_text.grid(row=6, column=0, columnspan=3, padx=5, pady=5)


root.mainloop()

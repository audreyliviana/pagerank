import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration") 
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # Calculate the probability of choosing a random page
    random_prob = (1-damping_factor) / len(corpus)
    # Calculate the probability of choosing a linked page
    linked_prob = damping_factor / len(corpus[page]) if corpus[page] else 0
    # Initialize dict
    proba = {p: (random_prob if linked_prob else 1/len(corpus)) for p in corpus}
    # Update linked pages probability
    for p in corpus[page]:
        proba[p] += linked_prob
    
    return proba


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Initialize sample counts
    samples = {p: 0 for p in corpus}
    # Choose a random starting page
    current_page = random.choice(list(corpus.keys()))
    # Generate samples
    for _ in range(n):
        samples[current_page] += 1
        transition_proba = transition_model(corpus, current_page, damping_factor)
        current_page = random.choices(list(transition_proba.keys()), weights=transition_proba.values())[0]
    
    # Calculate the estimated PageRank:
    pagerank = {p: samples[p] / n for p in corpus}

    return pagerank

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # Initialize pagerank
    N = len(corpus)
    pagerank = {p: 1 / N for p in corpus}
    threshold = 0.001

    while True:
        new_pagerank = {} 
        for page in corpus:
            rank = (1 - damping_factor) / N
            for p in corpus:
                if page in corpus[p]:
                    rank += damping_factor * pagerank[p] / len(corpus[p])
            new_pagerank[page] = rank
        # Check for convergence:
        if all(abs(new_pagerank[p] - pagerank[p]) < threshold for p in corpus):
            break
        pagerank = new_pagerank
    
    return pagerank

            


if __name__ == "__main__":
    main()

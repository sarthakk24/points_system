def score_word(attended):
        
    word_counts = {}
            
    for word in attended:
        if word in word_counts:
            word_counts[word] += 1
        else:
            word_counts[word] = 1

        # Define scoring rules
    scores = {
        1: 2,
        2: 5,
        3: 10
    }

    # Calculate the score for each word based on its count
    word_scores = [scores[count] for count in word_counts.values()]

    # Calculate the final score by summing up the word scores
    score = sum(word_scores)

    return score
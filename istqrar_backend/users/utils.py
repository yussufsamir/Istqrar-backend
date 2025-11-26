def update_trust_score(user, change):
    trust = user.trust_score
    new_score = trust.score + change

    # keep score between 0 and 100
    if new_score < 0:
        new_score = 0
    if new_score > 100:
        new_score = 100

    trust.score = new_score
    trust.save()
    return trust.score

def calculate_final_score(ela_score, fake_score):
    return (0.4 * ela_score) + (0.6 * fake_score)


def classify_risk(final_score):
    if final_score >= 0.65:
        return "HIGH"
    elif final_score >= 0.35:
        return "MEDIUM"
    else:
        return "LOW"


# Example from Person 1
ela_score = 0.64
fake_score = 0.998

final_score = calculate_final_score(ela_score, fake_score)
risk = classify_risk(final_score)

print(f"ELA score:       {ela_score:.3f}")
print(f"Deepfake score:  {fake_score:.3f}")
print(f"Final score:     {final_score:.3f}")
print(f"Risk:            {risk}")
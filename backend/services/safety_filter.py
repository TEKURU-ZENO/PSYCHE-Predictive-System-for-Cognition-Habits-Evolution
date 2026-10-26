def sanitize(output: dict, confidence: float):
    text = output.get("text", "")

    banned = ["diagnosis", "disorder", "you are definitely"]
    for b in banned:
        text = text.replace(b, "")

    if confidence < 0.6:
        text = text.replace(" are ", " may be ").replace(" is ", " could be ")

    output["text"] = text
    return output

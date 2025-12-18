from end_check.gemini import gemini_vote
from end_check.gpt import gpt_vote
from end_check.grok import grok_vote

def finished(goal, path, sens):
    s = ""
    for i in sens:
        s += f"{i}, "
    gpt = gpt_vote(goal, path, s)
    gemini = gemini_vote(goal, path, s)
    grok = grok_vote(goal, path, s)

    return gpt and (gemini or grok) or (gemini and grok)
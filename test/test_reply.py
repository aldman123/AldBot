from src.reply import TextReplyTrigger


def test_reply_matching():
    trigger = TextReplyTrigger(triggers=["pi"], reply='Did you mean "half of tau"?')

    assert trigger.isTriggered("pie") is False
    assert trigger.isTriggered("I love pi") is True

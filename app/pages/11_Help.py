"""Help & tutorial page.

Written deliberately in very plain English for users who are not
confident with computers. Big numbered steps, no jargon.
"""

import streamlit as st

from app.auth import require_auth
from app.branding import inject_css, page_header, tut_section, tut_step

require_auth()
inject_css()
page_header(
    "Help — How do I use this?",
    "Simple step-by-step instructions. No technical knowledge needed.",
)

st.markdown(
    "This page explains everything in plain English. "
    "**You cannot break anything by clicking around** — so don't worry, just have a go. "
    "If you get lost, click **Help** in the menu on the left to come back here."
)

tut_section("Getting in")

tut_step(
    1,
    "Signing in",
    "Type your <b>work email address</b> into the box and press the orange "
    "<b>Send sign-in code</b> button. Now open your email — you will have a message "
    "with an <b>8-digit number</b> in it. Type that number into the app and press "
    "<b>Verify and sign in</b>. That's it — no password to remember!",
    where="The first screen you see",
)

tut_step(
    2,
    "Didn't get the email?",
    "Wait one minute and check your <b>junk or spam folder</b> — sometimes the email "
    "hides in there. Still nothing? Press <b>Use a different email</b> and check you "
    "typed your email address correctly. One wrong letter and it goes to the wrong place.",
    where="The sign-in screen",
)

tut_section("Your training")

tut_step(
    3,
    "See your own training",
    "Click <b>My Profile</b> in the menu on the left. This shows all your courses "
    "and when each one runs out. Think of it like the MOT on your car — "
    "green means fine, red means it needs doing.",
    where="My Profile — left menu",
)

tut_step(
    4,
    "What do the colours mean?",
    "🟢 <b>Green</b> — all good, nothing to do. "
    "🟡 <b>Yellow</b> — runs out within 90 days, start thinking about it. "
    "🟠 <b>Orange</b> — runs out within 30 days, book your course now. "
    "🔴 <b>Red</b> — expired or about to expire, sort it straight away.",
)

tut_step(
    5,
    "Upload a certificate",
    "Done a course and got a certificate? Go to <b>My Profile</b>, find the course in "
    "your list, and click <b>Upload certificate</b>. Choose the photo or PDF from your "
    "phone or computer, then press the button. A manager will check it and tick it off — "
    "you don't need to do anything else.",
    where="My Profile — left menu",
)

st.markdown("---")

with st.expander("🧑‍💼 **For managers** — running the team (click to open)"):
    tut_section("Managing the team")
    tut_step(
        6,
        "The Dashboard — your morning glance",
        "Click <b>Dashboard</b> to see the big picture: how compliant the team is, "
        "what's expired, and what runs out soon. The big dial is like a fuel gauge — "
        "the closer to 100, the better.",
        where="Dashboard — left menu",
    )
    tut_step(
        7,
        "The Matrix — everyone at once",
        "Click <b>Matrix</b> to see every person and every course in one big grid. "
        "Same traffic-light colours: red squares are the problems.",
        where="Matrix — left menu",
    )
    tut_step(
        8,
        "Add a new person",
        "Click <b>People</b>, then fill in their name and email. To let them sign in "
        "themselves, use <b>send invite</b> — they get an email with a link, "
        "click it, and they're in.",
        where="People — left menu",
    )
    tut_step(
        9,
        "Approve uploaded certificates",
        "When someone uploads a certificate it lands in <b>Approvals</b>, waiting for you. "
        "Open it, look at the certificate, and press <b>Approve</b> if it looks right "
        "or <b>Reject</b> with a short note if it doesn't.",
        where="Approvals — left menu",
    )

st.markdown("---")
st.markdown("### Common questions")

with st.expander("**I clicked something and now I'm lost**"):
    st.markdown(
        "No problem — nothing is broken. Just click any name in the **menu on the left** "
        "to go where you want. **My Profile** is your home."
    )

with st.expander("**My details are wrong (name, phone, email)**"):
    st.markdown(
        "Go to **My Profile** and look for the edit section — you can fix your own "
        "contact details there. If something else is wrong, tell your manager."
    )

with st.expander("**The screen looks odd or stuck**"):
    st.markdown(
        "Press the **refresh button** in your browser (the circular arrow near the top, "
        "or the F5 key). That fixes most things. Still odd? Sign out and sign back in."
    )

with st.expander("**I need a human to help me**"):
    st.markdown(
        "Speak to your manager or email **Beacon Risk** — they can sort accounts, "
        "logins and anything on this list."
    )

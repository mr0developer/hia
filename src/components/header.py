import streamlit as st
from config.app_config import PRIMARY_COLOR, SECONDARY_COLOR


def show_user_greeting():
    """Render a styled top-right user greeting bar."""
    if not st.session_state.get("user"):
        return

    display_name = (
        st.session_state.user.get("name")
        or st.session_state.user.get("email", "")
    )
    # Use only the first name for a friendlier feel
    first_name = display_name.split()[0] if display_name else display_name

    st.markdown(
        f"""
        <style>
            .hia-greeting-bar {{
                display: flex;
                align-items: center;
                justify-content: flex-end;
                gap: 0.6rem;
                padding: 0.55rem 1.25rem 0.55rem 1rem;
                background: linear-gradient(
                    90deg,
                    transparent 0%,
                    rgba(25, 118, 210, 0.06) 60%,
                    rgba(100, 181, 246, 0.12) 100%
                );
                border-bottom: 1px solid rgba(100, 181, 246, 0.12);
                border-radius: 0 0 12px 12px;
                backdrop-filter: blur(4px);
                margin-bottom: 0.25rem;
            }}

            .hia-greeting-avatar {{
                width: 34px;
                height: 34px;
                border-radius: 50%;
                background: linear-gradient(135deg, {SECONDARY_COLOR}, {PRIMARY_COLOR});
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 0.85rem;
                font-weight: 700;
                color: #ffffff;
                letter-spacing: 0.5px;
                flex-shrink: 0;
                box-shadow: 0 2px 8px rgba(100, 181, 246, 0.35);
            }}

            .hia-greeting-text {{
                display: flex;
                flex-direction: column;
                align-items: flex-end;
                line-height: 1.2;
            }}

            .hia-greeting-label {{
                font-size: 0.7rem;
                color: rgba(100, 181, 246, 0.6);
                letter-spacing: 0.06em;
                text-transform: uppercase;
                font-family: "Source Sans Pro", sans-serif;
            }}

            .hia-greeting-name {{
                font-size: 0.95rem;
                font-weight: 600;
                color: {PRIMARY_COLOR};
                font-family: "Source Sans Pro", sans-serif;
                letter-spacing: 0.01em;
            }}

            .hia-greeting-dot {{
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #4caf50;
                box-shadow: 0 0 6px rgba(76, 175, 80, 0.7);
                flex-shrink: 0;
            }}
        </style>

        <div class="hia-greeting-bar">
            <div class="hia-greeting-text">
                <span class="hia-greeting-label">You are Signed in</span>
                <span class="hia-greeting-name">👋 Hello, {first_name}!</span>
            </div>
            <div class="hia-greeting-avatar">{first_name[0].upper() if first_name else "?"}</div>
            <div class="hia-greeting-dot" title="Online"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

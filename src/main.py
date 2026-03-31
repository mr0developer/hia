import streamlit as st
from auth.session_manager import SessionManager
from components.auth_pages import show_login_page, show_update_password_form
from components.sidebar import show_sidebar
from components.analysis_form import show_analysis_form
from components.footer import show_footer
from components.header import show_user_greeting
from config.app_config import APP_NAME, APP_TAGLINE, APP_DESCRIPTION, APP_ICON
from services.ai_service import get_chat_response

# Must be the first Streamlit command
st.set_page_config(
    page_title="HIA - Health Insights Agent", page_icon="🩺", layout="wide"
)

# Detect password-reset redirect BEFORE init_session() so that init_session()
# knows to skip token validation and not wipe the reset tokens from state.
# Supabase sends either:
#   PKCE flow  → ?token_hash=xxx&type=recovery  (modern default)
#   Legacy flow → ?access_token=xxx&type=recovery
# Both must be captured BEFORE st.query_params.clear() is called.

if st.query_params.get("type") == "recovery":
    st.session_state["password_reset_mode"] = True

    token_hash = st.query_params.get("token_hash", "")
    access_token = st.query_params.get("access_token", "")
    refresh_token = st.query_params.get("refresh_token", "")

    if token_hash:
        st.session_state["reset_token_hash"] = token_hash
    if access_token:
        st.session_state["reset_access_token"] = access_token
        st.session_state["reset_refresh_token"] = refresh_token

    # Clear params AFTER reading all values
    st.query_params.clear()

# Initialize session state
SessionManager.init_session()

# Hide all Streamlit form-related elements + global background styling
st.markdown(
    """
    <style>
        /* ── Hide form submission helper text ── */
        div[data-testid="InputInstructions"] > span:nth-child(1) {
            visibility: hidden;
        }

        /* ── Global body background ── */
        .stApp {
            background:
                radial-gradient(ellipse at 15% 20%, rgba(25, 118, 210, 0.08) 0%, transparent 50%),
                radial-gradient(ellipse at 85% 75%, rgba(100, 181, 246, 0.07) 0%, transparent 50%),
                radial-gradient(ellipse at 50% 50%, rgba(21, 101, 192, 0.04) 0%, transparent 70%),
                linear-gradient(160deg, #0a0e1a 0%, #0d1117 40%, #0a0f1e 100%);
            background-attachment: fixed;
        }

        /* ── Subtle dot-grid texture overlay ── */
        .stApp::before {
            content: "";
            position: fixed;
            inset: 0;
            background-image: radial-gradient(rgba(100, 181, 246, 0.07) 1px, transparent 1px);
            background-size: 32px 32px;
            pointer-events: none;
            z-index: 0;
        }

        /* ── Keep content above the texture ── */
        .stApp > * {
            position: relative;
            z-index: 1;
        }

        /* ── Main content area — subtle frosted card feel ── */
        .main .block-container {
            background: rgba(13, 17, 23, 0.55);
            backdrop-filter: blur(2px);
            border-radius: 16px;
            border: 1px solid rgba(100, 181, 246, 0.06);
            padding-top: 1.5rem;
        }

        /* ── Sidebar background ── */
        [data-testid="stSidebar"] {
            background:
                linear-gradient(180deg,
                    rgba(13, 21, 40, 0.98) 0%,
                    rgba(10, 16, 30, 0.98) 100%
                ) !important;
            border-right: 1px solid rgba(100, 181, 246, 0.1) !important;
        }

        /* ── Scrollbar styling ── */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb {
            background: rgba(100, 181, 246, 0.25);
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(100, 181, 246, 0.45);
        }

        /* ── Danger & Cancel Button Styling using Streamlit Keys ── */
        div[class*="st-key-logout"] button, 
        div[class*="st-key-delete"] button,
        div[class*="st-key-cancel"] button,
        div[class*="st-key-confirm"] button {
            background-color: rgba(211, 47, 47, 0.85) !important;
            color: #ffffff !important;
            border: 1px solid rgba(211, 47, 47, 0.5) !important;
        }
        div[class*="st-key-logout"] button:hover, 
        div[class*="st-key-delete"] button:hover,
        div[class*="st-key-cancel"] button:hover,
        div[class*="st-key-confirm"] button:hover {
            background-color: rgba(211, 47, 47, 1) !important;
            border: 1px solid rgba(211, 47, 47, 0.8) !important;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# If Supabase redirects with the recovery token in the URL hash fragment,
# use window.parent to rewrite the top-level browser URL (not the iframe URL).
st.markdown(
    """
    <script>
        (function() {
            try {
                // Try to access the parent frame's location (works when not cross-origin)
                var topHash = window.parent.location.hash;
                if (topHash && topHash.includes('type=recovery')) {
                    var params = new URLSearchParams(topHash.substring(1));
                    var tokenHash  = params.get('token_hash');
                    var accessToken = params.get('access_token');
                    var refreshToken = params.get('refresh_token');
                    var newUrl = window.parent.location.pathname + '?type=recovery';
                    if (tokenHash)    newUrl += '&token_hash='    + encodeURIComponent(tokenHash);
                    if (accessToken)  newUrl += '&access_token='  + encodeURIComponent(accessToken);
                    if (refreshToken) newUrl += '&refresh_token=' + encodeURIComponent(refreshToken);
                    window.parent.location.replace(newUrl);
                    return;
                }
                // Also check the current frame's hash as fallback
                var hash = window.location.hash;
                if (hash && hash.includes('type=recovery')) {
                    var params = new URLSearchParams(hash.substring(1));
                    var tokenHash  = params.get('token_hash');
                    var accessToken = params.get('access_token');
                    var refreshToken = params.get('refresh_token');
                    var newUrl = window.location.pathname + '?type=recovery';
                    if (tokenHash)    newUrl += '&token_hash='    + encodeURIComponent(tokenHash);
                    if (accessToken)  newUrl += '&access_token='  + encodeURIComponent(accessToken);
                    if (refreshToken) newUrl += '&refresh_token=' + encodeURIComponent(refreshToken);
                    window.location.replace(newUrl);
                }
            } catch(e) {
                // cross-origin restriction — fall back to current frame
                var hash = window.location.hash;
                if (hash && hash.includes('type=recovery')) {
                    var params = new URLSearchParams(hash.substring(1));
                    var tokenHash  = params.get('token_hash');
                    var accessToken = params.get('access_token');
                    var newUrl = window.location.pathname + '?type=recovery';
                    if (tokenHash)    newUrl += '&token_hash='    + encodeURIComponent(tokenHash);
                    if (accessToken)  newUrl += '&access_token='  + encodeURIComponent(accessToken);
                    window.location.replace(newUrl);
                }
            }
        })();
    </script>
""",
    unsafe_allow_html=True,
)


def show_welcome_screen():
    st.markdown(
        f"""
        <div style='text-align: center; padding: 50px;'>
            <h1>{APP_ICON} {APP_NAME}</h1>
            <h3>{APP_DESCRIPTION}</h3>
            <p style='font-size: 1.2em; color: #666;'>{APP_TAGLINE}</p>
            <p>Start by creating a new analysis session</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([2, 3, 2])
    with col2:
        if st.button(
            "➕ Create New Analysis Session", use_container_width=True, type="primary"
        ):
            success, session = SessionManager.create_chat_session()
            if success:
                st.session_state.current_session = session
                st.rerun()
            else:
                st.error("Failed to create session")


def show_chat_history():
    success, messages = st.session_state.auth_service.get_session_messages(
        st.session_state.current_session["id"]
    )

    if success:
        for msg in messages:
            # Skip system messages (they contain report text metadata)
            if msg.get("role") == "system":
                continue
            if msg["role"] == "user":
                st.info(msg["content"])
            else:
                st.success(msg["content"])
        return messages
    return []


def handle_chat_input(messages):
    if prompt := st.chat_input("Ask a follow-up question about the report..."):
        # Display user message immediately
        st.info(prompt)

        # Save user message
        st.session_state.auth_service.save_chat_message(
            st.session_state.current_session["id"], prompt, role="user"
        )

        # Get context (report text)
        # We try to get it from session state first (for immediate use)
        context_text = st.session_state.get("current_report_text", "")

        # If not in session state, try to retrieve from stored system message
        if not context_text and messages:
            for msg in messages:
                if msg.get("role") == "system" and "__REPORT_TEXT__" in msg.get(
                    "content", ""
                ):
                    # Extract report text from system message
                    content = msg.get("content", "")
                    start_idx = content.find("__REPORT_TEXT__\n") + len(
                        "__REPORT_TEXT__\n"
                    )
                    end_idx = content.find("\n__END_REPORT_TEXT__")
                    if start_idx > len("__REPORT_TEXT__\n") - 1 and end_idx > start_idx:
                        context_text = content[start_idx:end_idx]
                        # Also restore to session state for future use
                        st.session_state.current_report_text = context_text
                        break

        with st.spinner("Thinking..."):
            response = get_chat_response(prompt, context_text, messages)

            st.success(response)

            # Save AI response
            st.session_state.auth_service.save_chat_message(
                st.session_state.current_session["id"], response, role="assistant"
            )
            # Rerun to update history display properly
            st.rerun()


def main():
    SessionManager.init_session()

    if st.session_state.get("password_reset_mode"):
        # If we have a token_hash (PKCE flow), exchange it for a real session first.
        token_hash = st.session_state.get("reset_token_hash", "")
        if token_hash and not st.session_state.get("reset_session_verified"):
            success, result = st.session_state.auth_service.verify_recovery_token(token_hash)
            if success:
                st.session_state["reset_session_verified"] = True
                # token_hash is single-use — clear it so it isn't re-used on next rerun
                st.session_state.pop("reset_token_hash", None)
            else:
                st.error(f"Reset link is invalid or has expired. Please request a new one. ({result})")
                st.session_state.pop("password_reset_mode", None)
                show_footer()
                return

        # Fallback: re-apply raw access_token if that's what arrived (legacy flow)
        access_token = st.session_state.get("reset_access_token", "")
        refresh_token = st.session_state.get("reset_refresh_token", "")
        if access_token and not st.session_state.get("reset_session_verified"):
            try:
                st.session_state.auth_service.supabase.auth.set_session(
                    access_token, refresh_token
                )
            except Exception:
                pass

        show_update_password_form()
        show_footer()
        return

    if not SessionManager.is_authenticated():
        show_login_page()
        show_footer()
        return

    # Show user greeting at the top
    show_user_greeting()

    # Show sidebar
    show_sidebar()

    # Main chat area
    if st.session_state.get("current_session"):
        st.title(f"📊 {st.session_state.current_session['title']}")
        messages = show_chat_history()

        # If we have messages (meaning analysis is done), show chat input
        # Otherwise show analysis form
        if messages:
            # We can still show the analysis form collapsed or just hide it
            # For better UX, if analysis is done, we might not want to show the form again
            # unless the user wants to re-analyze/start over.
            # But the current form design allows re-analysis.
            # Let's put the analysis form in an expander if analysis is done.
            with st.expander("New Analysis / Update Report", expanded=False):
                show_analysis_form()

            handle_chat_input(messages)
        else:
            show_analysis_form()
    else:
        show_welcome_screen()


if __name__ == "__main__":
    main()

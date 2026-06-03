"""
streamlit_app.py — FundooNotes Backend Tester

A minimal Streamlit UI to manually exercise every endpoint of the
fundooNotes Django REST Framework backend.

Run:
    streamlit run streamlit_app.py

Requirements (pip install):
    streamlit requests
"""

import streamlit as st
import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DEFAULT_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="FundooNotes Tester", page_icon="📝", layout="wide")

# ---------------------------------------------------------------------------
# Session state helpers
# ---------------------------------------------------------------------------

def init_state():
    defaults = {
        "base_url": DEFAULT_BASE_URL,
        "access": "",
        "refresh": "",
        "username": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


def auth_headers() -> dict:
    if st.session_state.access:
        return {"Authorization": f"Bearer {st.session_state.access}"}
    return {}


def url(path: str) -> str:
    return st.session_state.base_url.rstrip("/") + path


def show_response(resp: requests.Response):
    """Render a response with colour-coded status."""
    color = "green" if resp.ok else "red"
    st.markdown(f"**Status:** :{color}[{resp.status_code}]")
    try:
        st.json(resp.json())
    except Exception:
        st.code(resp.text)


# ---------------------------------------------------------------------------
# Sidebar — connection + auth status
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("📝 FundooNotes")
    st.session_state.base_url = st.text_input("Backend URL", value=st.session_state.base_url)

    st.divider()
    if st.session_state.access:
        st.success(f"Logged in as **{st.session_state.username}**")
        if st.button("🚪 Logout (quick)", use_container_width=True):
            if st.session_state.refresh:
                try:
                    requests.post(
                        url("/api/users/logout/"),
                        json={"refresh": st.session_state.refresh},
                        headers=auth_headers(),
                        timeout=5,
                    )
                except Exception:
                    pass
            st.session_state.access = ""
            st.session_state.refresh = ""
            st.session_state.username = ""
            st.rerun()
    else:
        st.warning("Not logged in")

    st.divider()
    page = st.radio(
        "Navigate",
        [
            "🔐 Auth — Register",
            "🔑 Auth — Login / Logout",
            "✉️ Auth — Email Verify",
            "🔒 Auth — Password Reset",
            "👤 Profile",
            "📝 Notes",
            "🏷️ Labels",
            "📊 Stats",
        ],
    )

# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

# ── Register ────────────────────────────────────────────────────────────────
if page == "🔐 Auth — Register":
    st.header("Register a new account")
    with st.form("register_form"):
        username = st.text_input("Username")
        email    = st.text_input("Email")
        phone    = st.text_input("Phone number (max 15 digits)")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Register")

    if submitted:
        resp = requests.post(
            url("/api/users/register/"),
            json={"username": username, "email": email,
                  "phone_number": phone, "password": password},
            timeout=10,
        )
        show_response(resp)
        if resp.ok:
            st.info("Check your email (or Celery logs) for the verification link.")


# ── Login / Logout ──────────────────────────────────────────────────────────
elif page == "🔑 Auth — Login / Logout":
    st.header("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        resp = requests.post(
            url("/api/users/login/"),
            json={"username": username, "password": password},
            timeout=10,
        )
        show_response(resp)
        if resp.ok:
            data = resp.json().get("payload", {})
            st.session_state.access  = data.get("access", "")
            st.session_state.refresh = data.get("refresh", "")
            st.session_state.username = username
            st.success("Tokens saved — you are now logged in.")

    st.divider()
    st.header("Logout")
    st.caption("Blacklists the current refresh token.")
    if st.button("Logout", disabled=not st.session_state.refresh):
        resp = requests.post(
            url("/api/users/logout/"),
            json={"refresh": st.session_state.refresh},
            headers=auth_headers(),
            timeout=10,
        )
        show_response(resp)
        if resp.ok:
            st.session_state.access  = ""
            st.session_state.refresh = ""
            st.session_state.username = ""
            st.rerun()

    st.divider()
    st.header("Refresh Access Token")
    if st.button("Refresh token", disabled=not st.session_state.refresh):
        resp = requests.post(
            url("/api/token/refresh/"),
            json={"refresh": st.session_state.refresh},
            timeout=10,
        )
        show_response(resp)
        if resp.ok:
            data = resp.json()
            st.session_state.access  = data.get("access", st.session_state.access)
            st.session_state.refresh = data.get("refresh", st.session_state.refresh)
            st.success("Access token refreshed.")


# ── Email Verification ───────────────────────────────────────────────────────
elif page == "✉️ Auth — Email Verify":
    st.header("Verify Email")
    st.caption("Paste the token from the verification email / Celery log.")
    token = st.text_input("Verification token")
    if st.button("Verify", disabled=not token):
        resp = requests.get(
            url("/api/users/verify-email/"),
            params={"token": token},
            timeout=10,
        )
        show_response(resp)


# ── Password Reset ───────────────────────────────────────────────────────────
elif page == "🔒 Auth — Password Reset":
    st.header("Request Password Reset")
    st.caption("Always returns 200 — no email enumeration.")
    with st.form("reset_req_form"):
        email = st.text_input("Email")
        submitted = st.form_submit_button("Send reset email")
    if submitted:
        resp = requests.post(
            url("/api/users/reset-password/"),
            json={"email": email},
            timeout=10,
        )
        show_response(resp)

    st.divider()
    st.header("Confirm Password Reset")
    with st.form("reset_confirm_form"):
        token        = st.text_input("Reset token (from email / Celery log)")
        new_password = st.text_input("New password", type="password")
        confirm      = st.text_input("Confirm new password", type="password")
        submitted2   = st.form_submit_button("Reset password")
    if submitted2:
        resp = requests.post(
            url("/api/users/reset-password-confirm/"),
            json={"token": token, "new_password": new_password,
                  "confirm_password": confirm},
            timeout=10,
        )
        show_response(resp)


# ── Profile ──────────────────────────────────────────────────────────────────
elif page == "👤 Profile":
    st.header("User Profile")
    if not st.session_state.access:
        st.warning("Login first.")
    else:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("GET profile")
            if st.button("Fetch profile"):
                resp = requests.get(url("/api/users/profile/"), headers=auth_headers(), timeout=10)
                show_response(resp)

        with col2:
            st.subheader("PUT profile")
            with st.form("profile_update_form"):
                new_username = st.text_input("New username")
                new_phone    = st.text_input("New phone number")
                submitted    = st.form_submit_button("Update")
            if submitted:
                payload = {}
                if new_username: payload["username"] = new_username
                if new_phone:    payload["phone_number"] = new_phone
                resp = requests.put(
                    url("/api/users/profile/"),
                    json=payload,
                    headers=auth_headers(),
                    timeout=10,
                )
                show_response(resp)

        with col3:
            st.subheader("DELETE (deactivate)")
            st.warning("This deactivates your account.")
            if st.button("Deactivate account"):
                resp = requests.delete(url("/api/users/profile/"), headers=auth_headers(), timeout=10)
                show_response(resp)
                if resp.status_code == 204:
                    st.session_state.access  = ""
                    st.session_state.refresh = ""
                    st.session_state.username = ""
                    st.rerun()


# ── Notes ────────────────────────────────────────────────────────────────────
elif page == "📝 Notes":
    st.header("Notes")
    if not st.session_state.access:
        st.warning("Login first.")
    else:
        tab_list, tab_create, tab_detail, tab_update, tab_delete = st.tabs(
            ["List", "Create", "Get by ID", "Update", "Delete"]
        )

        with tab_list:
            st.subheader("GET /api/notes/")
            if st.button("Fetch all notes"):
                resp = requests.get(url("/api/notes/"), headers=auth_headers(), timeout=10)
                show_response(resp)

        with tab_create:
            st.subheader("POST /api/notes/")
            with st.form("note_create_form"):
                title      = st.text_input("Title")
                content    = st.text_area("Content")
                label_ids  = st.text_input("Label IDs (comma-separated, optional)")
                submitted  = st.form_submit_button("Create note")
            if submitted:
                payload: dict = {"title": title, "content": content}
                if label_ids.strip():
                    try:
                        payload["label_ids"] = [int(x.strip()) for x in label_ids.split(",") if x.strip()]
                    except ValueError:
                        st.error("Label IDs must be integers.")
                        payload = {}
                if payload:
                    resp = requests.post(url("/api/notes/"), json=payload, headers=auth_headers(), timeout=10)
                    show_response(resp)

        with tab_detail:
            st.subheader("GET /api/notes/<id>/")
            note_id = st.number_input("Note ID", min_value=1, step=1, key="get_note_id")
            if st.button("Fetch note"):
                resp = requests.get(url(f"/api/notes/{int(note_id)}/"), headers=auth_headers(), timeout=10)
                show_response(resp)

        with tab_update:
            st.subheader("PATCH /api/notes/<id>/  (partial update)")
            with st.form("note_update_form"):
                upd_id      = st.number_input("Note ID", min_value=1, step=1)
                upd_title   = st.text_input("New title (leave blank to skip)")
                upd_content = st.text_area("New content (leave blank to skip)")
                upd_archive = st.selectbox("is_archived", ["(no change)", "True", "False"])
                upd_labels  = st.text_input("New label IDs (comma-separated, leave blank to skip)")
                submitted   = st.form_submit_button("Update note")
            if submitted:
                payload = {}
                if upd_title:   payload["title"]   = upd_title
                if upd_content: payload["content"] = upd_content
                if upd_archive != "(no change)":
                    payload["is_archived"] = upd_archive == "True"
                if upd_labels.strip():
                    try:
                        payload["label_ids"] = [int(x.strip()) for x in upd_labels.split(",") if x.strip()]
                    except ValueError:
                        st.error("Label IDs must be integers.")
                        payload = {}
                if payload:
                    resp = requests.patch(
                        url(f"/api/notes/{int(upd_id)}/"),
                        json=payload,
                        headers=auth_headers(),
                        timeout=10,
                    )
                    show_response(resp)

        with tab_delete:
            st.subheader("DELETE /api/notes/<id>/  (soft-delete → is_trashed=True)")
            del_id = st.number_input("Note ID", min_value=1, step=1, key="del_note_id")
            if st.button("Soft-delete note"):
                resp = requests.delete(url(f"/api/notes/{int(del_id)}/"), headers=auth_headers(), timeout=10)
                show_response(resp)
                if resp.status_code == 204:
                    st.success("Note soft-deleted (204 No Content).")


# ── Labels ───────────────────────────────────────────────────────────────────
elif page == "🏷️ Labels":
    st.header("Labels")
    if not st.session_state.access:
        st.warning("Login first.")
    else:
        tab_list, tab_create, tab_detail, tab_update, tab_delete = st.tabs(
            ["List", "Create", "Get by ID", "Update", "Delete"]
        )

        with tab_list:
            st.subheader("GET /api/labels/")
            if st.button("Fetch all labels"):
                resp = requests.get(url("/api/labels/"), headers=auth_headers(), timeout=10)
                show_response(resp)

        with tab_create:
            st.subheader("POST /api/labels/")
            with st.form("label_create_form"):
                label_title = st.text_input("Label title")
                submitted   = st.form_submit_button("Create label")
            if submitted:
                resp = requests.post(
                    url("/api/labels/"),
                    json={"title": label_title},
                    headers=auth_headers(),
                    timeout=10,
                )
                show_response(resp)

        with tab_detail:
            st.subheader("GET /api/labels/<id>/")
            lbl_id = st.number_input("Label ID", min_value=1, step=1, key="get_lbl_id")
            if st.button("Fetch label"):
                resp = requests.get(url(f"/api/labels/{int(lbl_id)}/"), headers=auth_headers(), timeout=10)
                show_response(resp)

        with tab_update:
            st.subheader("PATCH /api/labels/<id>/")
            with st.form("label_update_form"):
                upd_lbl_id    = st.number_input("Label ID", min_value=1, step=1)
                upd_lbl_title = st.text_input("New title")
                submitted     = st.form_submit_button("Update label")
            if submitted and upd_lbl_title:
                resp = requests.patch(
                    url(f"/api/labels/{int(upd_lbl_id)}/"),
                    json={"title": upd_lbl_title},
                    headers=auth_headers(),
                    timeout=10,
                )
                show_response(resp)

        with tab_delete:
            st.subheader("DELETE /api/labels/<id>/  (hard-delete)")
            del_lbl_id = st.number_input("Label ID", min_value=1, step=1, key="del_lbl_id")
            if st.button("Delete label"):
                resp = requests.delete(url(f"/api/labels/{int(del_lbl_id)}/"), headers=auth_headers(), timeout=10)
                show_response(resp)
                if resp.status_code == 204:
                    st.success("Label deleted (204 No Content).")


# ── Stats ────────────────────────────────────────────────────────────────────
elif page == "📊 Stats":
    st.header("Request Counts")
    st.caption("GET /api/stats/requests/ — per-method counter tracked by middleware.")
    if not st.session_state.access:
        st.warning("Login first.")
    else:
        if st.button("Fetch stats"):
            resp = requests.get(url("/api/stats/requests/"), headers=auth_headers(), timeout=10)
            show_response(resp)
            if resp.ok:
                counts = resp.json().get("payload", {})
                if counts:
                    st.bar_chart(counts)

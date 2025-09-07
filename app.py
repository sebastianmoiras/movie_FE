import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("http://104.214.185.151:8000")

# === SESSION STATE ===
if "token" not in st.session_state:
    st.session_state["token"] = None
if "user_name" not in st.session_state:
    st.session_state["user_name"] = "User"
if "userid" not in st.session_state:
    st.session_state["userid"] = None
if "page" not in st.session_state:
    st.session_state["page"] = "login"
if "selected_movie" not in st.session_state:
    st.session_state["selected_movie"] = None
if "movies_cache" not in st.session_state:
    st.session_state["movies_cache"] = []
if "search_results" not in st.session_state:
    st.session_state["search_results"] = []


# === SIDEBAR MENU ===
def sidebar_menu():
    st.sidebar.title("📌 Menu")

    if st.sidebar.button("🏠 Home"):
        st.session_state["page"] = "home"
        st.rerun()

    if st.sidebar.button("⭐ My Recommendations"):
        st.session_state["page"] = "recommend"
        st.rerun()

    if st.sidebar.button("❤️ My Liked Movies"):
        st.session_state["page"] = "liked_movies"
        st.rerun()

    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.session_state["page"] = "login"
        st.rerun()


# === LOGIN PAGE ===
def login_page():
    st.title("🔐 Login to Notflix")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            res = requests.post(
                f"{BASE_URL}/login",
                params={"email": email, "password": password}
            )
            data = res.json()

            if data.get("success"):
                st.session_state["token"] = data["token"]
                st.session_state["user_name"] = data.get("name", "User")
                st.session_state["userid"] = data.get("userid")
                st.session_state["page"] = "home"
                st.rerun()
            else:
                st.error(data.get("message", "Login failed"))
        except Exception as e:
            st.error(f"Login error: {e}")

    st.markdown("No account?")
    if st.button("Sign Up"):
        st.session_state["page"] = "signup"
        st.rerun()


# === SIGNUP PAGE ===
def signup_page():
    st.title("📝 Create Account")
    name = st.text_input("Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    age = st.number_input("Age", min_value=1, max_value=120)
    nationality = st.text_input("Nationality")
    gender = st.radio("Gender", ["male", "female"])

    genres = st.multiselect(
        "Preferred Genres (min 3)",
        options=[
            (1, "Action"), (2, "Adventure"), (3, "Animation"), (4, "Comedy"),
            (5, "Crime"), (6, "Documentary"), (7, "Drama"), (8, "Family"),
            (9, "Fantasy"), (10, "History"), (11, "Horror"), (12, "Music"),
            (13, "Mystery"), (14, "Romance"), (15, "Science Fiction"),
            (16, "Thriller"), (17, "TV Movie"), (18, "War"), (19, "Western")
        ],
        format_func=lambda x: x[1]
    )

    if st.button("Sign Up"):
        if "@" not in email:
            st.error("Email must contains @")
        elif len(password) < 8 or not any(c.isupper() for c in password) or not any(c.isdigit() for c in password):
            st.error("Password must be at least 8 characters long, contain an uppercase letter, and a number!!")
        elif len(genres) < 3:
            st.error("Pick at least 3 genres:")
        else:
            genre_ids = [g[0] for g in genres]
            try:
                res = requests.post(
                    f"{BASE_URL}/signup",
                    params={
                        "name": name,
                        "email": email,
                        "password": password,
                        "age": age,
                        "nationality": nationality.lower(),
                        "gender": gender,
                        "preferred_genres": genre_ids
                    }
                )
                data = res.json()
                if data.get("success"):
                    st.success("Signup successful, please login!")
                    st.session_state["page"] = "login"
                    st.rerun()
                else:
                    st.error(data.get("message", "Signup failed"))
            except Exception as e:
                st.error(f"Signup error: {e}")

    if st.button("Back to Login"):
        st.session_state["page"] = "login"
        st.rerun()


# === HOME PAGE ===
def home_page():
    sidebar_menu()
    st.markdown(f"### 👋 Hello, {st.session_state.get('user_name', 'User')}")

    st.subheader("🔎 Search Movies")
    query = st.text_input("type what you want to search:")
    if st.button("Search"):
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        try:
            res = requests.get(f"{BASE_URL}/search", params={"query": query}, headers=headers)
            if res.status_code == 200:
                st.session_state["search_results"] = res.json()
            else:
                st.error("Search failed.")
        except Exception as e:
            st.error(f"Error search: {e}")

    movies = st.session_state["search_results"] or st.session_state["movies_cache"]

    if not st.session_state["movies_cache"] and not st.session_state["search_results"]:
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        try:
            res = requests.get(f"{BASE_URL}/movies", headers=headers)
            if res.status_code == 200:
                st.session_state["movies_cache"] = res.json()
                movies = st.session_state["movies_cache"]
            else:
                st.error("Failed to fetch movies")
                return
        except Exception as e:
            st.error(f"Error fetching movies: {e}")
            return

    st.subheader("🎬 Movie List")

    cols_per_row = 5
    for i in range(0, len(movies), cols_per_row):
        cols = st.columns(cols_per_row, gap="medium")
        for j, col in enumerate(cols):
            if i + j < len(movies):
                m = movies[i + j]
                movie_id = m.get("movieid")

                with col:
                    st.markdown("<div style='margin-bottom:35px; padding:8px;'>", unsafe_allow_html=True)
                    if "poster_url" in m and m["poster_url"]:
                        st.image(m["poster_url"], use_container_width=True)

                    st.markdown(
                        f"<div style='text-align:center; font-size:14px; font-weight:bold; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;'>{m.get('title','Untitled')}</div>",
                        unsafe_allow_html=True
                    )

                    if movie_id:
                        if st.button("Detail", key=f"detail_{i}_{j}"):
                            st.session_state["selected_movie"] = movie_id
                            st.session_state["page"] = "movie_detail"
                            st.rerun()
                    else:
                        st.markdown("<div style='color:yellow; text-align:center;'>⚠️ ID unavailable</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)


# === MOVIE DETAIL PAGE ===
def movie_detail_page():
    sidebar_menu()
    movie_id = st.session_state["selected_movie"]
    if not movie_id:
        st.error("⚠️ Movie ID is invalid.")
        if st.button("⬅️ Back to Movies"):
            st.session_state["page"] = "home"
            st.rerun()
        return

    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    res = requests.get(f"{BASE_URL}/movies/{movie_id}", headers=headers)

    if res.status_code == 200:
        m = res.json()
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(m.get("poster_url", ""), use_container_width=True)
        with col2:
            st.markdown(f"## {m.get('title','Untitled')}")
            st.write(f"📅 Release Date: {m.get('release_date','-')}")
            st.write(f"🌐 Language: {m.get('language','-')}")
            st.write(f"🎭 Genres: {', '.join(m.get('genres', [])) if m.get('genres') else '-'}")
            st.write("**Overview:**")
            st.write(m.get("overview", "No description"))

            st.subheader("⭐ Your Feedback")
            rating = st.slider("Rating (1-5)", 1, 5, 3)
            liked = st.radio("Do you like this movie?", ["👍 Like", "👎 Dislike"])

            if st.button("Submit Feedback"):
                try:
                    res = requests.post(
                        f"{BASE_URL}/feedback",
                        params={
                            "userid": st.session_state["userid"],
                            "movieid": movie_id,
                            "rating": rating,
                            "liked": True if liked == "👍 Like" else False
                        },
                        headers=headers
                    )
                    data = res.json()
                    if data.get("success"):
                        st.success("Feedback saved!")
                    else:
                        st.error(data.get("message", "Failed to save feedback"))
                except Exception as e:
                    st.error(f"Error feedback: {e}")
    else:
        st.error(f"Movie details not found (status {res.status_code})")

    if st.button("⬅️ Back to Movies"):
        st.session_state["page"] = "home"
        st.rerun()


# === RECOMMENDATION PAGE ===
# === RECOMMENDATION PAGE ===
def recommend_page():
    sidebar_menu()
    st.title("⭐ Recommended For You")

    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    try:
        res = requests.get(
            f"{BASE_URL}/recommend",
            params={"userid": st.session_state["userid"], "limit": 10},
            headers=headers
        )
        if res.status_code == 200:
            data = res.json()
            st.caption(f"Recommendation method: {data.get('method','-')}")
            movies = data.get("movies", [])
            if not movies:
                st.info("No recommendation for now.")
            else:
                cols_per_row = 5
                for i in range(0, len(movies), cols_per_row):
                    cols = st.columns(cols_per_row, gap="medium")
                    for j, col in enumerate(cols):
                        if i + j < len(movies):
                            m = movies[i+j]
                            movie_id = m.get("movieid")
                            with col:
                                st.markdown("<div style='margin-bottom:35px; padding:8px;'>", unsafe_allow_html=True)
                                if "poster_url" in m and m["poster_url"]:
                                    st.image(m["poster_url"], use_container_width=True)

                                # judul di-truncate (kayak homepage)
                                st.markdown(
                                    f"<div style='text-align:center; font-size:14px; font-weight:bold; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;'>{m.get('title','Untitled')}</div>",
                                    unsafe_allow_html=True
                                )

                                if movie_id:
                                    if st.button("Detail", key=f"rec_detail_{i}_{j}"):
                                        st.session_state["selected_movie"] = movie_id
                                        st.session_state["page"] = "movie_detail"
                                        st.rerun()
                                else:
                                    st.markdown("<div style='color:yellow; text-align:center;'>⚠️ ID unavailable</div>", unsafe_allow_html=True)
                                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error("Failed to get recommendations.")
    except Exception as e:
        st.error(f"Recommendation error: {e}")


# === LIKED MOVIES PAGE ===
def liked_movies_page():
    sidebar_menu()
    st.title("❤️ My Liked Movies")

    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    try:
        res = requests.get(
            f"{BASE_URL}/liked-movies",
            params={"userid": st.session_state["userid"], "limit": 20},
            headers=headers
        )
        if res.status_code == 200:
            data = res.json()
            movies = data.get("movies", [])
            if not movies:
                st.info("You haven't liked any movies yet.")
            else:
                cols_per_row = 5
                for i in range(0, len(movies), cols_per_row):
                    cols = st.columns(cols_per_row, gap="medium")
                    for j, col in enumerate(cols):
                        if i + j < len(movies):
                            m = movies[i+j]
                            movie_id = m.get("movieid")

                            with col:
                                st.markdown("<div style='margin-bottom:35px; padding:8px;'>", unsafe_allow_html=True)

                                if "poster_url" in m and m["poster_url"]:
                                    st.image(m["poster_url"], use_container_width=True)

                                # judul truncated biar rapi
                                st.markdown(
                                    f"<div style='text-align:center; font-size:14px; font-weight:bold; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;'>{m.get('title','Untitled')}</div>",
                                    unsafe_allow_html=True
                                )

                                # tombol detail
                                if movie_id:
                                    if st.button("Detail", key=f"liked_detail_{i}_{j}"):
                                        st.session_state["selected_movie"] = movie_id
                                        st.session_state["page"] = "movie_detail"
                                        st.rerun()
                                else:
                                    st.markdown("<div style='color:yellow; text-align:center;'>⚠️ ID unavailable</div>", unsafe_allow_html=True)

                                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.error("Failed to get liked movies.")
    except Exception as e:
        st.error(f"Error liked movies: {e}")



# === ROUTING ===
if st.session_state["page"] == "login":
    login_page()
elif st.session_state["page"] == "signup":
    signup_page()
elif st.session_state["page"] == "home":
    if st.session_state["token"]:
        home_page()
    else:
        st.session_state["page"] = "login"
elif st.session_state["page"] == "movie_detail":
    movie_detail_page()
elif st.session_state["page"] == "recommend":
    recommend_page()
elif st.session_state["page"] == "liked_movies":
    liked_movies_page()


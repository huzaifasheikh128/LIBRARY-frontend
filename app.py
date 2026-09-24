import streamlit as st
import requests

# --- IMPORTANT: REPLACE THIS URL AFTER DEPLOYING YOUR VERCEL BACKEND ---
API_URL = "https://YOUR-VERCEL-APP-URL.vercel.app" 

st.set_page_config(page_title="Library Management", layout="centered")
st.title("Library Management System")

menu = ["View All Books", "Add a New Book", "Manage Books", "Circulation"]
choice = st.sidebar.selectbox("Navigation", menu)

if choice == "View All Books":
    st.header("Current Inventory")
    search_query = st.text_input("🔍 Search by title or author:", "")
    
    try:
        if search_query:
            response = requests.get(f"{API_URL}/books/search", params={"q": search_query})
        else:
            response = requests.get(f"{API_URL}/books")
            
        if response.status_code == 200:
            books = response.json()
            if books:
                st.dataframe(books, use_container_width=True)
            else:
                if search_query:
                    st.warning(f"No books found matching '{search_query}'.")
                else:
                    st.info("The library database is currently empty.")
        else:
            st.error("Failed to retrieve data. Check if your API_URL is correct.")
    except Exception as e:
        st.error(f"Could not connect to the backend API: {e}")

elif choice == "Add a New Book":
    st.header("Register a New Book")
    with st.form(key="add_book_form"):
        title = st.text_input("Book Title")
        author = st.text_input("Author Name")
        isbn = st.text_input("ISBN (Unique)")
        year = st.number_input("Year Published", min_value=1000, max_value=2026, step=1)
        
        if st.form_submit_button(label="Add Book"):
            if title and author and isbn:
                payload = {"title": title, "author": author, "isbn": isbn, "published_year": year}
                res = requests.post(f"{API_URL}/books", json=payload)
                if res.status_code == 200:
                    st.success(f"Successfully added '{title}'!")
                else:
                    st.error(f"Error: {res.json().get('detail', 'Unknown error')}")
            else:
                st.warning("Please fill in all text fields before submitting.")

elif choice == "Manage Books":
    st.header("Update or Delete a Book")
    response = requests.get(f"{API_URL}/books")
    if response.status_code == 200:
        books = response.json()
        if books:
            book_options = {f"{b['title']} (ID: {b['book_id']})": b for b in books}
            selected_label = st.selectbox("Select a book to manage", list(book_options.keys()))
            selected_book = book_options[selected_label]
            book_id = selected_book['book_id']
            
            tab_update, tab_delete = st.tabs(["Update Details", "Delete Record"])
            
            with tab_update:
                with st.form("update_form"):
                    new_title = st.text_input("Title", value=selected_book['title'])
                    new_author = st.text_input("Author", value=selected_book['author'])
                    new_isbn = st.text_input("ISBN", value=selected_book['isbn'])
                    new_year = st.number_input("Year", value=selected_book['published_year'], min_value=1000)
                    
                    if st.form_submit_button("Update Book"):
                        payload = {"title": new_title, "author": new_author, "isbn": new_isbn, "published_year": new_year}
                        update_res = requests.put(f"{API_URL}/books/{book_id}", json=payload)
                        if update_res.status_code == 200:
                            st.success("Book updated successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to update book.")
            
            with tab_delete:
                st.warning(f"Are you sure you want to permanently delete '{selected_book['title']}'?")
                if st.button("Yes, Delete Book"):
                    del_res = requests.delete(f"{API_URL}/books/{book_id}")
                    if del_res.status_code == 200:
                        st.success("Book deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to delete book.")
        else:
            st.info("No books available to manage.")

elif choice == "Circulation":
    st.header("Circulation Desk")
    response = requests.get(f"{API_URL}/books")
    if response.status_code == 200:
        books = response.json()
        if books:
            tab_checkout, tab_return = st.tabs(["Check Out", "Return"])
            
            with tab_checkout:
                available_books = [b for b in books if b['status'] == 'Available']
                if available_books:
                    options = {f"{b['title']} (ID: {b['book_id']})": b['book_id'] for b in available_books}
                    selected = st.selectbox("Select an available book", list(options.keys()))
                    if st.button("Confirm Check Out"):
                        book_id = options[selected]
                        res = requests.patch(f"{API_URL}/books/{book_id}/checkout")
                        if res.status_code == 200:
                            st.success("Book checked out successfully!")
                            st.rerun()
                        else:
                            st.error(res.json().get('detail', 'Checkout failed'))
                else:
                    st.info("No books are currently available.")

            with tab_return:
                checked_out_books = [b for b in books if b['status'] == 'Checked Out']
                if checked_out_books:
                    options = {f"{b['title']} (ID: {b['book_id']})": b['book_id'] for b in checked_out_books}
                    selected = st.selectbox("Select a book to return", list(options.keys()))
                    if st.button("Confirm Return"):
                        book_id = options[selected]
                        res = requests.patch(f"{API_URL}/books/{book_id}/return")
                        if res.status_code == 200:
                            st.success("Book returned successfully!")
                            st.rerun()
                        else:
                            st.error(res.json().get('detail', 'Return failed'))
                else:
                    st.info("No books are currently checked out.")
        else:
            st.info("The library database is currently empty.")

import streamlit as st
from multiapp import MultiApp
from apps import trends, success_fail # import your app modules here


app = MultiApp()

app.add_app("Trend", trends.app)
app.add_app("Trial Success", success_fail.app)

# The main app
app.run()